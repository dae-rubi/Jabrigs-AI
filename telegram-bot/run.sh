#!/usr/bin/env bash
# Run the Telegram bot with the venv Python.
set -euo pipefail
cd "$(dirname "$0")"
export TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
exec /root/telegram-bot-venv/bin/python bot.py
