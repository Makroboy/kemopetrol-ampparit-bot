import os
import requests
from bs4 import BeautifulSoup
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

# Telegramin ympäristömuuttujat
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Haun URL ja backendin osoite
SEARCH_URL = "https://www.ampparit.com/haku?q=kemopetrol"
API_BASE = "https://lumbar-pickle-honey.glitch.me"

# Hae aiemmin nähdyt otsikot backendistä
def load_seen_titles():
    try:
        response = requests.get(f"{API_BASE}/seen")
        response.raise_for_status()
        return set(response.json())
    except Exception as e:
        print(f"⚠️ Virhe ladatessa vanhoja osumia: {e}")
        return set()

# Tallenna uudet otsikot backend-palvelimeen
def save_seen_titles(titles):
    try:
        response = requests.post(
            f"{API_BASE}/seen",
            headers={"Content-Type": "application/json"},
            data=json.dumps(sorted(titles))
        )
        response.raise_for_status()
        print("💾 Tallennettu osumat backend-palvelimeen.")
    except Exception as e:
        print(f"⚠️ Virhe tallentaessa osumia: {e}")

# Parsitaan hakutulokset
def fetch_titles():
    response = requests.get(SEARCH_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", class_="news-item-headline")
    return [(link.text.strip(), link["href"]) for link in links]

# Lähetetään Telegramiin
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

# Päälogiikka
def main():
    print("⏳ Tarkistetaan uudet osumat...")

    seen_titles = load_seen_titles()
    current_titles = fetch_titles()
    current_titles_set = set(title for title, _ in current_titles)

    new_titles = [(title, url) for title, url in current_titles if title not in seen_titles]

    if new_titles:
        print(f"🔔 {len(new_titles)} uutta osumaa, lähetetään Telegramiin...")
        send_telegram(new_titles)
        save_seen_titles(current_titles_set)
    else:
        print("👌 Ei uusia osumia.")
        save_seen_titles(current_titles_set)  # Varmista että viimeisimmät tallennetaan myös

if __name__ == "__main__":
    main()
