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

def fetch_bim_products():
    url = "https://www.bim.com.tr/categories/aktuel-urunler.aspx"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    products = []
    for el in soup.find_all(["h2", "h3", "h4", "p", "span", "div"]):
        text = el.get_text(strip=True)
        if 5 < len(text) < 200:
            products.append(text)
    return products

def main():
    print("BİM kontrol ediliyor...")
    products = fetch_bim_products()
    matches = [p for p in products if any(kw in p.lower() for kw in KEYWORDS)]

    if matches:
        lines = ["🏋️ <b>BİM'de Supplement Geldi!</b>\n"]
        for m in matches[:5]:
            lines.append(f"• {m}")
        lines.append("\n🔗 <a href='https://www.bim.com.tr/categories/aktuel-urunler.aspx'>BİM Aktüel Ürünler</a>")
        msg = "\n".join(lines)
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"})
        print("Bildirim gönderildi!")
    else:
        print("Ürün bulunamadı.")

if __name__ == "__main__":
    main()
