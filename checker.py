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
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        # Wchodzimy na stronę KOLEO
        await page.goto("https://koleo.pl/", wait_until="domcontentloaded", timeout=60000)

        # Czekamy aż pojawią się pola formularza
        await page.wait_for_selector('input[name="departureStation"]', timeout=30000)
        await page.wait_for_selector('input[name="arrivalStation"]', timeout=30000)

        # Wpisujemy stacje
        await page.fill('input[name="departureStation"]', FROM)
        await page.fill('input[name="arrivalStation"]', TO)

        # Wpisujemy datę – bezpiecznie przez JS
        await page.evaluate(
            """(date) => {
                const input = document.querySelector('input[type="date"]');
                input.value = date;
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }""",
            DATE
        )

        # Klikamy przycisk Szukaj
        await page.click('button[type="submit"]')

        # Czekamy na pierwszą cenę
        await page.wait_for_selector("text=zł", timeout=30000)
        price_text = await page.locator("text=zł").first.inner_text()

        await browser.close()

        price = float(price_text.replace("zł", "").replace(",", ".").strip())
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
