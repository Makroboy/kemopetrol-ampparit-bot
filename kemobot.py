# kemobot.py
import requests
from bs4 import BeautifulSoup
import json
import os

SEARCH_URL = "https://www.ampparit.com/haku?q=kemopetrol"
DATA_FILE = "latest_results.json"

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def fetch_titles():
    r = requests.get(SEARCH_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.find_all("a", class_="news-item-headline")

    results = []
    for a in articles:
        title = a.text.strip()
        href = a.get("href")
        if title and href:
            if href.startswith("/"):
                href = f"https://www.ampparit.com{href}"
            results.append(f"{title}\n{href}")
    return results


def load_previous():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_titles(titles):
    with open(DATA_FILE, "w") as f:
        json.dump(titles, f)


def send_telegram(new_titles):
    text = "\ud83d\udcf0 *Uusia Kemopetrol-osumia Ampparitissa:*\n\n"
    text += "\n\n".join(new_titles)

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print("\u2705 Telegram-ilmoitus l\u00e4hetetty.")
    else:
        print("\u274c Virhe Telegram-ilmoituksessa:", response.text)


def main():
    print("\u23f3 Tarkistetaan uudet osumat...")
    current_titles = fetch_titles()
    previous_titles = load_previous()
    new_titles = [t for t in current_titles if t not in previous_titles]

    if new_titles:
        print(f"\ud83d\udd14 {len(new_titles)} uutta osumaa \u2013 l\u00e4hetet\u00e4\u00e4n Telegramiin...")
        send_telegram(new_titles)
        save_titles(current_titles)
    else:
        print("\u2705 Ei uusia osumia.")


if __name__ == "__main__":
    main()
