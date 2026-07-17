import time
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# --- TWILIO AYARLARI ---
# Twilio panelinden aldığın bilgileri buraya yapıştır
ACCOUNT_SID = "AC0177283e190c54406c88ba3829f73b57"
AUTH_TOKEN = "01f4743720f871618d985d2d36f1fdbf"
TWILIO_NUMBER = "+14472235127"  # Örn: '+1234567890'
MY_NUMBER = "+905525886316"        # Kendi numaran (Örn: '+905xxxxxxxxx')

# --- HEDEF WEB SİTESİ ---
# ÖSYM Duyurular sayfası url'i
OSYM_URL = "https://www.osym.gov.tr/TR,21/duyurular.html"

def telefon_ara():
    """Sonuçlar açıklandığında telefonunu arayacak fonksiyon"""
    print("🔔 YKS Sınav Sonuçları Açıklandı! Telefon aranıyor...")
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        # Telefon araması başlatıyoruz
        call = client.calls.create(
            twiml="<Response><Say language='tr-TR' voice='alice'>Uyan uyan! YKS sonuclari aciklandi! Hemen bilgisayar basina gec!</Say></Response>",
            to=MY_NUMBER,
            from_=TWILIO_NUMBER
        )
        print(f"📞 Arama başarıyla başlatıldı! Arama ID: {call.sid}")
    except Exception as e:
        print(f"❌ Arama sırasında bir hata oluştu: {e}")

def duyurulari_kontrol_et():
    # Sayfaya istek atıyoruz (Tarayıcı gibi görünmek için User-Agent ekledik)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(OSYM_URL, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ ÖSYM sitesine erişilemedi. Durum kodu: {response.status_code}")
            return False

        # HTML içeriğini ayrıştırıyoruz
        soup = BeautifulSoup(response.text, "html.parser")
        
        # ÖSYM sayfasındaki tüm duyuru başlıklarını buluyoruz (genelde 'a' etiketleri içinde olur)
        duyurular = soup.find_all("a")
        
        for duyuru in duyurular:
            baslik = duyuru.get_text().strip().lower()
            
            # Başlıkta "yks" ve "sonuç" kelimelerinin aynı anda geçip geçmediğini kontrol ediyoruz
            if "yks" in baslik and "sonuç" in baslik:
                print(f"🎉 Eşleşen duyuru bulundu: {duyuru.get_text().strip()}")
                return True
                
    except Exception as e:
        print(f"❌ Kontrol sırasında hata oluştu: {e}")
        
    return False

def ana_dongu():
    print("⏳ ÖSYM YKS takip sistemi başlatıldı. Her 30 saniyede bir kontrol ediliyor...")
    
    while True:
        aciklandi_mi = duyurulari_kontrol_et()
        
        if aciklandi_mi:
            # Sonuç açıklandıysa ara ve döngüyü sonlandır
            telefon_ara()
            break
        else:
            print(f"😴 Henüz bir gelişme yok... Son kontrol: {time.strftime('%H:%M:%S')}")
            
        # 30 saniye bekle ve tekrar kontrol et
        time.sleep(30)

if __name__ == "__main__":
    # Test etmek istersen direkt telefon_ara() fonksiyonunu çalıştırabilirsin.
    # telefon_ara() 
    ana_dongu()