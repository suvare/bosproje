import requests
import logging
from datetime import datetime
from config import Config
import time
import hashlib

class NewsHandler:
    def __init__(self):
        self.processed_hashes = set()  # Tekrar önleme için hash'ler
        self.news_cache = []  # Önbellek
        self.cache_time = None  # Önbellek zamanı
    
    def get_news(self):
        """Profesyonel İngilizce analiz içerikleri"""
        try:
            # Önbellek kontrolü (10 dakika)
            if self.news_cache and self.cache_time and (time.time() - self.cache_time) < 600:
                logging.info("🔄 Önbellekten haberler alınıyor...")
                return self._get_unique_news(self.news_cache)
            
            logging.info("🌐 Profesyonel kripto analizleri alınıyor...")
            
            # Çoklu haber kaynakları
            all_news = []
            all_news.extend(self._get_coingecko_news())
            all_news.extend(self._get_cryptopanic_news())
            all_news.extend(self._get_professional_analysis())
            
            # Önbelleği güncelle
            self.news_cache = all_news
            self.cache_time = time.time()
            
            unique_news = self._get_unique_news(all_news)
            logging.info(f"✅ {len(unique_news)} benzersiz analiz hazır")
            return unique_news[:Config.MAX_POSTS_PER_CHECK]
            
        except Exception as e:
            logging.error(f"❌ Haber işleme hatası: {e}")
            return self._get_fallback_analysis()
    
    def _get_coingecko_news(self):
        """CoinGecko haberleri + profesyonel analiz"""
        try:
            url = "https://api.coingecko.com/api/v3/news"
            params = {'page': 1, 'per_page': 10}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                analyzed_news = []
                if isinstance(data, list):
                    for news in data[:5]:
                        analyzed = self._analyze_news(news)
                        if analyzed:
                            analyzed_news.append(analyzed)
                
                return analyzed_news
            return []
        except:
            return []
    
    def _get_cryptopanic_news(self):
        """CryptoPanic haber beslemesi"""
        try:
            # CryptoPanic RSS yedek kaynak olarak
            url = "https://cryptopanic.com/news/rss/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return self._parse_rss_news(response.text)
            return []
        except:
            return []
    
    def _analyze_news(self, news):
        """Haberleri profesyonel analize dönüştür"""
        title = news.get('title', '')
        url = news.get('url', '')
        
        if not title or not url:
            return None
        
        analysis = self._generate_professional_analysis(title)
        
        return {
            'title': analysis['title'],
            'url': url,
            'analysis': analysis['analysis'],
            'importance': analysis['importance'],
            'source': self._clean_source_name(news.get('source', {})),
            'created_at': datetime.now().strftime("%H:%M"),
            'trading_advice': analysis['trading_advice'],
            'market_impact': analysis['market_impact']
        }
    
    def _generate_professional_analysis(self, title):
        """Profesyonel kripto analizi oluştur"""
        title_lower = title.lower()
        
        # Profesyonel analiz şablonları (İNGİLİZCE)
        if any(word in title_lower for word in ['bitcoin', 'btc', 'xbt']):
            return {
                'title': '₿ Bitcoin Market Analysis',
                'analysis': 'Bitcoin shows strong institutional interest with ETF approvals pending. Technical indicators suggest key support levels are being tested. Market sentiment remains cautiously optimistic.',
                'importance': 4,
                'trading_advice': 'Consider dollar-cost averaging at current levels. Watch for breakout above resistance.',
                'market_impact': 'HIGH - Affects entire crypto market'
            }
        elif any(word in title_lower for word in ['ethereum', 'eth']):
            return {
                'title': '🔷 Ethereum Network Update',
                'analysis': 'Ethereum continues ecosystem growth with Layer 2 adoption increasing. Gas fees optimization and upcoming upgrades maintain positive momentum. DeFi TVL shows steady growth.',
                'importance': 3,
                'trading_advice': 'Accumulate on dips. Monitor ETH/BTC ratio for strength signals.',
                'market_impact': 'MEDIUM - Key for DeFi and NFT sectors'
            }
        elif any(word in title_lower for word in ['sec', 'etf', 'regulation']):
            return {
                'title': '⚖️ Regulatory Developments',
                'analysis': 'Regulatory clarity continues to evolve with major jurisdictions defining frameworks. Institutional adoption hinges on clear regulations. Compliance becomes competitive advantage.',
                'importance': 5,
                'trading_advice': 'Monitor regulatory news closely. Consider regulated investment vehicles.',
                'market_impact': 'VERY HIGH - Market-wide implications'
            }
        elif any(word in title_lower for word in ['defi', 'decentralized finance']):
            return {
                'title': '🔄 DeFi Ecosystem Analysis',
                'analysis': 'DeFi protocols show innovation in yield strategies and cross-chain interoperability. Security remains paramount with increasing TVL. Real-world asset tokenization gains traction.',
                'importance': 3,
                'trading_advice': 'Diversify across established protocols. Monitor governance token developments.',
                'market_impact': 'MEDIUM - Sector-specific impact'
            }
        elif any(word in title_lower for word in ['nft', 'metaverse']):
            return {
                'title': '🖼️ Digital Assets & Metaverse',
                'analysis': 'NFT market matures with focus on utility and intellectual property. Metaverse projects demonstrate real-world use cases. Gaming and entertainment sectors drive adoption.',
                'importance': 2,
                'trading_advice': 'Focus on projects with strong communities and utility.',
                'market_impact': 'LOW - Niche market impact'
            }
        else:
            return {
                'title': '💎 Crypto Market Intelligence',
                'analysis': 'Market shows consolidation after recent volatility. Macroeconomic factors continue to influence crypto valuations. Institutional participation increases market maturity.',
                'importance': 2,
                'trading_advice': 'Maintain balanced portfolio. Stay updated on macro developments.',
                'market_impact': 'MEDIUM - General market sentiment'
            }
    
    def _get_professional_analysis(self):
        """Küratörlü profesyonel analizler"""
        return [
            {
                'title': '📊 Daily Market Intelligence',
                'url': 'https://coinmarketcap.com/',
                'analysis': 'Market structure shows accumulation patterns in major cryptocurrencies. Derivatives data indicates balanced positioning. Funding rates remain neutral across exchanges.',
                'importance': 3,
                'source': 'Quantum Analytics',
                'created_at': datetime.now().strftime("%H:%M"),
                'trading_advice': 'Set limit orders at key support levels. Monitor volume for breakout confirmation.',
                'market_impact': 'MEDIUM - Technical analysis focus'
            }
        ]
    
    def _get_fallback_analysis(self):
        """Yedek profesyonel içerik"""
        return [
            {
                'title': '🔍 Quantum Crypto Intel - Live Analysis',
                'url': 'https://t.me/quantumcryptointel',
                'analysis': 'Professional crypto market analysis and intelligence. Real-time insights and trading signals.',
                'importance': 2,
                'source': 'Quantum System',
                'created_at': datetime.now().strftime("%H:%M"),
                'trading_advice': 'Stay tuned for live market updates and analysis.',
                'market_impact': 'LOW - System update'
            }
        ]
    
    def _get_unique_news(self, news_list):
        """İçerik hash'leme ile tekrarları kaldır"""
        unique_news = []
        
        for news in news_list:
            content_hash = self._generate_content_hash(news['title'] + news['analysis'])
            
            if content_hash not in self.processed_hashes:
                unique_news.append(news)
                self.processed_hashes.add(content_hash)
                
                # Hash depolama limiti (bellek sorunlarını önle)
                if len(self.processed_hashes) > 1000:
                    self.processed_hashes.clear()
        
        return unique_news
    
    def _generate_content_hash(self, content):
        """İçerik tekilleştirme için hash oluştur"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _clean_source_name(self, source):
        """Kaynak ismini temizle"""
        if isinstance(source, dict):
            source_name = source.get('title', 'CoinGecko')
        else:
            source_name = str(source)
        
        source_name = source_name.replace('News', '').replace('Media', '').strip()
        return source_name[:15] if source_name else 'MarketSource'
    
    def _parse_rss_news(self, rss_content):
        """Basit RSS parsing (yer tutucu)"""
        # Bu kısım proper RSS parsing ile genişletilebilir
        return []
    
    def format_news_message(self, news):
        """Profesyonel İngilizce analiz formatı"""
        importance_emoji = {1: '🔸', 2: '🔹', 3: '📊', 4: '🚀', 5: '⚡'}
        emoji = importance_emoji.get(news['importance'], '💎')
        
        return f"""**{emoji} {news['title']}**

📈 **Market Analysis:**
{news['analysis']}

💡 **Trading Advice:** {news['trading_advice']}

⚡ **Market Impact:** `{news['market_impact']}`
🔗 **Source:** `{news['source']}`
⏰ **Time:** `{news['created_at']}`

[📖 Read Full Analysis]({news['url']})

#CryptoAnalysis #TradingSignals #{news['source'].replace(' ', '')}"""