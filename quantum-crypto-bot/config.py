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
    
    # Takip Edilen Coin'ler (3 coin ile sınırlı - rate limit için)
    TRACKED_COINS = [
        {'id': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin'},
        {'id': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum'},
        {'id': 'solana', 'symbol': 'SOL', 'name': 'Solana'}
    ]
    
    @classmethod
    def validate(cls):
        """Config doğrulama"""
        required_vars = ['BOT_TOKEN', 'CHANNEL_ID']
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"❌ Gerekli değişken: {var}")
        
        print("✅ Config doğrulama başarılı")
        return True