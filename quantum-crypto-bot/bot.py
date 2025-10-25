import telebot
import schedule
import time
import logging
from threading import Thread
from datetime import datetime
# bot.py'ye bu import'u ekleyin
from analytics import Analytics
# Yeni import'lar
from twitter_handler import TwitterHandler
from instagram_handler import InstagramHandler

class QuantumCryptoBot:
    def __init__(self):
        self.running = True
        self.news_count = 0
        self.error_count = 0
        self.analytics = Analytics()
        self.twitter = TwitterHandler()  # ✅ Twitter entegrasyonu
        self.instagram = InstagramHandler()  # ✅ Instagram entegrasyonu
    
    def cross_platform_share(self, analysis):
        """Çoklu platforma paylaşım"""
        try:
            # Twitter'a paylaş
            twitter_success = self.twitter.post_tweet(analysis)
            
            # Instagram'a paylaş (görsel)
            instagram_success = self.instagram.post_to_instagram(analysis)
            
            logging.info(f"🌐 Cross-platform: Twitter:{twitter_success} Instagram:{instagram_success}")
            
        except Exception as e:
            logging.error(f"❌ Cross-platform paylaşım hatası: {e}")
    
    def send_to_channel(self, message, news_data=None):
        """Ana paylaşım fonksiyonu - Cross-platform"""
        try:
            # Telegram'a gönder
            sent_message = bot.send_message(Config.CHANNEL_ID, message, parse_mode='Markdown')
            
            # Analytics'e kaydet
            if news_data and hasattr(sent_message, 'message_id'):
                message_log = {
                    'message_id': sent_message.message_id,
                    'coin': news_data.get('coin', 'GENERAL'),
                    'sentiment': news_data.get('sentiment', 'neutral'),
                    'importance': news_data.get('importance', 3),
                    'source': news_data.get('source', 'Unknown')
                }
                self.analytics.log_message(message_log)
            
            # Cross-platform paylaşım
            self.cross_platform_share(news_data)
            
            self.news_count += 1
            logging.info(f"✅ #{self.news_count} analiz TÜM platformlara gönderildi")
            return True
            
        except Exception as e:
            self.error_count += 1
            logging.error(f"❌ Mesaj gönderme hatası: {e}")
            return False

class QuantumCryptoBot:
    def __init__(self):
        self.running = True
        self.news_count = 0
        self.error_count = 0
        self.analytics = Analytics()  # ✅ Analytics ekle
    
    def send_to_channel(self, message, news_data=None):
        """Kanal'a mesaj gönder ve analytics kaydet"""
        try:
            # Mesajı gönder
            sent_message = bot.send_message(Config.CHANNEL_ID, message, parse_mode='Markdown')
            
            # Analytics'e kaydet
            if news_data and hasattr(sent_message, 'message_id'):
                message_log = {
                    'message_id': sent_message.message_id,
                    'coin': news_data.get('coin', 'GENERAL'),
                    'sentiment': news_data.get('sentiment', 'neutral'),
                    'importance': news_data.get('importance', 3),
                    'source': news_data.get('source', 'Unknown')
                }
                self.analytics.log_message(message_log)
            
            self.news_count += 1
            logging.info(f"✅ #{self.news_count} analiz gönderildi ve kaydedildi")
            return True
            
        except Exception as e:
            self.error_count += 1
            logging.error(f"❌ Mesaj gönderme hatası: {e}")
            return False
    
    def check_and_post_news(self):
        """Analizleri kontrol et ve paylaş - Analytics ile"""
        try:
            logging.info("🔍 Analizler kontrol ediliyor...")
            
            news_list = news_handler.get_news()
            
            if not news_list:
                logging.info("ℹ️ Analiz bulunamadı")
                return
            
            logging.info(f"✅ {len(news_list)} analiz bulundu")
            
            # İlk analizi paylaş
            news_item = news_list[0]
            message = news_handler.format_news_message(news_item)
            
            if self.send_to_channel(message, news_item):
                logging.info("📊 Analiz başarıyla paylaşıldı ve analytics'e kaydedildi")
        
        except Exception as e:
            logging.error(f"❌ Analiz kontrol hatası: {e}")
    
    def send_daily_report(self):
        """Günlük analytics raporu gönder"""
        try:
            metrics = self.analytics.get_performance_metrics()
            daily_summary = self.analytics.get_daily_summary(1)
            
            if daily_summary:
                today = daily_summary[0]
                report = f"""**📊 Günlük Analytics Raporu**

📈 **Bugünkü Performans:**
• Toplam Mesaj: {today['message_count']}
• Toplam Görüntülenme: {today['total_views']}
• Ortalama Görüntülenme: {today['avg_views']:.1f}
• En Popüler Coin: {today['top_coin']}
• Hakim Sentiment: {today['top_sentiment']}

🏆 **Genel İstatistikler:**
• Toplam Mesaj: {metrics['total_messages']}
• Toplam Görüntülenme: {metrics['total_views']}
• Ortalama Engagement: {metrics['avg_engagement']}
• Başarı Oranı: {metrics['success_rate']}%

#Analytics #Report #{datetime.now().strftime('%d%m%Y')}"""
                
                bot.send_message(Config.CHANNEL_ID, report, parse_mode='Markdown')
                logging.info("📊 Günlük rapor gönderildi")
                
        except Exception as e:
            logging.error(f"❌ Rapor gönderme hatası: {e}")
    
    def start_scheduler(self):
        """Zamanlayıcıyı başlat - Analytics raporu ile"""
        schedule.every(Config.CHECK_INTERVAL).seconds.do(self.check_and_post_news)
        
        # Günlük analytics raporu (Saat 20:00'da)
        schedule.every().day.at("20:00").do(self.send_daily_report)
        
        logging.info(f"⏰ Zamanlayıcı başlatıldı: {Config.CHECK_INTERVAL}s aralık + Günlük rapor")
        
        # İlk kontrolü hemen yap
        self.check_and_post_news()
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)

