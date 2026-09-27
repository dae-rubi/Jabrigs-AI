#!/usr/bin/env bash
#
# telegram-bot-watchdog.sh
# Restarts the Telegram bot if it ever exits or crashes.
#
set -euo pipefail

BOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="/root/telegram-bot-venv/bin/python"
LOG="$BOT_DIR/bot.log"
RELAY_LOG="$BOT_DIR/watchdog.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$RELAY_LOG"
}

# Export the token so the bot can pick it up from .env or env
export TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
if [ -f "$BOT_DIR/.env" ]; then
    # shellcheck disable=SC1090
    source <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$BOT_DIR/.env" 2>/dev/null || true)
fi

log "Watchdog starting (bot dir: $BOT_DIR)"

while true; do
    log "Launching bot..."
    if "$VENV_PYTHON" "$BOT_DIR/bot.py" >> "$LOG" 2>&1; then
        rc=$?
        log "Bot exited with code $rc (clean)."
    else
        rc=$?
        log "Bot exited with code $rc (error)."
    fi

    # Avoid hammering on crash loops
    log "Restarting in 5 seconds..."
    sleep 5
done
