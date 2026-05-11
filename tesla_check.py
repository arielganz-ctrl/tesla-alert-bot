import os
import json
import hashlib
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

TESLA_URL = "https://www.tesla.com/he_IL/inventory/new/my?PaymentType=cash"
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEEN_FILE = Path("seen_tesla.json")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=20).raise_for_status()


def make_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(list(seen), ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_page_text():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            locale="he-IL",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
        page.goto(TESLA_URL, wait_until="networkidle", timeout=90000)
        page.wait_for_timeout(7000)
        text = page.inner_text("body")
        browser.close()
        return text


def main():
    text = fetch_page_text()
    page_id = make_id(text)
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
