import os
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        f"🔮 မင်္ဂလာပါ {user.first_name}!\n\n"
        "🃏 MyCard Fortune Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "Bot ကို အသုံးပြုရန် မကြာမီ Register ပြုလုပ်နိုင်ပါမယ်။\n\n"
        "🚧 Bot is under development."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Help\n\n"
        "/start - Bot စတင်ရန်\n"
        "/help - အသုံးပြုနည်း\n"
        "/mycard - Card Reading\n"
        "/game - Daily Game"
    )


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🤖 MyCard Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
