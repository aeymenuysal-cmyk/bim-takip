import os
import json
import requests
import base64
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GITHUB_TOKEN = os.environ["GUNLUK_GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPO"]
GUNLUK_FILE = "gunluk.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=10)

def get_last_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates?limit=20"
    resp = requests.get(url, timeout=10)
    updates = resp.json().get("result", [])
    today = datetime.now().strftime("%Y-%m-%d")
    for update in reversed(updates):
        msg = update.get("message", {})
        text = msg.get("text", "")
        chat_id = str(msg.get("chat", {}).get("id", ""))
        msg_date = datetime.fromtimestamp(msg.get("date", 0)).strftime("%Y-%m-%d")
        if chat_id == TELEGRAM_CHAT_ID and text and msg_date == today and not text.startswith("/"):
            return text
    return None

def get_gunluk():
    print(f"Repo: {GITHUB_REPO}")
    print(f"Token ilk 4: {GITHUB_TOKEN[:4]}")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GUNLUK_FILE}"

def save_gunluk(data, sha=None):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GUNLUK_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode()).decode()
    payload = {"message": "Günlük güncellendi", "content": content}
    if sha:
        payload["sha"] = sha
    resp = requests.put(url, headers=headers, json=payload, timeout=10)
    print(f"PUT gunluk: {resp.status_code} - {resp.text}")

def soru_sor():
    bugun = datetime.now().strftime("%d.%m.%Y")
    msg = (f"🌙 <b>İyi geceler!</b>\n\n📅 {bugun}\n\nBugün nasıl geçti? Ne yaptın?\n(Cevabını yaz, günlüğüne kaydedeyim 📓)")
    send_telegram(msg)
    print("Soru gönderildi.")

def cevabi_kaydet():
    cevap = get_last_message()
    print(f"Bulunan cevap: {cevap}")
    if not cevap:
        print("Henüz cevap yok.")
        return
    today = datetime.now().strftime("%Y-%m-%d")
    gunluk, sha = get_gunluk()
    if today in gunluk:
        print("Bugün zaten kaydedilmiş.")
        return
    gunluk[today] = {"tarih": datetime.now().strftime("%d.%m.%Y"), "not": cevap}
    save_gunluk(gunluk, sha)
    toplam = len(gunluk)
    send_telegram(f"✅ <b>Günlüğe kaydedildi!</b>\n\n📓 Toplam <b>{toplam}</b> gün yazdın.\nİyi geceler! 😴")
    print(f"Kaydedildi. Toplam {toplam} gün.")

import sys
MODE = os.environ.get("MODE", "soru")
print(f"Mode: {MODE}")
if __name__ == "__main__":
    if MODE == "kaydet":
        cevabi_kaydet()
    else:
        soru_sor()
