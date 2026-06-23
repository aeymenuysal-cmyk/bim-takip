import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

KEYWORDS = [
    "kreatin", "creatine", "protein tozu", "whey",
    "protein powder", "mass gainer", "amino asit", "bcaa",
    "pre-workout", "pre workout"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.bim.com.tr/Categories/100/aktuel-urunler.aspx"

def get_all_dates():
    """Ana sayfadan tüm aktüel tarih linklerini çek"""
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    dates = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "Bim_AktuelTarihKey=" in href:
            label = a.get_text(strip=True)
            full_url = "https://www.bim.com.tr" + href if href.startswith("/") else href
            if label and label not in dates:
                dates[label] = full_url

    return dates

def scan_page(url):
    """Bir aktüel sayfasındaki ürün isimlerini döndür"""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    products = []
    for el in soup.find_all(["h2", "h3", "h4", "p", "span"]):
        text = el.get_text(strip=True)
        if 5 < len(text) < 200:
            products.append(text)
    return products

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }, timeout=10)

def main():
    print("BİM tüm aktüel tarihler taranıyor...")

    dates = get_all_dates()
    print(f"{len(dates)} tarih bulundu: {list(dates.keys())}")

    found_any = False

    for label, url in dates.items():
        print(f"  → {label} taranıyor...")
        try:
            products = scan_page(url)
            matches = [p for p in products if any(kw in p.lower() for kw in KEYWORDS)]

            if matches:
                found_any = True
                lines = [f"🏋️ <b>BİM'de Supplement Bulundu!</b>\n📅 <b>{label}</b>\n"]
                for m in matches[:5]:
                    lines.append(f"• {m}")
                lines.append(f"\n🔗 <a href='{url}'>BİM Aktüel - {label}</a>")
                msg = "\n".join(lines)
                send_telegram(msg)
                print(f"    ✅ {len(matches)} ürün bulundu, bildirim gönderildi!")
            else:
                print(f"    ❌ Ürün bulunamadı.")
        except Exception as e:
            print(f"    ⚠️ Hata: {e}")

    if not found_any:
        print("Hiçbir tarihte kreatin/protein tozu bulunamadı.")

if __name__ == "__main__":
    main()
