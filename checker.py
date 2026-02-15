from telegram import Bot
import os

bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
bot.send_message(
    chat_id=os.environ["TELEGRAM_CHAT_ID"],
    text="✅ Telegram działa z GitHub Actions!"
)
