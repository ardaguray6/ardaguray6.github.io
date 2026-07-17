import requests
from bs4 import BeautifulSoup
from twilio.rest import Client
import time
import sys

# --- TWILIO BİLGİLERİNİ DOĞRUDAN BURAYA YAZ ---
ACCOUNT_SID = "AC0177283e190c54406c88ba3829f73b57"
AUTH_TOKEN = "b16d18bf4bbaaaecfa42c65ebdd08e86"
TWILIO_NUMBER = "+14472235127"
MY_NUMBER = "+905551638737"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    session = requests.Session()
    session.headers.update(headers)

    for attempt in range(3):  # 3 kere deneme
        try:
            print(f"🔗 ÖSYM sitesine bağlanılıyor... (Deneme {attempt+1}/3)")
            response = session.get(OSYM_URL, timeout=20)
            
            print(f"📡 Bağlantı durumu: {response.status_code}")
            
            if response.status_code != 200:
                print(f"⚠️ Site yanıt vermedi: {response.status_code}")
                time.sleep(5)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            tum_linkler = soup.find_all("a")

            print(f"🔍 Toplam bulunan <a> etiketi: {len(tum_linkler)}")
            print("\n🔍 --- DUYURULAR KONTROL EDİLİYOR ---")

            duyuru_sayisi = 0
            bulundu = False

            for link in tum_linkler:
                href = link.get("href", "").lower()
                metin = link.get_text().strip().lower()

                if len(metin) > 15 and "/tr," in href:
                    duyuru_sayisi += 1
                    
                    if duyuru_sayisi <= 12:  # Daha fazla log görelim
                        print(f"   {duyuru_sayisi:2d}. '{metin[:80]}...'")

                    if "yks" in metin and ("sonuç" in metin or "açıklandı" in metin or "sonuclari" in metin):
                        print(f"\n🎉 HEDEF BULUNDU! → {metin}")
                        bulundu = True
                        break

            print("-------------------------------------------")
            print(f"Toplam incelenen duyuru: {duyuru_sayisi}")

            if bulundu:
                return True

            if duyuru_sayisi == 0:
                print("⚠️ Hiç duyuru linki bulunamadı! Sayfa yapısı değişmiş olabilir.")

            return False

        except requests.exceptions.Timeout:
            print("⏱️ Zaman aşımı, tekrar deneniyor...")
        except Exception as e:
            print(f"❌ Hata: {e}")
        
        time.sleep(5)  # Denemeler arası bekleme

    print("❌ 3 deneme sonrası da siteye bağlanılamadı.")
    return False

if __name__ == "__main__":
    print("=== YKS KONTROL BAŞLADI ===")
    print(f"Zaman: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    aciklandi_mi = duyurulari_kontrol_et()
   
    if aciklandi_mi:
        telefon_ara()
    else:
        print("😴 Yeni bir YKS duyurusu yok. Beklemeye devam...")
    
    print("=== İŞLEM TAMAMLANDI ===")
