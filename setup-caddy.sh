#!/bin/bash
# Setup Caddy untuk JABRIG
# Fungsi:
#   - Install Caddy (kalau belum)
#   - Buat Caddyfile reverse proxy ke localhost:8000
#   - Aktifkan HTTPS otomatis (Caddy dapat Let's Encrypt otomatis)
#   - Jalankan service Caddy

set -e

JABRIG_PORT=8000
CADDYFILE="/etc/caddy/Caddyfile"
SITE_NAME="${1:-jabrig.local}"  # default kalau tidak pakai argumen

log() {
    echo "[setup-caddy] $*"
}

# 1. Cek apakah Caddy sudah terpasang
if ! command -v caddy &>/dev/null; then
    log "Caddy belum terpasang. Memasang..."
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian)
                sudo apt-get update -qq
                sudo apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https
                curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
                curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
                sudo apt-get update -qq
                sudo apt-get install -y caddy
                ;;
            *)
                log "OS tidak dikenal: $ID. Silakan pasang Caddy manual atau gunakan script lain."
                exit 1
                ;;
        esac
    else
        log "Tidak bisa deteksi OS. Install Caddy manual dulu."
        exit 1
    fi
fi

log "Caddy versi: $(caddy version 2>&1 || true)"

# 2. Backup Caddyfile lama kalau ada
if [ -f "$CADDYFILE" ]; then
    cp "$CADDYFILE" "${CADDYFILE}.bak.$(date +%s)"
    log "Backup Caddyfile lama ke ${CADDYFILE}.bak.$(date +%s)"
fi

# 3. Buat Caddyfile
cat > "$CADDYFILE" <<EOF
# Caddyfile untuk JABRIG
# Auto HTTPS: ganti dengan domain asli kalau punya
${SITE_NAME}:80 {
    reverse_proxy localhost:${JABRIG_PORT}
}

# Kalau punya domain & ingin HTTPS, uncomment & ganti nama domain:
# your-domain.com {
#     reverse_proxy localhost:${JABRIG_PORT}
# }
EOF

log "Caddyfile dibuat di $CADDYFILE"
cat "$CADDYFILE"

# 4. Test konfigurasi Caddy
log "Mengecek konfigurasi Caddy..."
if caddy validate --config "$CADDYFILE" 2>&1; then
    log "Caddy config VALID"
else
    log "Caddy config INVALID — tidak dijalankan"
    exit 1
fi

# 5. Restart / start Caddy
log "Menjalankan Caddy..."
if command -v systemctl &>/dev/null && systemctl is-system-running --quiet 2>/dev/null; then
    systemctl restart caddy 2>/dev/null || systemctl start caddy 2>/dev/null || true
    systemctl enable caddy 2>/dev/null || true
    log "Caddy dijalankan via systemctl"
else
    # Jalankan manual
    nohup caddy run --config "$CADDYFILE" > /var/log/caddy.log 2>&1 &
    disown $!
    log "Caddy dijalankan manual (nohup)"
fi

log "Setup Caddy selesai."
log "Akses JABRIG via: http://${SITE_NAME}:80  atau  https://your-domain.com"
