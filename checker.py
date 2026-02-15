import os
import asyncio
from playwright.async_api import async_playwright
from telegram import Bot

FROM = os.environ["FROM_STATION"]
TO = os.environ["TO_STATION"]
DATE = os.environ["TRAVEL_DATE"]
MAX_PRICE = float(os.environ["MAX_PRICE"])

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

LAST_PRICE_FILE = "last_price.txt"


async def get_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://koleo.pl/", timeout=60000)

        await page.fill('input[placeholder="Skąd"]', FROM)
        await page.fill('input[placeholder="Dokąd"]', TO)
        await page.fill('input[type="date"]', DATE)

        await page.click('button[type="submit"]')

        # czekamy aż pojawi się cena
        await page.wait_for_selector("text=zł", timeout=30000)

        text = await page.inner_text("text=zł")
        price = float(
            text.split("zł")[0]
            .replace(",", ".")
            .strip()
        )

        await browser.close()
        return price


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


async def main():
    price = await get_price()
    print("Aktualna cena:", price)

    last_price = load_last_price()

    if price <= MAX_PRICE and price != last_price:
        await notify(price)
        save_last_price(price)


if __name__ == "__main__":
    asyncio.run(main())
