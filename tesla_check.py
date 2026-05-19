import os
import json
import hashlib
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

TESLA_URL = "https://www.tesla.com/he_IL/inventory/new/my?TRIM=MY&PaymentType=cash"
SEEN_FILE = Path("seen_tesla.json")


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=20)
    print("Telegram:", r.status_code, r.text)
    r.raise_for_status()


def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    return set()


def save_seen(seen):
    SEEN_FILE.write_text(
        json.dumps(sorted(seen), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def car_id(car):
    return car.get("VIN") or hashlib.sha256(
        json.dumps(car, sort_keys=True).encode()
    ).hexdigest()


def describe_car(car):
    vin = car.get("VIN", "")
    price = car.get("PurchasePrice") or car.get("Price") or ""
    trim = car.get("TrimName") or car.get("TRIM") or ""
    paint = car.get("PAINT") or ""
    wheels = car.get("WHEELS") or ""

    return (
        "🚗 Model Y חדש הופיע במלאי Tesla Israel!\n\n"
        f"VIN: {vin}\n"
        f"מחיר: {price}\n"
        f"דגם: {trim}\n"
        f"צבע: {paint}\n"
        f"ג׳אנטים: {wheels}\n\n"
        f"{TESLA_URL}"
    )


def fetch_inventory_from_browser():
    inventory_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            locale="he-IL",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )

        def handle_response(response):
            nonlocal inventory_data
            if "inventory-results" in response.url:
                try:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        inventory_data = results
                        print(f"Found inventory API response: {len(results)} cars")
                except Exception as e:
                    print("Could not parse inventory response:", e)

        page.on("response", handle_response)

        page.goto(TESLA_URL, wait_until="networkidle", timeout=90000)
        page.wait_for_timeout(10000)

        browser.close()

    return inventory_data


def main():
    cars = fetch_inventory_from_browser()

    if not cars:
        send_telegram(
            "⚠️ Tesla Watch רץ, אבל לא הצליח לקרוא רכבי Model Y מהמלאי.\n"
            "יכול להיות שטסלה חסמה זמנית את GitHub או ששינתה את האתר."
        )
        return

    current_ids = {car_id(car): car for car in cars}
    seen = load_seen()

    if not seen:
        save_seen(set(current_ids.keys()))
        send_telegram(f"✅ Tesla Model Y Watch started.\nכרגע נמצאו {len(cars)} רכבי Model Y במלאי.")
        return

    new_ids = set(current_ids.keys()) - seen

    if new_ids:
        for cid in new_ids:
            send_telegram(describe_car(current_ids[cid]))

        save_seen(set(current_ids.keys()))
    else:
        print(f"No new Model Y cars. Current count: {len(cars)}")


if __name__ == "__main__":
    main()
