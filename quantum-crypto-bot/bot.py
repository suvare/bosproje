import telebot
import schedule
import time
import logging
from threading import Thread
from datetime import datetime

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