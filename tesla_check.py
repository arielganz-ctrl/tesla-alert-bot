import os
import json
import hashlib
import requests
from pathlib import Path

TESLA_URL = "https://www.tesla.com/he_IL/inventory/new/my?PaymentType=cash"
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEEN_FILE = Path("seen_tesla.json")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload, timeout=20).raise_for_status()


def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2), encoding="utf-8")


def make_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch_page():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "he-IL,he;q=0.9,en;q=0.8"
    }
    r = requests.get(TESLA_URL, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text


def main():
    html = fetch_page()
    page_id = make_id(html)
    seen = load_seen()

    if not seen:
        save_seen({page_id})
        send_telegram("✅ Tesla Watch started.\nהמערכת התחילה לעקוב אחרי עמוד המלאי של טסלה.")
        return

    if page_id not in seen:
        send_telegram(
            "🚗 יש שינוי בעמוד המלאי של Tesla Israel!\n\n"
            "יכול להיות שנוסף רכב חדש או שהמלאי השתנה.\n\n"
            f"{TESLA_URL}"
        )
        save_seen({page_id})
    else:
        print("No change detected.")


if __name__ == "__main__":
    main()