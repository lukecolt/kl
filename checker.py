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
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://koleo.pl/", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(2)  # czekamy na pełny JS

        inputs = await page.query_selector_all("input")
        await inputs[0].fill(FROM)
        await inputs[1].fill(TO)

        # Data
        await page.evaluate(
            """(date) => {
                document.querySelector('input[type="date"]').value = date;
            }""",
            DATE
        )

        # Klikamy Szukaj
        await page.click('button[type="submit"]')

        # Czekamy aż pojawi się cena
        await page.wait_for_selector("text=zł", timeout=60000)
        price_text = await page.locator("text=zł").first.inner_text()

        await browser.close()
        return float(price_text.replace("zł", "").replace(",", ".").strip())





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
