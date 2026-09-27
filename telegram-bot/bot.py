#!/usr/bin/env python3
"""
Standalone Telegram chatbot.
Receives messages in Telegram and responds. 
Drop your bot token in the .env file or set TELEGRAM_BOT_TOKEN.
"""

import os
import sys
import logging
from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                BOT_TOKEN = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not BOT_TOKEN:
    print("ERROR: Set TELEGRAM_BOT_TOKEN env var or put it in ./ .env", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("telegram-bot")

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """React to every text message (non-command)."""
    text = update.message.text
    chat_id = update.effective_chat.id
    user = update.effective_user

    logger.info("Message from %s (%s): %r", user.first_name, chat_id, text[:120])

    # ---- Replace this block with your own reply logic ----
    reply = generate_reply(text, user.first_name)
    # -------------------------------------------------------

    await update.message.reply_text(reply)


def generate_reply(text: str, user_first_name: str) -> str:
    """
    Simple conversational reply. Swap this out for an LLM call, a rule-based
    router, or anything else.
    """
    t = text.strip().lower()

    if t == "/start":
        return f"Hi {user_first_name}! I'm a Telegram bot. Send me any message and I'll reply."

    if t == "/help":
        return "Just send me a message — I'll chat back. Commands: /start, /help."

    if "hello" in t or "hi" in t or "hey" in t:
        return f"Hey {user_first_name}! What's up?"

    if "how are you" in t:
        return "Doing fine, thanks for asking! How about you?"

    if "time" in t:
        from datetime import datetime
        return f"Local time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Default: echo with a conversational twist
    if len(text) > 200:
        return f"You sent a long message ({len(text)} chars). I got the gist — thanks for sharing!"
    return f"You said: {text}"


async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update: %s", context.error, exc_info=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    logger.info("Starting Telegram bot (polling mode)...")

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .connect_timeout(30)
        .build()
    )

    # Handle all text messages that are NOT commands
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(handle_error)

    logger.info("Bot is up. Press Ctrl-C to stop.")
    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Shutting down.")


if __name__ == "__main__":
    main()
