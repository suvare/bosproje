import requests
import logging
from datetime import datetime
import time
import random
import hashlib
import feedparser
from config import Config

class NewsHandler:
    def __init__(self):
        self.cryptopanic_api_key = "d3f3eb1a1cf4aa55974aa5b9e318eb56ba622439"
        self.base_url = "https://cryptopanic.com/api/developer/v2"
        self.last_fetch = None
        self.news_cache = []
        self.fallback_count = 0
        self.processed_hashes = set()
        self.last_news_titles = []
    
    def get_news(self):
        """Geliştirilmiş haber sistemi - DÜZGÜN LINKLER"""
        try:
            logging.info("🌐 Gelişmiş haber sistemi aktif...")
            
            # Önbellek kontrolü (30 dakika)
            if self._should_use_cache():
                logging.info("🔄 Önbellekten haberler kullanılıyor...")
                return self.news_cache[:Config.MAX_POSTS_PER_CHECK]
            
            # 1. ÖNCE CRYPTOPANIC API
            news_data = self._try_cryptopanic_api()
            
            # 2. CRYPTOPANIC ÇALIŞMAZSA GELİŞMİŞ RSS
            if not news_data:
                logging.info("🔄 Gelişmiş RSS sistemi deneniyor...")
                news_data = self._try_advanced_rss()
            
            # 3. HABER BULUNDUYSA İŞLE
            if news_data and news_data.get('results'):
                analyzed_news = self._create_smart_analysis(news_data)
                if analyzed_news:
                    unique_news = self._remove_duplicates(analyzed_news)
                    
                    if unique_news:
                        self.news_cache = unique_news
                        self.last_fetch = datetime.now()
                        self.fallback_count = 0
                        logging.info(f"✅ {len(unique_news)} benzersiz haber analiz edildi")
                        return unique_news[:Config.MAX_POSTS_PER_CHECK]
                    else:
                        logging.info("🔄 Tüm haberler işlenmiş, cache kullanılıyor...")
                        return self.news_cache[:Config.MAX_POSTS_PER_CHECK] if self.news_cache else self._get_smart_fallback()
            
            # 4. AKILLI FALLBACK
            return self._get_smart_fallback()
                
        except Exception as e:
            logging.error(f"❌ Sistem hatası: {e}")
            return self._get_smart_fallback()
    
    def _try_cryptopanic_api(self):
        """CryptoPanic API - DÜZGÜN LINK DESTEĞİ"""
        try:
            url = f"{self.base_url}/posts/"
            params = {
                'auth_token': self.cryptopanic_api_key,
                'public': 'true',
                'kind': 'news',
                'currencies': 'BTC,ETH,SOL,DOGE,BNB,ADA,XRP,DOT,AVAX,MATIC,LTC',
                'regions': 'en',
                'page': 1
            }
            
            response = requests.get(url, params=params, timeout=12)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    # LINK KONTROLÜ ve FİLTRELEME
                    valid_results = []
                    for post in results[:8]:
                        url = post.get('url', '')
                        title = post.get('title', '')
                        
                        # GEÇERLİ LİNK KONTROLÜ
                        if self._is_valid_url(url) and title:
                            valid_results.append(post)
                    
                    if valid_results:
                        data['results'] = valid_results
                        logging.info(f"📰 API: {len(valid_results)} geçerli haber alındı")
                        return data
                    else:
                        logging.warning("⚠️ API: Geçerli haber bulunamadı")
                else:
                    logging.warning("⚠️ API: Boş veri döndü")
            else:
                logging.warning(f"⚠️ API Hatası: {response.status_code}")
                
        except Exception as e:
            logging.warning(f"⚠️ API hatası: {e}")
        
        return None
    
    def _try_advanced_rss(self):
        """Gelişmiş RSS Sistemi - DÜZGÜN LINKLER"""
        try:
            # Çoklu RSS kaynağı
            rss_feeds = [
                "https://cryptopanic.com/news/rss/",
                "https://cryptoslate.com/feed/",
                "https://cointelegraph.com/rss"
            ]
            
            all_entries = []
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:5]:
                            # LINK ve TITLE KONTROLÜ
                            if hasattr(entry, 'link') and hasattr(entry, 'title'):
                                if entry.link and entry.title:
                                    # BENZERSİZ HABER KONTROLÜ
                                    if entry.title not in self.last_news_titles:
                                        all_entries.append(entry)
                                        self.last_news_titles.append(entry.title)
                        
                        logging.info(f"📡 {feed_url}: {len(feed.entries)} haber tarandı")
                    time.sleep(1)  # Rate limit
                except Exception as e:
                    logging.warning(f"⚠️ RSS feed hatası {feed_url}: {e}")
                    continue
            
            if all_entries:
                # RSS'yi API formatına dönüştür
                fake_results = []
                for entry in all_entries[:6]:
                    fake_post = {
                        'title': entry.title,
                        'url': entry.link,
                        'source': {'title': self._get_source_from_url(entry.link)},
                        'votes': {'important': 0, 'positive': 0, 'negative': 0},
                        'sentiment': self._detect_sentiment(entry.title),
                        'created_at': datetime.now().isoformat()
                    }
                    fake_results.append(fake_post)
                
                fake_data = {'results': fake_results}
                logging.info(f"📰 RSS: {len(fake_results)} geçerli haber alındı")
                return fake_data
            else:
                logging.warning("⚠️ RSS: Hiç haber bulunamadı")
                
        except Exception as e:
            logging.error(f"❌ RSS sistemi hatası: {e}")
        
        return None
    
    def _is_valid_url(self, url):
        """URL geçerlilik kontrolü"""
        if not url or url == 'https://cryptopanic.com':
            return False
        
        valid_domains = [
            'cryptopanic.com', 'cointelegraph.com', 'decrypt.co', 
            'theblock.co', 'cryptoslate.com', 'newsbtc.com',
            'coin desk.com', 'ambcrypto.com', 'u.today'
        ]
        
        return any(domain in url for domain in valid_domains)
    
    def _get_source_from_url(self, url):
        """URL'den kaynak ismini çıkar"""
        domain_sources = {
            'cryptopanic.com': 'CryptoPanic',
            'cointelegraph.com': 'CoinTelegraph',
            'decrypt.co': 'Decrypt',
            'theblock.co': 'The Block',
            'cryptoslate.com': 'CryptoSlate',
            'newsbtc.com': 'NewsBTC',
            'coindesk.com': 'CoinDesk',
            'ambcrypto.com': 'AMBCrypto',
            'u.today': 'U.Today'
        }
        
        for domain, source in domain_sources.items():
            if domain in url:
                return source
        
        return 'Crypto News'
    
    def _detect_sentiment(self, title):
        """Başlıktan sentiment analizi"""
        title_lower = title.lower()
        
        positive_words = ['bullish', 'surge', 'rally', 'pump', 'growth', 'positive', 'approval', 'adoption']
        negative_words = ['bearish', 'crash', 'drop', 'dump', 'warning', 'negative', 'rejection', 'hack']
        
        positive_count = sum(1 for word in positive_words if word in title_lower)
        negative_count = sum(1 for word in negative_words if word in title_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _remove_duplicates(self, news_list):
        """Tekrar eden haberleri filtrele"""
        unique_news = []
        
        for news in news_list:
            news_hash = self._generate_news_hash(news)
            
            if news_hash not in self.processed_hashes:
                unique_news.append(news)
                self.processed_hashes.add(news_hash)
                
                if len(self.processed_hashes) > 800:
                    self.processed_hashes.clear()
                    logging.info("🧹 Hash cache temizlendi")
        
        logging.info(f"🔄 {len(news_list)} haberden {len(unique_news)} benzersiz")
        return unique_news
    
    def _generate_news_hash(self, news):
        """Haber için benzersiz hash"""
        content = f"{news['title']}_{news['market_analysis'][:80]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _create_smart_analysis(self, api_data):
        """Akıllı analiz sistemi"""
        analyzed_news = []
        
        for post in api_data.get('results', [])[:4]:
            try:
                analysis = self._create_detailed_analysis(post)
                if analysis:
                    analyzed_news.append(analysis)
            except Exception as e:
                logging.warning(f"⚠️ Analiz hatası: {e}")
                continue
        
        return analyzed_news if analyzed_news else [self._create_fallback_post()]
    
    def _create_detailed_analysis(self, post):
        """Detaylı haber analizi"""
        title = post.get('title', 'Crypto Market Update')
        url = post.get('url', 'https://cryptopanic.com')
        source = post.get('source', {}).get('title', 'Crypto News')
        
        # URL'yi kontrol et, geçersizse düzelt
        if not self._is_valid_url(url):
            url = "https://cryptopanic.com/news/"
        
        analysis_data = self._analyze_specific_news(title)
        
        return {
            'title': analysis_data['title'],
            'url': url,
            'source': source,
            'importance': analysis_data['importance'],
            'sentiment': analysis_data['sentiment'],
            'market_analysis': analysis_data['market_analysis'],
            'trading_advice': analysis_data['trading_advice'],
            'market_impact': analysis_data['market_impact'],
            'created_at': datetime.now().strftime("%H:%M"),
            'coin': analysis_data['coin']
        }
    
    def _analyze_specific_news(self, title):
        """Haber başlığına özel analiz"""
        title_lower = title.lower()
        
        # 🐕 DOGECOIN
        if any(word in title_lower for word in ['dogecoin', 'doge']):
            if any(word in title_lower for word in ['price', 'surge', 'pump', 'rally']):
                return {
                    'coin': 'DOGE',
                    'title': '🐕 Dogecoin Price Analysis',
                    'importance': 3,
                    'sentiment': 'positive',
                    'market_analysis': 'DOGE showing momentum with technical indicators suggesting potential upside. Meme coin sector activity increasing.',
                    'trading_advice': 'Consider small position size. Set stop-loss at 5-7% for risk management.',
                    'market_impact': 'MEDIUM'
                }
        
        # ₿ BITCOIN
        elif any(word in title_lower for word in ['bitcoin', 'btc']):
            if any(word in title_lower for word in ['etf', 'institution']):
                return {
                    'coin': 'BTC',
                    'title': '₿ Bitcoin ETF Update',
                    'importance': 4,
                    'sentiment': 'positive',
                    'market_analysis': 'Bitcoin ETF developments influencing institutional flows. Regulatory clarity improving adoption prospects.',
                    'trading_advice': 'Accumulate on market dips. Monitor ETF flow data weekly.',
                    'market_impact': 'HIGH'
                }
            else:
                return {
                    'coin': 'BTC',
                    'title': '₿ Bitcoin Market Intelligence',
                    'importance': 3,
                    'sentiment': 'neutral',
                    'market_analysis': 'BTC testing key technical levels. Market sentiment balanced between institutional accumulation and retail interest.',
                    'trading_advice': 'Set buy orders below current levels. Watch for volume confirmation.',
                    'market_impact': 'HIGH'
                }
        
        # 🔷 ETHEREUM
        elif any(word in title_lower for word in ['ethereum', 'eth']):
            return {
                'coin': 'ETH',
                'title': '🔷 Ethereum Network Update',
                'importance': 3,
                'sentiment': 'neutral',
                'market_analysis': 'Ethereum ecosystem evolving with Layer-2 adoption and protocol upgrades. DeFi activity supporting network value.',
                'trading_advice': 'Accumulate for long-term growth. Monitor gas fee trends.',
                'market_impact': 'HIGH'
            }
        
        # 🟣 SOLANA
        elif any(word in title_lower for word in ['solana', 'sol']):
            return {
                'coin': 'SOL',
                'title': '🟣 Solana Ecosystem',
                'importance': 3,
                'sentiment': 'neutral',
                'market_analysis': 'Solana network performance and ecosystem growth being monitored. Developer activity showing positive trajectory.',
                'trading_advice': 'Trade with careful position sizing. Watch network metrics.',
                'market_impact': 'MEDIUM'
            }
        
        # ⚖️ REGULATION
        elif any(word in title_lower for word in ['regulation', 'sec', 'legal']):
            return {
                'coin': 'GENERAL',
                'title': '⚖️ Regulatory Update',
                'importance': 5,
                'sentiment': 'neutral',
                'market_analysis': 'Regulatory developments impacting crypto market structure. Institutional adoption dependent on regulatory clarity.',
                'trading_advice': 'Stay informed on regulatory news. Diversify across jurisdictions.',
                'market_impact': 'VERY HIGH'
            }
        
        # DEFAULT - Rastgele coin analizi
        coins = [
            ('BTC', '₿ Bitcoin', 'Market consolidation with institutional interest steady.', 'HIGH'),
            ('ETH', '🔷 Ethereum', 'Network upgrades and Layer-2 adoption progressing.', 'HIGH'),
            ('SOL', '🟣 Solana', 'Ecosystem growth and developer activity monitored.', 'MEDIUM'),
            ('BNB', '💠 BNB Chain', 'Exchange token performance correlating with platform growth.', 'MEDIUM'),
            ('ADA', '🌐 Cardano', 'Development activity and ecosystem expansion ongoing.', 'MEDIUM')
        ]
        coin, coin_name, analysis, impact = random.choice(coins)
        
        return {
            'coin': coin,
            'title': f'{coin_name} Market Analysis',
            'importance': 3,
            'sentiment': 'neutral',
            'market_analysis': analysis,
            'trading_advice': 'Monitor key technical levels for entry opportunities.',
            'market_impact': impact
        }
    
    def _should_use_cache(self):
        """Önbellek kontrolü"""
        if not self.last_fetch or not self.news_cache:
            return False
        
        time_diff = (datetime.now() - self.last_fetch).total_seconds()
        return time_diff < 1800  # 30 dakika
    
    def _get_smart_fallback(self):
        """Akıllı fallback"""
        self.fallback_count += 1
        
        if self.fallback_count <= 2:
            logging.info("🔄 Yedek içerik kullanılıyor...")
            return self._get_fallback_content()
        else:
            logging.info("⏸️ Fallback limiti, cache kullanılıyor...")
            return self.news_cache[:Config.MAX_POSTS_PER_CHECK] if self.news_cache else self._get_fallback_content()
    
    def _get_fallback_content(self):
        """Kaliteli yedek içerik"""
        return [self._create_fallback_post()]
    
    def _create_fallback_post(self):
        """Profesyonel yedek analiz"""
        templates = [
            {
                'coin': 'BTC',
                'title': '₿ Bitcoin Market Intelligence',
                'url': 'https://cryptopanic.com/news/',
                'source': 'Quantum Analytics',
                'importance': 3,
                'sentiment': 'neutral',
                'market_analysis': 'Bitcoin market analysis in progress. Technical levels and institutional flows being monitored for trading signals.',
                'trading_advice': 'Monitor key support levels. Consider DCA strategy during volatility.',
                'market_impact': 'HIGH',
                'created_at': datetime.now().strftime("%H:%M")
            },
            {
                'coin': 'ETH',
                'title': '🔷 Ethereum Network Update', 
                'url': 'https://cryptopanic.com/news/',
                'source': 'Market Intelligence',
                'importance': 3,
                'sentiment': 'neutral',
                'market_analysis': 'Ethereum ecosystem developments and network upgrades being analyzed. DeFi and NFT sectors showing dynamic activity.',
                'trading_advice': 'Watch for Layer-2 adoption metrics and gas fee trends.',
                'market_impact': 'HIGH',
                'created_at': datetime.now().strftime("%H:%M")
            }
        ]
        
        return random.choice(templates)
    
    def format_news_message(self, news):
        """Profesyonel Telegram formatı"""
        try:
            sentiment_emojis = {
                'positive': '🟢 BULLISH',
                'negative': '🔴 BEARISH', 
                'neutral': '🟡 NEUTRAL'
            }
            
            importance_emojis = {
                1: '🔸', 2: '🟡', 3: '📊', 4: '🚀', 5: '⚡'
            }
            
            coin_emojis = {
                'BTC': '₿', 'ETH': '🔷', 'SOL': '🟣', 'DOGE': '🐕', 
                'BNB': '💠', 'ADA': '🌐', 'XRP': '✨', 'DOT': '🔵',
                'AVAX': '❄️', 'MATIC': '🟪', 'LTC': '⚡', 'GENERAL': '📊'
            }
            
            sentiment_emoji = sentiment_emojis.get(news.get('sentiment', 'neutral'), '🟡')
            importance_emoji = importance_emojis.get(news.get('importance', 3), '📊')
            coin_emoji = coin_emojis.get(news.get('coin', 'GENERAL'), '📊')
            
            impact = news.get('market_impact', 'MEDIUM')
            impact_emoji = '📊'
            if 'HIGH' in impact:
                impact_emoji = '⚡'
            elif 'VERY HIGH' in impact:
                impact_emoji = '🚨'

            return f"""**{importance_emoji} {coin_emoji} {news['title']}**

**{sentiment_emoji} Market Analysis:**
{news['market_analysis']}

**💡 Trading Advice:**
{news['trading_advice']}

**{impact_emoji} Market Impact:** `{news['market_impact']}`
**📊 Importance:** `{news['importance']}/5`
**🎯 Sentiment:** `{news['sentiment'].upper()}`
**💰 Coin:** `{news.get('coin', 'MARKET')}`

**🔗 Source:** `{news['source']}`
**⏰ Time:** `{news['created_at']}`

[📖 Read Full Story]({news['url']})

#CryptoAnalysis #{news['source'].replace(' ', '')} #{news.get('coin', 'GENERAL')}"""
            
        except Exception as e:
            logging.error(f"❌ Format error: {e}")
            return f"**📊 Crypto Market Intelligence**\n\nProfessional analysis being prepared...\n\n[📖 Read More]({news.get('url', 'https://cryptopanic.com/news/')})"