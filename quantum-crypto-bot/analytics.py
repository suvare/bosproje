import sqlite3
import logging
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import pandas as pd

class Analytics:
    def __init__(self, db_path='analytics.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Database tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Messages tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                coin TEXT,
                sentiment TEXT,
                importance INTEGER,
                source TEXT,
                timestamp DATETIME,
                views INTEGER DEFAULT 0,
                engagement_score REAL DEFAULT 0
            )
        ''')
        
        # User engagement tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_engagement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_messages INTEGER,
                total_views INTEGER,
                avg_engagement REAL,
                most_popular_coin TEXT,
                most_popular_sentiment TEXT
            )
        ''')
        
        # Performance metrics tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                api_success_rate REAL,
                avg_response_time REAL,
                error_count INTEGER,
                cache_hit_rate REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("✅ Analytics database initialized")
    
    def log_message(self, message_data):
        """Yeni mesajı database'e kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages 
                (message_id, coin, sentiment, importance, source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                message_data.get('message_id'),
                message_data.get('coin', 'GENERAL'),
                message_data.get('sentiment', 'neutral'),
                message_data.get('importance', 3),
                message_data.get('source', 'Unknown'),
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"❌ Message log error: {e}")
            return False
    
    def update_message_views(self, message_id, views):
        """Mesaj görüntülenme sayısını güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE messages 
                SET views = ?, engagement_score = ? 
                WHERE message_id = ?
            ''', (views, views * 0.8, message_id))  # Basit engagement score
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"❌ Views update error: {e}")
            return False
    
    def get_daily_summary(self, days=7):
        """Günlük özet istatistikleri"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = f'''
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as message_count,
                    SUM(views) as total_views,
                    AVG(views) as avg_views,
                    MAX(views) as max_views,
                    (SELECT coin FROM messages m2 
                     WHERE DATE(m2.timestamp) = DATE(m1.timestamp) 
                     GROUP BY coin ORDER BY COUNT(*) DESC LIMIT 1) as top_coin,
                    (SELECT sentiment FROM messages m3 
                     WHERE DATE(m3.timestamp) = DATE(m1.timestamp) 
                     GROUP BY sentiment ORDER BY COUNT(*) DESC LIMIT 1) as top_sentiment
                FROM messages m1
                WHERE timestamp >= date('now', '-{days} days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.error(f"❌ Daily summary error: {e}")
            return []
    
    def get_coin_analytics(self):
        """Coin bazlı analitikler"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT 
                    coin,
                    COUNT(*) as message_count,
                    SUM(views) as total_views,
                    AVG(views) as avg_views,
                    AVG(engagement_score) as avg_engagement,
                    (SELECT COUNT(*) FROM messages m2 
                     WHERE m2.coin = m1.coin AND m2.sentiment = 'positive') as positive_count,
                    (SELECT COUNT(*) FROM messages m2 
                     WHERE m2.coin = m1.coin AND m2.sentiment = 'negative') as negative_count
                FROM messages m1
                GROUP BY coin
                ORDER BY total_views DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.error(f"❌ Coin analytics error: {e}")
            return []
    
    def get_sentiment_analysis(self):
        """Sentiment analizi"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT 
                    sentiment,
                    COUNT(*) as count,
                    AVG(views) as avg_views,
                    AVG(engagement_score) as avg_engagement
                FROM messages
                GROUP BY sentiment
                ORDER BY count DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logging.error(f"❌ Sentiment analysis error: {e}")
            return []
    
    def generate_engagement_chart(self):
        """Engagement grafiği oluştur"""
        try:
            data = self.get_daily_summary(14)
            if not data:
                return None
            
            dates = [item['date'] for item in data]
            views = [item['total_views'] for item in data]
            messages = [item['message_count'] for item in data]
            
            plt.figure(figsize=(12, 6))
            plt.plot(dates, views, marker='o', label='Toplam Görüntülenme', linewidth=2)
            plt.plot(dates, messages, marker='s', label='Toplam Mesaj', linewidth=2)
            plt.title('14 Günlük Engagement Analizi')
            plt.xlabel('Tarih')
            plt.ylabel('Sayı')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Resmi byte'a çevir
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plt.close()
            
            return buf
            
        except Exception as e:
            logging.error(f"❌ Chart generation error: {e}")
            return None
    
    def get_performance_metrics(self):
        """Bot performans metrikleri"""
        return {
            'total_messages': self._get_total_messages(),
            'total_views': self._get_total_views(),
            'avg_engagement': self._get_avg_engagement(),
            'top_coin': self._get_top_coin(),
            'top_sentiment': self._get_top_sentiment(),
            'success_rate': self._get_success_rate()
        }
    
    def _get_total_messages(self):
        conn = sqlite3.connect(self.db_path)
        count = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
        conn.close()
        return count
    
    def _get_total_views(self):
        conn = sqlite3.connect(self.db_path)
        total = conn.execute('SELECT SUM(views) FROM messages').fetchone()[0] or 0
        conn.close()
        return total
    
    def _get_avg_engagement(self):
        conn = sqlite3.connect(self.db_path)
        avg = conn.execute('SELECT AVG(engagement_score) FROM messages').fetchone()[0] or 0
        conn.close()
        return round(avg, 2)
    
    def _get_top_coin(self):
        conn = sqlite3.connect(self.db_path)
        result = conn.execute('''
            SELECT coin FROM messages 
            GROUP BY coin ORDER BY COUNT(*) DESC LIMIT 1
        ''').fetchone()
        conn.close()
        return result[0] if result else 'N/A'
    
    def _get_top_sentiment(self):
        conn = sqlite3.connect(self.db_path)
        result = conn.execute('''
            SELECT sentiment FROM messages 
            GROUP BY sentiment ORDER BY COUNT(*) DESC LIMIT 1
        ''').fetchone()
        conn.close()
        return result[0] if result else 'N/A'
    
    def _get_success_rate(self):
        # Basit success rate hesaplama
        total = self._get_total_messages()
        if total == 0:
            return 100
        high_engagement = self._get_high_engagement_count()
        return round((high_engagement / total) * 100, 1)
    
    def _get_high_engagement_count(self):
        conn = sqlite3.connect(self.db_path)
        count = conn.execute('SELECT COUNT(*) FROM messages WHERE engagement_score > 5').fetchone()[0]
        conn.close()
        return count
def generate_detailed_report(self):
    """Detaylı analytics raporu"""
    try:
        metrics = self.get_performance_metrics()
        coin_stats = self.get_coin_analytics()
        sentiment_stats = self.get_sentiment_analysis()
        daily_data = self.get_daily_summary(7)
        
        report = {
            'summary': {
                'total_messages': metrics['total_messages'],
                'total_views': metrics['total_views'],
                'avg_engagement': metrics['avg_engagement'],
                'success_rate': metrics['success_rate']
            },
            'top_coins': coin_stats[:5],
            'sentiment_distribution': sentiment_stats,
            'weekly_trend': daily_data,
            'recommendations': self._generate_recommendations(coin_stats, sentiment_stats)
        }
        
        return report
        
    except Exception as e:
        logging.error(f"❌ Detailed report error: {e}")
        return {}

def _generate_recommendations(self, coin_stats, sentiment_stats):
    """Analytics verilerine göre öneriler"""
    recommendations = []
    
    # Coin bazlı öneriler
    top_coin = coin_stats[0] if coin_stats else None
    if top_coin and top_coin['avg_engagement'] > 10:
        recommendations.append(f"✅ {top_coin['coin']} içerikleri çok başarılı, daha fazla paylaşın")
    
    # Sentiment önerileri
    positive_count = next((s['count'] for s in sentiment_stats if s['sentiment'] == 'positive'), 0)
    negative_count = next((s['count'] for s in sentiment_stats if s['sentiment'] == 'negative'), 0)
    
    if positive_count > negative_count * 1.5:
        recommendations.append("🎯 Pozitif haberler daha çok ilgi görüyor")
    elif negative_count > positive_count:
        recommendations.append("⚠️ Negatif haberleri dengeli paylaşın")
    
    # Engagement önerileri
    avg_engagement = self._get_avg_engagement()
    if avg_engagement < 5:
        recommendations.append("📈 Engagement'i artırmak için içerik formatını iyileştirin")
    
    return recommendations
def generate_weekly_chart(self):
    """Haftalık performans grafiği"""
    try:
        data = self.get_daily_summary(7)
        if not data:
            return None
        
        dates = [item['date'] for item in data]
        views = [item['total_views'] for item in data]
        messages = [item['message_count'] for item in data]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Görüntülenme grafiği
        ax1.plot(dates, views, marker='o', color='blue', linewidth=2, label='Görüntülenme')
        ax1.set_title('7 Günlük Görüntülenme Trendi')
        ax1.set_ylabel('Görüntülenme')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Mesaj sayısı grafiği
        ax2.bar(dates, messages, color='green', alpha=0.7, label='Mesaj Sayısı')
        ax2.set_title('Günlük Mesaj Dağılımı')
        ax2.set_ylabel('Mesaj Sayısı')
        ax2.set_xlabel('Tarih')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Resmi byte'a çevir
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf
        
    except Exception as e:
        logging.error(f"❌ Weekly chart error: {e}")
        return None