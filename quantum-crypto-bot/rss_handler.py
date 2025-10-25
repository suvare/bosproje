import feedparser
import logging
from datetime import datetime
from config import Config

class RSSHandler:
    def __init__(self):
        self.feeds = [
            "https://cointelegraph.com/rss",
            "https://www.coindesk.com/arc/outboundfeeds/rss/"
        ]
    
    def get_news(self):
        """RSS feed'lerden haber çek"""
        try:
            all_news = []
            
            for feed_url in self.feeds:
                news = self._parse_feed(feed_url)
                all_news.extend(news)
            
            return all_news[:Config.MAX_POSTS_PER_CHECK]
            
        except Exception as e:
            logging.error(f"RSS hatası: {e}")
            return []
    
    def _parse_feed(self, feed_url):
        """RSS feed'i parse et"""
        feed = feedparser.parse(feed_url)
        news_list = []
        
        for entry in feed.entries[:3]:  # İlk 3 haber
            news_list.append({
                'title': entry.title,
                'url': entry.link,
                'importance': 3,
                'source': feed.feed.get('title', 'RSS Feed'),
                'created_at': datetime.now().strftime("%Y-%m-%d")
            })
        
        return news_list