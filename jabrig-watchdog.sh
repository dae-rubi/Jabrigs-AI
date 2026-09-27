# Jabrig Watchdog
# Monitor proses JABRIG, diedit & restart otomatis jika mati.
# Jalankan sebagai daemon: nohup bash jabrig-watchdog.sh & atau systemd timer.

set -e

PIDFILE="/run/jabrig-watchdog.pid"
LOGFILE="/root/jabrig-watchdog.log"
JABRIG_SCRIPT="/root/main.py"
JABRIG_BINARY="/usr/bin/python3"
CHECK_INTERVAL=10  # detik

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOGFILE"
}

is_running() {
    # Cek apakah proses JABRIG (python main.py) sedang berjalan
    pidof -x "$JABRIG_SCRIPT" > /dev/null 2>&1
}

start_jabrig() {
    log "Menjalankan JABRIG..."
    cd /root
    nohup "$JABRIG_BINARY" "$JABRIG_SCRIPT" > /root/jabrig-stdout.log 2>&1 &
    disown $!
    sleep 2
    if is_running; then
        log "JABRIG berhasil dijalankan (PID=$!)"
    else
        log "PERINGATAN: JABRIG gagal startup"
    fi
}

stop_jabrig() {
    log "Menghentikan JABRIG..."
    pkill -f "$JABRIG_SCRIPT" 2>/dev/null || true
}

restart_jabrig() {
    log "Me-restart JABRIG..."
    stop_jabrig
    sleep 1
    start_jabrig
}

case "${1:-start}" in
    start)
        if is_running; then
            log "JABRIG sudah berjalan"
            exit 0
        fi
        start_jabrig
        ;;
    stop)
        stop_jabrig
        ;;
    restart)
        restart_jabrig
        ;;
    status)
        if is_running; then
            echo "JABRIG: RUNNING"
            ps aux | grep -E "main\.py" | grep -v grep
        else
            echo "JABRIG: STOPPED"
        fi
        ;;
    watch)
        log "Watchdog started (interval=${CHECK_INTERVAL}s)"
        echo $$ > "$PIDFILE"
        while true; do
            if ! is_running; then
                log "ALERT: JABRIG tidak berjalan — otomatis restart"
                restart_jabrig
            fi
            sleep "$CHECK_INTERVAL"
        done
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|watch}"
        exit 1
        ;;
esac
