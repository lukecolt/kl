import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

FROM = os.getenv("FROM_STATION")
TO = os.getenv("TO_STATION")
DATE = os.getenv("TRAVEL_DATE")
MAX_PRICE = float(os.getenv("MAX_PRICE"))

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

LAST_PRICE_FILE = "last_price.txt"


def get_price():
    """
    Prosty scraping wyników wyszukiwania KOLEO.
    Jeśli KOLEO zmieni strukturę HTML – trzeba zaktualizować selektor.
    """
    search_url = (
        f"https://koleo.pl/rozklad-pkp/"
        f"{FROM}/{TO}/{DATE}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(search_url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # ⚠️ Ten selektor może wymagać aktualizacji
    price_element = soup.select_one(".connection-price")

    if not price_element:
        raise Exception("Nie znaleziono ceny – możliwa zmiana struktury strony.")

    price_text = price_element.text.strip()
    price = float(
        price_text.replace("zł", "")
        .replace(",", ".")
        .strip()
    )

    return price


def notify(price):
    bot = Bot(token=TELEGRAM_TOKEN)
    message = (
        f"🚆 KOLEO – Alert cenowy!\n"
        f"{FROM} → {TO}\n"
        f"📅 {DATE}\n"
        f"💰 {price} zł\n"
        f"🎯 Limit: {MAX_PRICE} zł"
    )
    bot.send_message(chat_id=CHAT_ID, text=message)


def load_last_price():
    if not os.path.exists(LAST_PRICE_FILE):
        return None
    with open(LAST_PRICE_FILE, "r") as f:
        return float(f.read().strip())


def save_last_price(price):
    with open(LAST_PRICE_FILE, "w") as f:
        f.write(str(price))


if __name__ == "__main__":
    try:
        price = get_price()
        print("Aktualna cena:", price)

        last_price = load_last_price()

        # Alert tylko jeśli:
        # - cena <= limit
        # - oraz różni się od poprzednio zapisanej
        if price <= MAX_PRICE and price != last_price:
            notify(price)
            save_last_price(price)

    except Exception as e:
        print("Błąd:", e)
