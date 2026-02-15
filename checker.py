import os
import asyncio
from playwright.async_api import async_playwright
from telegram import Bot

# --------------------------
# Ustawienia z GitHub Secrets
# --------------------------
FROM = os.environ["FROM_STATION"]
TO = os.environ["TO_STATION"]
DATE = os.environ["TRAVEL_DATE"]  # format YYYY-MM-DD
MAX_PRICE = float(os.environ["MAX_PRICE"])

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

LAST_PRICE_FILE = "last_price.txt"

# --------------------------
# Funkcja pobierająca cenę
# --------------------------
async def get_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Używamy URL z datą w query string (stabilne w CI)
        url = f"https://koleo.pl/?from={FROM}&to={TO}&date={DATE}"
        await page.goto(url, wait_until="networkidle", timeout=60000)

        # Czekamy, aż pojawi się cena
        awa
