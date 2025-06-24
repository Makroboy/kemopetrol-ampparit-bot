import os
import time
import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEARCH_URL = "https://www.ampparit.com/haku?q=kemopetrol"
SEEN_TITLES_FILE = "seen_titles.txt"

def load_seen_titles():
    if os.path.exists(SEEN_TITLES_FILE):
        with open(SEEN_TITLES_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def save_seen_titles(titles):
    with open(SEEN_TITLES_FILE, "w", encoding="utf-8") as f:
        for title in titles:
            f.write(title + "\n")

def fetch_titles():
    response = requests.get(SEARCH_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", class_="news-item-headline")
    return [(link.text.strip(), link["href"]) for link in links]

def send_telegram(new_titles):
    for title, url in new_titles:
        message = f"🆕 {title}\n🔗 {url}"
        safe_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message.encode("utf-8", "surrogatepass").decode("utf-8"),
        }
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data=safe_payload
        )
        print(f"✅ Lähetetty: {title} ({response.status_code})")

def main():
    print("⏳ Tarkistetaan uudet osumat...")

    seen_titles = load_seen_titles()
    current_titles = fetch_titles()
    current_titles_set = set(title for title, _ in current_titles)

    new_titles = [(title, url) for title, url in current_titles if title not in seen_titles]
    new_titles.append(("TESTI: Tämä on testi-ilmoitus", "https://example.com"))
    
    if new_titles:
        print(f"🔔 {len(new_titles)} uutta osumaa, lähetetään Telegramiin...")
        send_telegram(new_titles)
        save_seen_titles(current_titles_set)
    else:
        print("👌 Ei uusia osumia.")

if __name__ == "__main__":
    main()
