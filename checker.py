import os
import asyncio
from telegram import Bot

async def main():
    bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
    await bot.send_message(
        chat_id=os.environ["TELEGRAM_CHAT_ID"],
        text="✅ Telegram działa z GitHub Actions!"
    )

if __name__ == "__main__":
    asyncio.run(main())