# Logging ayarı
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from config import Config

print("🔧 Config doğrulanıyor...")
if not Config.validate():
    print("❌ Config doğrulama başarısız. Bot durduruluyor.")
    exit(1)

from news_handler import NewsHandler

# Bot'u oluştur
bot = telebot.TeleBot(Config.BOT_TOKEN)
news_handler = NewsHandler()

class QuantumCryptoBot:
    def __init__(self):
        self.running = True
        self.news_count = 0
        self.error_count = 0
    
    def send_to_channel(self, message):
        """Kanal'a mesaj gönder"""
        try:
            bot.send_message(Config.CHANNEL_ID, message, parse_mode='Markdown')
            self.news_count += 1
            logging.info(f"✅ #{self.news_count} analiz gönderildi")
            return True
        except Exception as e:
            self.error_count += 1
            logging.error(f"❌ Mesaj gönderme hatası: {e}")
            return False
    
    def check_and_post_news(self):
        """Analizleri kontrol et ve paylaş"""
        try:
            logging.info("🔍 Analizler kontrol ediliyor...")
            
            news_list = news_handler.get_news()
            
            if not news_list:
                logging.info("ℹ️ Analiz bulunamadı")
                return
            
            logging.info(f"✅ {len(news_list)} analiz bulundu")
            
            # İlk analizi paylaş
            message = news_handler.format_news_message(news_list[0])
            if self.send_to_channel(message):
                logging.info("📊 Analiz başarıyla paylaşıldı")
        
        except Exception as e:
            logging.error(f"❌ Analiz kontrol hatası: {e}")
    
    def start_scheduler(self):
        """Zamanlayıcıyı başlat"""
        schedule.every(Config.CHECK_INTERVAL).seconds.do(self.check_and_post_news)
        
        logging.info(f"⏰ Zamanlayıcı başlatıldı: {Config.CHECK_INTERVAL}s aralık")
        
        # İlk kontrolü hemen yap
        self.check_and_post_news()
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start(self):
        """Botu başlat"""
        try:
            logging.info("🚀 Quantum Crypto Bot başlatılıyor...")
            
            # Zamanlayıcıyı thread'de başlat
            scheduler_thread = Thread(target=self.start_scheduler)
            scheduler_thread.daemon = True
            scheduler_thread.start()
            
            logging.info("🎉 Bot başarıyla başlatıldı")
            
            # Ana döngü
            while self.running:
                time.sleep(10)
                
        except Exception as e:
            logging.error(f"❌ Bot başlatma hatası: {e}")
            self.stop()
    
    def stop(self):
        """Botu durdur"""
        self.running = False
        logging.info("🛑 Bot durduruldu")

# Botu başlat
if __name__ == "__main__":
    quantum_bot = QuantumCryptoBot()
    
    try:
        quantum_bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Bot kullanıcı tarafından durduruldu")
        quantum_bot.stop()
    except Exception as e:
        logging.error(f"💥 Beklenmeyen hata: {e}")
        quantum_bot.stop()
