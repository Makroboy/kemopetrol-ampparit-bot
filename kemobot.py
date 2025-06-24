import os
import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEARCH_URL = "https://www.ampparit.com/haku?q=kemopetrol"
BACKEND_URL = "https://lumbar-pickle-honey.glitch.me"

def load_seen_titles():
    try:
        response = requests.get(f"{BACKEND_URL}/seen")
        if response.status_code == 200:
            return set(response.json())
    except Exception as e:
        print(f"⚠️ Virhe ladattaessa tallennettuja otsikoita: {e}")
    return set()

def save_seen_titles(titles):
    try:
        response = requests.post(f"{BACKEND_URL}/seen", json=list(sorted(titles)))
        if response.status_code == 200:
            print("💾 Tallennettiin uudet otsikot Glitch-backendiin.")
        else:
            print(f"⚠️ Tallennus epäonnistui: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Virhe tallennettaessa: {e}")

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

    # ➕ Keinotekoinen testiosuma
    current_titles.append(("TESTI – tämä on keinotekoinen osuma", "https://example.com/testi"))

    current_titles_set = set(title for title, _ in current_titles)
    new_titles = [(title, url) for title, url in current_titles if title not in seen_titles]

    if new_titles:
        print(f"🔔 {len(new_titles)} uutta osumaa, lähetetään Telegramiin...")
        send_telegram(new_titles)
        save_seen_titles(current_titles_set)
    else:
        print("👌 Ei uusia osumia.")
        save_seen_titles(current_titles_set)  # Päivitetään kuitenkin

if __name__ == "__main__":
    main()
