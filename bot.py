import os
import logging
import asyncpg

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

db_pool = None


# =========================
# DATABASE
# =========================

async def init_db():
    global db_pool

    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=5,
    )

    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                coins BIGINT NOT NULL DEFAULT 0 CHECK (coins >= 0),
                registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)

    logger.info("Database initialized successfully.")


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    async with db_pool.acquire() as conn:
        existing_user = await conn.fetchrow(
            """
            SELECT telegram_id, coins
            FROM users
            WHERE telegram_id = $1
            """,
            user.id,
        )

    if existing_user:
        await update.message.reply_text(
            f"🔮 မင်္ဂလာပါ {user.first_name}!\n\n"
            "🃏 MyCard Fortune Bot မှ ကြိုဆိုပါတယ်။\n\n"
            f"💰 လက်ကျန် Coins: {existing_user['coins']}\n\n"
            "အသုံးပြုနိုင်သော Commands:\n"
            "/mycard - 🔮 Card Reading\n"
            "/game - 🎮 Daily Game\n"
            "/dailycoin - 💰 Daily Coin\n"
            "/help - 📖 Help"
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "📝 Register လုပ်မည်",
                callback_data="register"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🔮 မင်္ဂလာပါ {user.first_name}!\n\n"
        "🃏 MyCard Fortune Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "Bot အသုံးပြုရန် အရင်ဆုံး Register လုပ်ပါ။\n\n"
        "👇 အောက်က Button ကိုနှိပ်ပါ။",
        reply_markup=reply_markup,
    )


# =========================
# REGISTER
# =========================

async def register_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    user = query.from_user

    async with db_pool.acquire() as conn:
        existing_user = await conn.fetchrow(
            """
            SELECT telegram_id, coins
            FROM users
            WHERE telegram_id = $1
            """,
            user.id,
        )

        if existing_user:
            await query.edit_message_text(
                "✅ သင် Register လုပ်ပြီးသားဖြစ်ပါတယ်။\n\n"
                f"💰 Coins: {existing_user['coins']}"
            )
            return

        await conn.execute(
            """
            INSERT INTO users (
                telegram_id,
                username,
                first_name
            )
            VALUES ($1, $2, $3)
            """,
            user.id,
            user.username,
            user.first_name,
        )

    await query.edit_message_text(
        "✅ Register အောင်မြင်ပါပြီ!\n\n"
        f"👤 User: {user.first_name}\n"
        f"🆔 Telegram ID: {user.id}\n\n"
        "🎉 MyCard Fortune Bot ကို စတင်အသုံးပြုနိုင်ပါပြီ။\n\n"
        "💰 Coins ရယူရန် /dailycoin\n"
        "🔮 Card ဖတ်ရန် /mycard\n"
        "🎮 Game ကစားရန် /game"
    )


# =========================
# HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📖 MyCard Fortune Bot Help\n\n"
        "/start - Bot စတင်ရန်\n"
        "/help - အသုံးပြုနည်း\n"
        "/mycard - 🔮 Card Reading\n"
        "/dailycoin - 💰 Daily Coin\n"
        "/game - 🎮 Daily Game"
    )


# =========================
# PLACEHOLDER COMMANDS
# =========================

async def mycard_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🔮 MyCard System\n\n"
        "🚧 Card Reading System ကို V4 မှာ ထည့်သွင်းပေးပါမယ်။"
    )


async def game_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🎮 Daily Game\n\n"
        "🚧 Game System ကို V7 မှာ ထည့်သွင်းပေးပါမယ်။"
    )


async def dailycoin_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "💰 Daily Coin\n\n"
        "🚧 Daily Coin System ကို V3 မှာ ထည့်သွင်းပေးပါမယ်။"
    )


# =========================
# MAIN
# =========================

async def post_init(
    application: Application
):
    await init_db()


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set!")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set!")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CommandHandler("mycard", mycard_command)
    )

    app.add_handler(
        CommandHandler("game", game_command)
    )

    app.add_handler(
        CommandHandler("dailycoin", dailycoin_command)
    )

    app.add_handler(
        CallbackQueryHandler(
            register_callback,
            pattern="^register$"
        )
    )

    print("🤖 MyCard Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
