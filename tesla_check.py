def main():
    text = fetch_page_text()

    relevant_lines = []

    for line in text.splitlines():
        line = line.strip()

        if (
            "Model Y" in line
            or "מודל Y" in line
            or "₪" in line
            or "טווח" in line
            or "ק״מ" in line
        ):
            relevant_lines.append(line)

    relevant_text = "\n".join(relevant_lines)

    page_id = make_id(relevant_text)

    seen = load_seen()

    if not seen:
        save_seen({page_id})
        send_telegram(
            "✅ Tesla Watch started.\nהמערכת התחילה לעקוב אחרי Model Y."
        )
        return

    if page_id not in seen:
        send_telegram(
            "🚗 יש שינוי במלאי של Model Y!\n\n"
            f"{TESLA_URL}"
        )

        save_seen({page_id})

    else:
        print("No change detected.")
