import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# --- TWILIO BİLGİLERİNİ DOĞRUDAN BURAYA YAZ ---
ACCOUNT_SID = "AC0177283e190c54406c88ba3829f73b57"
AUTH_TOKEN = "b16d18bf4bbaaaecfa42c65ebdd08e86"
TWILIO_NUMBER = "+14472235127"
MY_NUMBER = "+905525886316"

OSYM_URL = "https://www.osym.gov.tr/TR,21/duyurular.html"

def telefon_ara():
    print("🔔 YKS Sınav Sonuçları Açıklandı! Telefon aranıyor...")
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        call = client.calls.create(
            twiml="<Response><Say language='tr-TR' voice='alice'>Uyan uyan! YKS sonuclari aciklandi! Hemen bilgisayar basina gec!</Say></Response>",
            to=MY_NUMBER,
            from_=TWILIO_NUMBER
        )
        print(f"📞 Arama başarıyla başlatıldı! Arama ID: {call.sid}")
    except Exception as e:
        print(f"❌ Arama sırasında bir hata oluştu: {e}")

def duyurulari_kontrol_et():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "tr,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }
    
    try:
        print("🔗 ÖSYM sitesine bağlanılıyor...")
        response = requests.get(OSYM_URL, headers=headers, timeout=15)
        
        print(f"📡 Bağlantı durumu: {response.status_code}")
        if response.status_code != 200:
            print(f"⚠️ ÖSYM sitesine erişilemedi. Durum kodu: {response.status_code}")
            return False

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Sayfadaki tüm linkleri (a etiketlerini) alıyoruz
        tum_linkler = soup.find_all("a")
        
        print("\n🔍 --- DUYURULAR TAYFASI KONTROL EDİLİYOR ---")
        
        duyuru_sayisi = 0
        for link in tum_linkler:
            href = link.get("href", "")
            metin = link.get_text().strip().lower()
            
            # ÖSYM'nin gerçek duyuru linkleri genellikle '/TR,' ile başlar
            # Menü linklerini veya boş yazıları eliyoruz
            if "/tr," in href.lower() and len(metin) > 15:
                duyuru_sayisi += 1
                
                # Sadece en güncel ilk 10 duyuruyu ekrana yazdırıp kontrol edelim
                if duyuru_sayisi <= 10:
                    print(f"👉 Bulunan Duyuru #{duyuru_sayisi}: '{metin}'")
                
                # Anahtar kelime kontrolü (yks ve sonuç/açıklandı kelimeleri aynı başlıkta geçmeli)
                if "yks" in metin and ("sonuç" in metin or "açıklandı" in metin):
                    print(f"\n🎉 HEDEF BULUNDU! Duyuru başlığı: {metin}")
                    return True
                    
        print("-------------------------------------------\n")
        
        if duyuru_sayisi == 0:
            print("⚠️ Uyarı: Sayfada hiç geçerli duyuru linki tespit edilemedi! Sitenin yapısı değişmiş olabilir.")
            
    except requests.exceptions.Timeout:
        print("⏱️ Zaman aşımı! ÖSYM sitesi yanıt vermedi.")
    except Exception as e:
        print(f"❌ Kontrol sırasında hata oluştu: {e}")
    return False

if __name__ == "__main__":
    aciklandi_mi = duyurulari_kontrol_et()
    
    if aciklandi_mi:
        telefon_ara()
    else:
        print("😴 Yeni bir YKS duyurusu yok. Beklemeye devam...")
