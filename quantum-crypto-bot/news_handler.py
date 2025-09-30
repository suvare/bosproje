import requests
import logging
from datetime import datetime
import time
import re
import random
from config import Config

class NewsHandler:
    def __init__(self):
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.binance_url = "https://api.binance.com/api/v3"
        self.last_market_update = None
        self.market_cache = {}
        self.request_count = 0
        self.last_request_time = time.time()
    
    def get_news(self):
        """Rate limit korumalı analiz sistemi"""
        try:
            logging.info("🌐 Preparing real-time analysis...")
            
            # Rate limit kontrolü
            self._rate_limit_delay()
            
            # 1. Önce haberleri al
            news = self._get_news_safe()
            
            # 2. Canlı piyasa verilerini al (cache'li)
            market_data = self._get_cached_market_data_safe()
            
            # 3. Analiz oluştur
            analyzed_news = []
            for item in news[:Config.MAX_POSTS_PER_CHECK]:
                analysis = self._create_smart_analysis(item, market_data)
                if analysis:
                    analyzed_news.append(analysis)
            
            if analyzed_news:
                logging.info(f"✅ {len(analyzed_news)} analysis ready")
                return analyzed_news
            else:
                return self._get_fallback_analysis()
            
        except Exception as e:
            logging.error(f"❌ Analysis error: {e}")
            return self._get_fallback_analysis()
    
    def _rate_limit_delay(self):
        """Rate limit koruması"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # 10 saniyede 1'den fazla istek yapma
        if time_since_last < 10:
            sleep_time = 10 - time_since_last
            logging.info(f"⏳ Rate limit protection: Waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Her 10 istekte 30 saniye bekle
        if self.request_count % 10 == 0:
            logging.info("🔄 Rate limit: Waiting 30s after 10 requests")
            time.sleep(30)
    
    def _get_cached_market_data_safe(self):
        """Rate limit korumalı piyasa verisi"""
        current_time = time.time()
        
        # Cache kontrol (10 dakika)
        if (self.last_market_update and 
            current_time - self.last_market_update < 600 and 
            self.market_cache):
            logging.info("🔄 Using cached market data")
            return self.market_cache
        
        try:
            logging.info("📊 Fetching new market data...")
            market_data = {}
            
            # Rate limit delay
            time.sleep(2)
            
            # Binance API - Rate limit yok
            btc_price = self._get_binance_price('BTCUSDT')
            eth_price = self._get_binance_price('ETHUSDT')
            sol_price = self._get_binance_price('SOLUSDT')
            
            if btc_price:
                market_data['bitcoin'] = {
                    'current_price': btc_price['price'],
                    'price_change_percentage_24h': btc_price['price_change_percent'],
                    'volume_24h': btc_price['volume']
                }
                logging.info(f"✅ BTC: ${btc_price['price']:,.2f}")
            
            if eth_price:
                market_data['ethereum'] = {
                    'current_price': eth_price['price'],
                    'price_change_percentage_24h': eth_price['price_change_percent'],
                    'volume_24h': eth_price['volume']
                }
                logging.info(f"✅ ETH: ${eth_price['price']:,.2f}")
            
            if sol_price:
                market_data['solana'] = {
                    'current_price': sol_price['price'],
                    'price_change_percentage_24h': sol_price['price_change_percent'],
                    'volume_24h': sol_price['volume']
                }
                logging.info(f"✅ SOL: ${sol_price['price']:,.2f}")
            
            # CoinGecko'yu sadece gerekirse kullan
            if not market_data:
                market_data = self._get_coingecko_data_safe()
            
            # Cache'i güncelle
            self.market_cache = market_data
            self.last_market_update = current_time
            
            return market_data
            
        except Exception as e:
            logging.error(f"❌ Market data error: {e}")
            return self.market_cache
    
    def _get_binance_price(self, symbol):
        """Binance API - Rate limit yok"""
        try:
            url = f"{self.binance_url}/ticker/24hr?symbol={symbol}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'price': float(data['lastPrice']),
                    'price_change_percent': float(data['priceChangePercent']),
                    'volume': float(data['volume'])
                }
            return None
            
        except Exception as e:
            logging.warning(f"⚠️ Binance data failed: {e}")
            return None
    
    def _get_coingecko_data_safe(self):
        """CoinGecko - Rate limit korumalı"""
        try:
            time.sleep(5)  # Extra delay for CoinGecko
            
            market_data = {}
            coins = ['bitcoin', 'ethereum', 'solana']
            
            for coin_id in coins:
                try:
                    url = f"{self.coingecko_url}/coins/{coin_id}"
                    params = {'localization': 'false', 'market_data': 'true'}
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        market_data[coin_id] = self._parse_coin_data(data)
                        logging.info(f"✅ {coin_id.upper()}: ${market_data[coin_id]['current_price']:,.2f}")
                    else:
                        logging.warning(f"⚠️ CoinGecko {coin_id} error: {response.status_code}")
                    
                    time.sleep(3)  # Her coin arasında bekle
                    
                except Exception as e:
                    logging.warning(f"⚠️ {coin_id} data failed: {e}")
                    continue
            
            return market_data
            
        except Exception as e:
            logging.error(f"❌ CoinGecko overall error: {e}")
            return {}
    
    def _parse_coin_data(self, data):
        """Coin verisini işle"""
        market_data = data.get('market_data', {})
        
        return {
            'current_price': market_data.get('current_price', {}).get('usd', 0),
            'price_change_percentage_24h': market_data.get('price_change_percentage_24h', 0),
            'volume_24h': market_data.get('total_volume', {}).get('usd', 0)
        }
    
    def _get_news_safe(self):
        """Rate limit korumalı haber alma"""
        try:
            # Önce CryptoPanic (rate limit yok)
            news = self._get_cryptopanic_news()
            if news:
                return news
            
            # CryptoPanic çalışmazsa CoinGecko'yu dene
            logging.warning("⚠️ CryptoPanic failed, trying CoinGecko...")
            return self._get_coingecko_news_safe()
            
        except Exception as e:
            logging.error(f"❌ News error: {e}")
            return self._get_sample_news()
    
    def _get_cryptopanic_news(self):
        """CryptoPanic RSS - Rate limit yok"""
        try:
            url = "https://cryptopanic.com/news/rss/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                news_list = []
                
                # RSS parsing
                titles = re.findall(r'<title>(.*?)</title>', response.text)
                links = re.findall(r'<link>(.*?)</link>', response.text)
                
                for i in range(min(15, len(titles))):
                    if (titles[i] and links[i] and 
                        'CryptoPanic' not in titles[i] and
                        len(titles[i]) > 20):
                        news_list.append({
                            'title': titles[i],
                            'url': links[i],
                            'source': 'CryptoPanic'
                        })
                
                if news_list:
                    logging.info(f"📰 {len(news_list)} news from CryptoPanic")
                    return news_list
                    
            return []
            
        except Exception as e:
            logging.warning(f"⚠️ CryptoPanic error: {e}")
            return []
    
    def _get_coingecko_news_safe(self):
        """CoinGecko haber - Rate limit korumalı"""
        try:
            time.sleep(5)
            
            url = f"{self.coingecko_url}/news"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                news_list = []
                
                if isinstance(data, list):
                    for item in data[:8]:
                        title = item.get('title') or item.get('name')
                        url = item.get('url') or item.get('link')
                        
                        if title and url:
                            news_list.append({
                                'title': title,
                                'url': url,
                                'source': 'CoinGecko'
                            })
                
                if news_list:
                    logging.info(f"📰 {len(news_list)} news from CoinGecko")
                    return news_list
            
            return []
                
        except Exception as e:
            logging.warning(f"⚠️ CoinGecko news error: {e}")
            return []
    
    def _get_sample_news(self):
        """Örnek haberler - Fallback"""
        sample_news = [
            {
                'title': 'Crypto Market Analysis - Live Price Updates',
                'url': 'https://cryptopanic.com',
                'source': 'Market Intelligence'
            },
            {
                'title': 'Bitcoin & Ethereum Technical Analysis - Current Trends', 
                'url': 'https://cryptopanic.com',
                'source': 'Technical Analysis'
            },
            {
                'title': 'Blockchain Innovation & Market Developments Overview',
                'url': 'https://cryptopanic.com',
                'source': 'Industry News'
            }
        ]
        logging.info(f"🔧 {len(sample_news)} sample news created")
        return sample_news
    
    def _create_smart_analysis(self, news_item, market_data):
        """Akıllı analiz oluştur"""
        try:
            title = news_item.get('title', '')
            
            # Piyasa durumunu analiz et
            market_analysis = self._analyze_market_condition(market_data)
            
            # Habere göre özel analiz
            news_analysis = self._analyze_news_sentiment(title)
            
            # Trading sinyali oluştur
            trading_signal = self._generate_trading_signal(market_data, news_analysis)
            
            # Özet piyasa verisi
            summary_data = self._summarize_market_data(market_data)
            
            return {
                'title': f"📊 {title}",
                'url': news_item.get('url', ''),
                'source': news_item.get('source', 'CryptoPanic'),
                'market_analysis': market_analysis,
                'news_analysis': news_analysis,
                'trading_signal': trading_signal,
                'market_data': summary_data,
                'timestamp': datetime.now().strftime("%H:%M"),
                'importance': 3  # Sabit importance - filtre sorununu çözmek için
            }
            
        except Exception as e:
            logging.error(f"❌ Analysis creation error: {e}")
            return None
    
    def _analyze_market_condition(self, market_data):
        """Piyasa durumunu analiz et"""
        btc_data = market_data.get('bitcoin', {})
        
        if not btc_data:
            return "⏳ Market data updating..."
        
        price_change = btc_data.get('price_change_percentage_24h', 0)
        
        # Fiyat değişim analizi
        if price_change > 5:
            return "🚀 STRONG UPTREND - Bullish momentum"
        elif price_change > 2:
            return "📈 MODERATE UPTREND - Positive trend"
        elif price_change < -5:
            return "🔻 STRONG DOWNTREND - Bearish pressure" 
        elif price_change < -2:
            return "📉 MODERATE DOWNTREND - Caution advised"
        else:
            return "➡️ SIDEWAYS - Market consolidation"
    
    def _analyze_news_sentiment(self, title):
        """Haber sentiment analizi"""
        title_lower = title.lower()
        
        positive_keywords = ['approval', 'approved', 'bullish', 'rally', 'surge', 'growth', 
                           'adoption', 'institutional', 'positive', 'breakout', 'success',
                           'green', 'profit', 'gain', 'win', 'approve', 'partnership']
        negative_keywords = ['rejection', 'rejected', 'bearish', 'crash', 'drop', 'decline', 
                           'warning', 'regulation', 'ban', 'negative', 'selloff', 'fear',
                           'red', 'loss', 'fail', 'reject', 'warning', 'hack']
        
        positive_count = sum(1 for word in positive_keywords if word in title_lower)
        negative_count = sum(1 for word in negative_keywords if word in title_lower)
        
        if positive_count > negative_count:
            return f"📈 POSITIVE ({positive_count}/{negative_count}) - Positive catalyst"
        elif negative_count > positive_count:
            return f"📉 NEGATIVE ({negative_count}/{positive_count}) - Negative impact"
        else:
            return "➡️ NEUTRAL - Market technicals important"
    
    def _generate_trading_signal(self, market_data, news_analysis):
        """Trading sinyali oluştur"""
        btc_data = market_data.get('bitcoin', {})
        
        if not btc_data:
            return "⏳ Waiting for data..."
        
        price_change = btc_data.get('price_change_percentage_24h', 0)
        
        # Kombinasyon analizi
        if price_change > 3 and "POSITIVE" in news_analysis:
            return "🟢 STRONG BUY - Bullish momentum + positive news"
        elif price_change > 1 and "POSITIVE" in news_analysis:
            return "🟡 BUY - Positive trend"
        elif price_change < -3 and "NEGATIVE" in news_analysis:
            return "🔴 STRONG SELL - Bearish pressure + negative news"
        elif price_change < -1 and "NEGATIVE" in news_analysis:
            return "🟡 SELL - Caution advised"
        elif -1 <= price_change <= 1:
            return "⚪ NEUTRAL - Wait for confirmation"
        else:
            return "🔷 MIXED - Analyze carefully"
    
    def _summarize_market_data(self, market_data):
        """Piyasa verisini özetle"""
        summary = {}
        
        if 'bitcoin' in market_data:
            btc = market_data['bitcoin']
            summary['btc_price'] = f"${btc.get('current_price', 0):,.2f}"
            summary['btc_change'] = f"{btc.get('price_change_percentage_24h', 0):+.2f}%"
        
        if 'ethereum' in market_data:
            eth = market_data['ethereum']
            summary['eth_price'] = f"${eth.get('current_price', 0):,.2f}"
            summary['eth_change'] = f"{eth.get('price_change_percentage_24h', 0):+.2f}%"
        
        if 'solana' in market_data:
            sol = market_data['solana']
            summary['sol_price'] = f"${sol.get('current_price', 0):,.2f}"
            summary['sol_change'] = f"{sol.get('price_change_percentage_24h', 0):+.2f}%"
        
        return summary if summary else {'status': 'Updating...'}
    
    def _get_fallback_analysis(self):
        """Yedek analiz"""
        return [{
            'title': '🔍 Quantum Crypto Intel - Market Analysis',
            'url': 'https://t.me/quantumcryptointel',
            'source': 'Quantum Analytics',
            'market_analysis': '📊 Processing market data...',
            'news_analysis': '📰 Preparing real-time analysis',
            'trading_signal': '💡 System updating...',
            'market_data': {'status': 'Live data loading...'},
            'timestamp': datetime.now().strftime("%H:%M"),
            'importance': 3
        }]
    
    def format_news_message(self, analysis):
        """Analizi formatla"""
        market_data_text = ""
        if 'btc_price' in analysis['market_data']:
            market_data_text += f"• BTC: {analysis['market_data']['btc_price']} ({analysis['market_data']['btc_change']})\n"
        if 'eth_price' in analysis['market_data']:
            market_data_text += f"• ETH: {analysis['market_data']['eth_price']} ({analysis['market_data']['eth_change']})\n"
        if 'sol_price' in analysis['market_data']:
            market_data_text += f"• SOL: {analysis['market_data']['sol_price']} ({analysis['market_data']['sol_change']})\n"
        
        if not market_data_text:
            market_data_text = "• 📈 Data updating...\n"
        
        return f"""**{analysis['title']}**

📈 **Market Analysis:**
{analysis['market_analysis']}

📰 **News Impact:**
{analysis['news_analysis']}

💡 **Trading Signal:**
{analysis['trading_signal']}

💰 **Live Prices:**
{market_data_text.rstrip()}

⏰ **Time:** {analysis['timestamp']}
🔗 **Source:** {analysis['source']}

[📖 Read More]({analysis['url']})

#CryptoAnalysis #LiveData #{analysis['source'].replace(' ', '')}"""