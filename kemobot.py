import os
import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEARCH_URL = "https://www.ampparit.com/haku?q=kemopetrol"
GLITCH_API_BASE = "https://lumbar-pickle-honey.glitch.me"

def fetch_titles():
    response = requests.get(SEARCH_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", class_="news-item-headline")
    return [(link.text.strip(), link["href"]) for link in links]

def get_seen_titles():
    try:
        response = requests.get(f"{GLITCH_API_BASE}/seen")
        response.raise_for_status()
        return set(response.json())
    except Exception as e:
        print(f"⚠️ Virhe haettaessa nähtyjä otsikoita: {e}")
        return set()

def add_seen_titles(titles):
    try:
        response = requests.post(f"{GLITCH_API_BASE}/add", json={"titles": list(titles)})
        response.raise_for_status()
        print("📌 Tallennettu uudet otsikot Glitchiin.")
    except Exception as e:
        print(f"⚠️ Virhe tallennettaessa otsikoita: {e}")

def send_telegram(new_titles):
    for title, url in new_titles:
        message = f"🆕 {title}\n🔗 {url}"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data=payload
        )
        print(f"✅ Lähetetty: {title} ({response.status_code})")

def main():
    print("⏳ Tarkistetaan uudet osumat...")

    seen_titles = get_seen_titles()
    current_titles = fetch_titles()
    new_titles = [(title, url) for title, url in current_titles if title not in seen_titles]

    if new_titles:
        print(f"🔔 {len(new_titles)} uutta osumaa, lähetetään Telegramiin...")
        send_telegram(new_titles)
        new_titles_set = set(title for title, _ in new_titles)
        add_seen_titles(new_titles_set)
    else:
        print("👌 Ei uusia osumia.")

if __name__ == "__main__":
    main()
