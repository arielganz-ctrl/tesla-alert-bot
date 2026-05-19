import os
import json
import hashlib
import urllib.parse
import requests
from pathlib import Path

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEEN_FILE = Path("seen_tesla.json")

SEARCH_URL = "https://www.tesla.com/inventory/api/v4/inventory-results"

QUERY = {
    "query": {
        "model": "my",
        "condition": "new",
        "market": "IL",
        "language": "he",
        "super_region": "europe",
        "arrangeby": "Price",
        "order": "asc"
    },
    "offset": 0,
    "count": 50,
    "outsideOffset": 0,
    "outsideSearch": False
}


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
    SEEN_FILE.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_inventory():
    params = {"query": json.dumps(QUERY, separators=(",", ":"))}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    r = requests.get(SEARCH_URL, params=params, headers=headers, timeout=30)
    print("Tesla status:", r.status_code)
    print(r.text[:500])
    r.raise_for_status()

    data = r.json()
    return data.get("results", [])


def car_id(car):
    return car.get("VIN") or hashlib.sha256(json.dumps(car, sort_keys=True).encode()).hexdigest()


def describe_car(car):
    vin = car.get("VIN", "")
    price = car.get("PurchasePrice") or car.get("Price") or ""
    trim = car.get("TrimName") or car.get("TRIM") or ""
    paint = car.get("PAINT") or ""
    wheels = car.get("WHEELS") or ""
    odometer = car.get("Odometer") or ""

    return (
        "🚗 Model Y חדש במלאי!\n\n"
        f"VIN: {vin}\n"
        f"מחיר: {price}\n"
        f"דגם/רמת גימור: {trim}\n"
        f"צבע: {paint}\n"
        f"ג׳אנטים: {wheels}\n"
        f"ק״מ: {odometer}\n\n"
        "https://www.tesla.com/he_IL/inventory/new/my?TRIM=MY&PaymentType=cash"
    )


def main():
    cars = fetch_inventory()
    current_ids = {car_id(car): car for car in cars}
    seen = load_seen()

    if not seen:
        save_seen(set(current_ids.keys()))
        send_telegram(f"✅ Tesla Model Y Watch started.\nכרגע נמצאו {len(cars)} רכבים במלאי.")
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
