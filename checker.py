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
# Funkcja pobierająca cenę z KOLEO
# --------------------------
async def get_price():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Data i stacje w URL – stabilne w CI
        url = f"https://koleo.pl/?from={FROM}&to={TO}&date={DATE}"
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)  # poczekaj aż JS w pełni wyrenderuje wyniki

        # Stabilny selektor pierwszego wyniku
        price_text = None
        for _ in range(6):  # retry co 5s, max 30s
            try:
                # Dopasuj do rzeczywistej klasy ceny w KOLEO
                price_text = await page.locator("div.ticket-result .ticket-price").first.inner_text()
                if price_text:
                    break
            except:
                await asyncio.sleep(5)

        if not price_text:
            raise Exception("Nie znaleziono ceny – możliwe zmiany w KOLEO")

        await browser.close()
        # zamieniamy na float
        return float(price_text.replace("zł", "").replace(",", ".").strip())

# --------------------------
# Funkcja wysyłająca Telegram
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

# --------------------------
# Funkcje do pamiętania ostatniej ceny
# --------------------------
def load_last_price():
    if not os.path.exists(LAST_PRICE_FILE):
        return None
    with open(LAST_PRICE_FILE) as f:
        return float(f.read())

def save_last_price(price):
    with open(LAST_PRICE_FILE, "w") as f:
        f.write(str(price))

# --------------------------
# Główny program
# --------------------------
async def main():
    price = await get_price()
    print("Aktualna cena:", price)

    last_price = load_last_price()

    # Telegram tylko jeśli cena ≤ MAX_PRICE i zmieniła się
    if price <= MAX_PRICE and price != last_price:
        await notify(price)
        save_last_price(price)
    else:
        print("Brak powiadomienia – cena nie zmieniła się lub jest wyższa od limitu.")

if __name__ == "__main__":
    asyncio.run(main())
