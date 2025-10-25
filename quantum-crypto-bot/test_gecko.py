import requests
import json

url = "https://api.coingecko.com/api/v3/news"
params = {'per_page': 3, 'page': 1}

print("🔍 CoinGecko API Testi...")

try:
    response = requests.get(url, params=params)
    print(f"✅ Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"🎉 {len(data)} haber bulundu!")
        
        if len(data) > 0:
            print(f"📰 İlk haber: {data[0]['title']}")
            print(f"🔗 Link: {data[0]['url']}")
        
        # Tüm response'u göster
        print(f"📄 Response önizleme: {json.dumps(data[:1], indent=2)[:500]}...")
    else:
        print(f"❌ Hata: {response.text}")
        
except Exception as e:
    print(f"💥 Exception: {e}")