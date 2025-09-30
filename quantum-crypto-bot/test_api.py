import requests
import json

def test_api():
    print("🔍 CoinGecko API Testi...")
    
    url = "https://api.coingecko.com/api/v3/news"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🎉 {len(data)} haber bulundu!")
            
            if len(data) > 0:
                print("\n📰 İLK 3 HABER:")
                for i, news in enumerate(data[:3]):
                    print(f"{i+1}. {news.get('title', 'Başlık yok')}")
                    print(f"   🔗 {news.get('url', 'Link yok')}")
                    print(f"   📢 {news.get('source', {}).get('title', 'Kaynak yok')}")
                    print()
        else:
            print(f"❌ Hata: {response.text}")
            
    except Exception as e:
        print(f"💥 Exception: {e}")

if __name__ == "__main__":
    test_api()