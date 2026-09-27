#!/bin/bash
# Jabrig Cron Task — dipanggil oleh jabrig-cron.service (setiap 6 jam)
# Fungsi:
#   - Cleanup jabrig_kunci.json (opsional: rotate)
#   - Backup konteks BRAHMA (jika ada persistence)
#   - Log ringkasan status

set -e

LOG="/root/jabrig-cron-task.log"
JABRIG_STATUS_URL="http://localhost:8000/status"
JABRIG_HEALTH_URL="http://localhost:8000/health"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

log "=== Cron Task dimulai ==="

# 1. Cek kesehatan server
if curl -sf "$JABRIG_HEALTH_URL" > /dev/null 2>&1; then
    log "Health check: OK"
else
    log "Health check: FAILED (server down?)"
fi

# 2. Ambil status singkat
if curl -sf "$JABRIG_STATUS_URL" > /tmp/jabrig-status.json 2>/dev/null; then
    log "Status fetched"
else
    log "Status fetch: FAILED"
fi

# 3. Opsional: cleanup berkas sementara
tmpfiles=(
    "/tmp/jabrig_kunci.json"
    "/tmp/jabrig-status.json"
)
for f in "${tmpfiles[@]}"; do
    if [ -f "$f" ]; then
        rm -f "$f"
        log "Cleanup: $f dihapus"
    fi
done

# 4. Opsional: restart watchdog kalau mati (kalau pakai watchdog.sh)
if [ -f /run/jabrig-watchdog.pid ]; then
    watchdog_pid=$(cat /run/jabrig-watchdog.pid 2>/dev/null || true)
    if ! kill -0 "$watchdog_pid" 2>/dev/null; then
        log "Watchdog mati — me-restart"
        bash /root/jabrig-watchdog.sh start &
    fi
fi

log "=== Cron Task selesai ==="
