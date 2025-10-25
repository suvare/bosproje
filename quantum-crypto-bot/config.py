import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Ayarları
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CHANNEL_ID = os.getenv('CHANNEL_ID')
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
    
    # Performans Ayarları
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 1800))
    MAX_POSTS_PER_CHECK = int(os.getenv('MAX_POSTS_PER_CHECK', 1))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 15))
    
    # Genişletilmiş Coin Listesi
    TRACKED_COINS = [
        {'id': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin'},
        {'id': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum'},
        {'id': 'solana', 'symbol': 'SOL', 'name': 'Solana'},
        {'id': 'binancecoin', 'symbol': 'BNB', 'name': 'Binance Coin'},
        {'id': 'cardano', 'symbol': 'ADA', 'name': 'Cardano'},
        {'id': 'ripple', 'symbol': 'XRP', 'name': 'XRP'},
        {'id': 'polkadot', 'symbol': 'DOT', 'name': 'Polkadot'},
        {'id': 'dogecoin', 'symbol': 'DOGE', 'name': 'Dogecoin'},
        {'id': 'avalanche-2', 'symbol': 'AVAX', 'name': 'Avalanche'},
        {'id': 'matic-network', 'symbol': 'MATIC', 'name': 'Polygon'},
        {'id': 'litecoin', 'symbol': 'LTC', 'name': 'Litecoin'},
        {'id': 'uniswap', 'symbol': 'UNI', 'name': 'Uniswap'},
        {'id': 'chainlink', 'symbol': 'LINK', 'name': 'Chainlink'}
    ]
    
    @classmethod
    def validate(cls):
        """Config doğrulama"""
        required_vars = ['BOT_TOKEN', 'CHANNEL_ID']
        
        for var in required_vars:
            value = getattr(cls, var)
            if not value:
                logging.error(f"❌ Gerekli değişken eksik: {var}")
                return False
        
        # CHANNEL_ID kontrolü (@ işareti ile başlamalı)
        if not cls.CHANNEL_ID.startswith('@'):
            logging.error("❌ CHANNEL_ID @ işareti ile başlamalı (örnek: @channelname)")
            return False
        
        logging.info("✅ Config doğrulama başarılı")
        return True