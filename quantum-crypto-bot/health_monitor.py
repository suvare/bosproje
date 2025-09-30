import logging
import psutil
import time
from datetime import datetime
from threading import Thread

class HealthMonitor:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.running = True
        self.metrics = {
            'start_time': datetime.now(),
            'news_count': 0,
            'errors': 0,
            'last_check': None
        }
    
    def start_monitoring(self):
        """Sistem sağlık kontrolünü başlat"""
        monitor_thread = Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        logging.info("🏥 Health monitor started")
    
    def _monitor_loop(self):
        """Sürekli monitoring"""
        while self.running:
            try:
                self._check_system_health()
                time.sleep(60)  # Her dakika kontrol
            except Exception as e:
                logging.error(f"❌ Health monitor hatası: {e}")
    
    def _check_system_health(self):
        """Sistem durumunu kontrol et"""
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        
        self.metrics.update({
            'last_check': datetime.now(),
            'cpu_usage': cpu_percent,
            'memory_usage': memory_info.percent,
            'uptime': (datetime.now() - self.metrics['start_time']).total_seconds()
        })
        
        # Uyarı kontrolü
        if cpu_percent > 80:
            logging.warning(f"⚠️ Yüksek CPU kullanımı: {cpu_percent}%")
        
        if memory_info.percent > 85:
            logging.warning(f"⚠️ Yüksek RAM kullanımı: {memory_info.percent}%")
    
    def get_metrics(self):
        """Metrikleri getir"""
        return self.metrics