# Admin komutları için (isteğe bağlı)
@bot.message_handler(commands=['analytics'])
def handle_analytics(message):
    """Admin için analytics dashboard"""
    try:
        if message.from_user.id != Config.ADMIN_ID:
            bot.reply_to(message, "❌ Bu komut sadece admin için.")
            return
        
        analytics = Analytics()
        metrics = analytics.get_performance_metrics()
        coin_stats = analytics.get_coin_analytics()
        sentiment_stats = analytics.get_sentiment_analysis()
        
        response = f"""**🤖 Quantum Bot Analytics Dashboard**

📈 **Genel Metrikler:**
• Toplam Mesaj: {metrics['total_messages']}
• Toplam Görüntülenme: {metrics['total_views']}
• Ort. Engagement: {metrics['avg_engagement']}
• Başarı Oranı: {metrics['success_rate']}%

💰 **Coin Performansı:**
"""
        
        for coin in coin_stats[:5]:  # İlk 5 coin
            response += f"• {coin['coin']}: {coin['message_count']} msj, {coin['avg_views']:.1f} görüntülenme\n"
        
        response += f"\n🎯 **Sentiment Dağılımı:**\n"
        for sentiment in sentiment_stats:
            response += f"• {sentiment['sentiment']}: {sentiment['count']} mesaj\n"
        
        bot.reply_to(message, response, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Analytics komut hatası: {e}")
        bot.reply_to(message, "❌ Analytics verisi alınamadı.")
def update_message_views(self):
    """Mesaj görüntülenmelerini güncelle"""
    try:
        conn = self.analytics.conn
        cursor = conn.cursor()
        
        # Son 24 saatteki mesajları getir
        cursor.execute('''
            SELECT message_id FROM messages 
            WHERE timestamp >= datetime('now', '-1 day')
        ''')
        
        messages = cursor.fetchall()
        
        for (message_id,) in messages:
            try:
                # Telegram'dan mesaj istatistiklerini al
                chat = bot.get_chat(Config.CHANNEL_ID)
                message_info = bot.get_chat_message(chat.id, message_id)
                
                # Views sayısını güncelle (eğer mevcutsa)
                if hasattr(message_info, 'views'):
                    self.analytics.update_message_views(message_id, message_info.views)
                    logging.info(f"📊 Message {message_id}: {message_info.views} views")
                    
            except Exception as e:
                logging.warning(f"⚠️ Message view update failed: {e}")
                continue
                
    except Exception as e:
        logging.error(f"❌ Views update error: {e}")
def send_weekly_analytics_report(self):
    """Haftalık detaylı analytics raporu"""
    try:
        report = self.analytics.generate_detailed_report()
        
        if not report:
            return
        
        summary = report['summary']
        top_coins = report['top_coins']
        recommendations = report['recommendations']
        
        report_text = f"""**📊 Haftalık Analytics Raporu**

🏆 **Genel Performans:**
• Toplam Mesaj: {summary['total_messages']}
• Toplam Görüntülenme: {summary['total_views']}
• Ort. Engagement: {summary['avg_engagement']}
• Başarı Oranı: {summary['success_rate']}%

💰 **En Popüler Coinler:**
"""
        
        for coin in top_coins:
            engagement_emoji = "🔥" if coin['avg_engagement'] > 8 else "📈" if coin['avg_engagement'] > 5 else "📊"
            report_text += f"• {coin['coin']}: {coin['message_count']} mesaj, {coin['avg_views']:.1f} görüntülenme {engagement_emoji}\n"
        
        report_text += f"\n💡 **Optimizasyon Önerileri:**\n"
        for rec in recommendations[:3]:  # İlk 3 öneri
            report_text += f"• {rec}\n"
        
        report_text += f"\n#Analytics #Rapor #{(datetime.now()).strftime('%d%m%Y')}"
        
        bot.send_message(Config.CHANNEL_ID, report_text, parse_mode='Markdown')
        logging.info("📊 Haftalık analytics raporu gönderildi")
        
    except Exception as e:
        logging.error(f"❌ Haftalık rapor hatası: {e}")

def start_scheduler(self):
    """Zamanlayıcıyı başlat - Gelişmiş analytics ile"""
    # Haber kontrolü
    schedule.every(Config.CHECK_INTERVAL).seconds.do(self.check_and_post_news)
    
    # Günlük görüntülenme güncelleme
    schedule.every().day.at("21:00").do(self.update_message_views)
    
    # Günlük özet raporu
    schedule.every().day.at("20:00").do(self.send_daily_report)
    
    # Haftalık detaylı rapor (Pazar günleri)
    schedule.every().sunday.at("19:00").do(self.send_weekly_analytics_report)
    
    logging.info(f"⏰ Zamanlayıcı başlatıldı: Analytics raporları aktif")
    
    # İlk kontrolü hemen yap
    self.check_and_post_news()
    
    while self.running:
        schedule.run_pending()
        time.sleep(1)