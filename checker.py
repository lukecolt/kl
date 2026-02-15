import os
import requests
import asyncio
from telegram import Bot

FROM = os.environ["FROM_STATION"]
TO = os.environ["TO_STATION"]
DATE = os.environ["TRAVEL_DATE"]
MAX_PRICE = float(os.environ["MAX_PRICE"])

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

LAST_PRICE_FILE = "last_price.txt"


# --------------------------
# Pobranie ceny z API KOLEO
# --------------------------
def get_price():
    url = "https://koleo.pl/api/v2/search"

    params = {
        "query[date]": DATE,
        "query[from]": FROM,
        "query[to]": TO
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception("Błąd API KOLEO")

    data = response.json()

    # Pierwsza cena z wyników
    price = data["data"][0]["price"]["amount"]
    return float(price)


# --------------------------
# Telegram
# --------------------------
async def notify(price):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text=(
            f"🚆 KOLEO – alert cenowy\n"
            f"{FROM} → {TO}\n"
            f"📅 {DATE}\n"
            f"💰 {price} zł\n"
            f"🎯 limit: {MAX_PRICE} zł"
        )
    )


def load_last_price():
    if not os.path.exists(LAST_PRICE_FILE):
        return None
    with open(LAST_PRICE_FILE) as f:
        return float(f.read())


def save_last_price(price):
    with open(LAST_PRICE_FILE, "w") as f:
        f.write(str(price))


# --------------------------
# MAIN
# --------------------------
async def main():
    price = get_price()
    print("Aktualna cena:", price)

    last_price = load_last_price()

    if price <= MAX_PRICE and price != last_price:
        await notify(price)
        save_last_price(price)
    else:
        print("Brak powiadomienia.")


if __name__ == "__main__":
    asyncio.run(main())
