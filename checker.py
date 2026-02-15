import requests
import os
import asyncio
from telegram import Bot
from datetime import datetime

FROM_STATION = "Warszawa Centralna"
TO_STATION = "Kraków Główny"
DATE = "2026-03-15"
PRICE_LIMIT = 60.0

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def get_price():
    url = "https://bilkom.pl/api/search"

    payload = {
        "from": FROM_STATION,
        "to": TO_STATION,
        "date": DATE,
        "time": "00:00",
        "adults": 1,
        "children": 0
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Błąd API Bilkom: {response.status_code}")

    data = response.json()

    prices = []

    for connection in data.get("connections", []):
        price = connection.get("price")
        if price:
            prices.append(float(price))

    if not prices:
        raise Exception("Nie znaleziono cen w odpowiedzi API")

    return min(prices)


async def send_telegram(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


async def main():
    price = get_price()
    print(f"Aktualna najniższa cena: {price} zł")

    if price < PRICE_LIMIT:
        message = (
            f"🔥 Cena spadła!\n\n"
            f"{FROM_STATION} → {TO_STATION}\n"
            f"Data: {DATE}\n"
            f"Cena: {price} zł\n"
            f"Limit: {PRICE_LIMIT} zł"
        )
        await send_telegram(message)
    else:
        print("Cena powyżej limitu – brak powiadomienia.")


if __name__ == "__main__":
    asyncio.run(main())
