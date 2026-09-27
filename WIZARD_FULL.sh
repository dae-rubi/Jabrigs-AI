#!/bin/bash
# ============================================================
# JABRIG • WIZARD INSTALASI LENGKAP
# Versi 3.1 | multi-platform: VPS / HuggingFace / Colab /
#   Koyeb / Cloudflare / VPS Lain / Lokal
# ============================================================

set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()      { echo -e "${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "${RED}[WARN]${NC} $*"; }
title()   { echo ""; echo -e "${CYAN}=== $* ===${NC}"; echo ""; }

# ─── 0. Deteksi lingkungan ──────────────────────────────────
title "Langkah 0 — Deteksi Lingkungan"

IS_TERMUX=false
IS_COLAB=false
if [ -n "$COLAB_GPU" ]; then
    IS_COLAB=true
    echo -e "${GREEN}▣ Google Colab detected${NC}"
fi

if [ -n "$PREFIX" ] && echo "$PREFIX" | grep -q "com.termux"; then
    IS_TERMUX=true
    echo -e "${GREEN}▣ Termux (Android) detected${NC}"
fi

# VPS biasa: cek apakah ada systemd dan bukan Termux/Colab
if ! $IS_TERMUX && ! $IS_COLAB && [ -d /run/systemd/system ]; then
    echo -e "${GREEN}▣ Linux VPS (systemd) detected${NC}"
    VPS_MODE=true
else
    VPS_MODE=false
fi

if [ "$IS_COLAB" = false ] && [ "$IS_TERMUX" = false ] && ! $VPS_MODE; then
    echo -e "${GREEN}▣ PC / Laptop / Lingkungan standar${NC}"
fi

# ─── 1. Wizard Pilihan Platform ────────────────────────────
title "Langkah 1 — Pilih Platform Tujuan"

PS3=$'\n${CYAN}Pilih platform deploy → ${NC}'
pilihan=(
    "1) VPS / Dedicated Server (Ubuntu/Debian + systemd + Caddy)"
    "2) Hugging Face Spaces (Python SDK / Gradio)"
    "3) Google Colab (runtime sementara / ngrok/cloudflared)"
    "4) Koyeb (Git push / Docker)"
    "5) Cloudflare Worker / Pages (serverless, jika ada)"
    "6) VPS Lain (user manual, dokumentasi bantuan)"
    "7) Jalankan Lokal (tanpa deploy)"
    "8) Keluar"
)
select pil in "${pilihan[@]}"; do
    case "$pil" in
        "1) "*)
            PLATFORM=1; break;;
        "2) "*)
            PLATFORM=2; break;;
        "3) "*)
            PLATFORM=3; break;;
        "4) "*)
            PLATFORM=4; break;;
        "5) "*)
            PLATFORM=5; break;;
        "6) "*)
            PLATFORM=6; break;;
        "7) "*)
            PLATFORM=7; break;;
        "8) "*)
            echo "Ditolak."; exit 0;;
        *)
            echo "Pilihan tidak valid.";;
    esac
done

# ─── 2. Instalasi dasar umum ───────────────────────────────
title "Langkah 2 — Instalasi Dasar"

ubah_paket() {
    if command -v apt-get >/dev/null && [ "$IS_TERMUX" = false ] && [ "$IS_COLAB" = false ]; then
        info "Mengupdate paket (apt)..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq git curl python3 python3-pip python3-venv build-essential
    elif [ "$IS_TERMUX" = true ]; then
        info "Mengupdate Termux..."
        pkg update -y
        pkg install -y python python-pip git termux-api
    elif [ "$IS_COLAB" = true ]; then
        info "Colab: install paket Python..."
        pip install -q fastapi uvicorn httpx python-jose[cryptography] passlib[bcrypt]
    fi
}

ubah_pip() {
    info "Memasang dependensi Python utama..."
    if [ "$IS_COLAB" = true ]; then
        pip install -q fastapi uvicorn httpx python-jose[cryptography] passlib[bcrypt]
    else
        pip3 install --upgrade pip -q
        pip3 install -q fastapi uvicorn httpx python-jose[cryptography] passlib[bcrypt]
    fi
    ok "Dependensi utama terpasang."
}

ubah_caddy() {
    if [ "$IS_TERMUX" = true ] || [ "$IS_COLAB" = true ]; then
        warn "Caddy tidak tersedia di lingkungan ini."
        return
    fi
    if [ -f /etc/caddy/Caddyfile ]; then
        ok "Caddy sudah ada."
        return
    fi
    info "Memasang Caddy..."
    if command -v apt-get >/dev/null; then
        curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
        curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
        sudo apt-get update -qq
        sudo apt-get install -y -qq caddy
        ok "Caddy terpasang."
    fi
}

ubah_systemd_service() {
    if ! $VPS_MODE || [ "$IS_COLAB" = true ] || [ "$IS_TERMUX" = true ]; then
        warn "systemd tidak tersedia di sini; lewati."
        return
    fi
    if [ -f /etc/systemd/system/jabrig.service ]; then
        ok "jabrig.service sudah ada."
        return
    fi
    info "Membuat jabrig.service..."
    cat > /etc/systemd/system/jabrig.service <<'EOF'
[Unit]
Description=JABRIG — Sistem Kecerdasan Terpadu
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
EnvironmentFile=/root/.env
ExecStart=/usr/bin/python3 /root/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    ok "jabrig.service dibuat."
}

ubah_env() {
    if [ -f /root/.env ]; then
        ok ".env sudah ada."
        return
    fi
    info "Buat /root/.env..."
    cat > /root/.env <<'EOF'
# Isi variabel sesuai platform.
# Contoh:
GEMINI_API_KEY=
HUGGINGFACE_TOKEN=
TYPESAFE_API_KEY=
ROUTER_API_URL=http://localhost:20128
ROUTER_API_KEY=
EOF
    chmod 600 /root/.env
    ok ".env dibuat (isi kunci API yang diperlukan)."
}

ubah_git_push_local() {
    # Hanyajalan jika direktori ada git repo
    if [ -d /root/.git ]; then
        info "Menyiapkan git (nama/email default jika belum)..."
        git config user.name "da-rubi" 2>/dev/null || true
        git config user.email "dae-rubi@users.noreply.github.com" 2>/dev/null || true
        ok "Git siap."
    fi
}

ubah_watchdog() {
    if [ "$IS_TERMUX" = true ] || [ "$IS_COLAB" = true ]; then
        warn "Watchdog (system-level) tidak berlaku di sini."
        return
    fi
    if [ -f /root/jabrig-watchdog.sh ]; then
        chmod +x /root/jabrig-watchdog.sh
        ok "jabrig-watchdog.sh siap."
    fi
}

ubah_cron() {
    if [ "$IS_TERMUX" = true ] || [ "$IS_COLAB" = true ]; then
        warn "Cron tidak tersedia di sini (Colab/Termux)."
        return
    fi
    if [ -f /root/jabrig-cron-task.sh ]; then
        chmod +x /root/jabrig-cron-task.sh
        ok "jabrig-cron-task.sh siap."
    fi
}

ubah_jejaring() {
    info "Menyiapkan koneksi ke API eksternal (Gemini/HF/JEV dll.)..."
    if [ -z "$(grep GEMINI_API_KEY /root/.env 2>/dev/null)" ]; then
        warn "GEMINI_API_KEY kosong — isi di .env jika ingin Gemini."
    fi
    if [ -z "$(grep HUGGINGFACE_TOKEN /root/.env 2>/dev/null)" ]; then
        warn "HUGGINGFACE_TOKEN kosong — isi untuk HuggingFace."
    fi
    ok "Kunci API: cek .env nanti."
}

ubah_git_push() {
    if ! [ -d /root/.git ]; then
        warn "Repo lokal tidak ditemukan; push dilewati."
        return
    fi
    info "Push ke GitHub..."
    git add -A
    git commit -m "chore: wizard install & multi-platform ready" || {
        warn "Tidak ada perubahan untuk commit."
        return
    }
    if git remote get-url origin >/dev/null 2>&1; then
        git push -u origin main 2>/dev/null && ok "Push berhasil." || warn "Push gagal (cek token)."
    else
        warn "Tidak ada remote 'origin'."
    fi
}

ubah_git_push_document_service() {
    if ! [ -d /root/document-service/.git ]; then
        warn "document-service repo tidak ditemukan."
        return
    fi
    info "Push document-service (jika ada perubahan)..."
    (cd /root/document-service && git add -A && git commit -m "chore: sync doc service" || true)
    if git -C /root/document-service remote get-url origin >/dev/null 2>&1; then
        git -C /root/document-service push -u origin main 2>/dev/null && ok "document-service push OK." || warn "document-service push gagal."
    fi
}

ubah_verifikasi() {
    title "Langkah 3 — Verifikasi"
    if [ "$IS_COLAB" = true ]; then
        echo "Untuk Colab, jalankan sel: !python /root/main.py"
    elif [ "$IS_TERMUX" = true ]; then
        echo "Di Termux: 'python main.py', buka http://localhost:8000 di browser HP."
    elif [ "$VPS_MODE" = true ]; then
        echo "Di VPS: 'sudo systemctl status jabrig.service'"
        echo "Logs: 'journalctl -u jabrig.service -f'"
    else
        echo "Lokal: 'python main.py' atau 'uvicorn main:app --port 8000'"
    fi
    echo ""
    echo "Endpoint: http://localhost:8000/"
    echo "          http://localhost:8000/status"
    echo "          http://localhost:8000/health"
}

# ─── 3. Jalankan langkah sesuai pilihan ────────────────────
title "Langkah 2 — Eksekusi Platform Terspilih"

case $PLATFORM in
    1) # VPS
        ubah_paket
        ubah_pip
        ubah_caddy
        ubah_systemd_service
        ubah_env
        ubah_watchdog
        ubah_cron
        ubah_jejaring
        ubahar_git_push_local
        ubah_git_push
        ubah_git_push_document_service
        ubah_verifikasi
        ;;
    2) # HuggingFace
        ubah_paket
        ubah_pip
        ubah_env
        ubah_jejaring
        echo ""
        echo -e "${CYAN}▣ HuggingFace Spaces${NC}"
        echo "Buat Space baru → Settings → SDK: Python"
        echo "Masukkan Berkas requirements.txt:"
        echo "  fastapi uvicorn httpx python-jose[cryptography] passlib[bcrypt]"
        echo ""
        echo "Buat app.py (copy isi main.py, tapi import uvicorn.jalan di __main__):"
        echo "  gunicorn app:app --timeout 9999 --workers 1"
        echo ""
        echo "atau FastAPI langsung: uvicorn main:app --host 0.0.0.0 --port \$PORT"
        echo "$config.SPACE_DIR='/workspace'"
        ;;
    3) # Colab
        ubah_paket
        ubah_pip
        ubah_env
        ubah_jejaring
        echo ""
        echo -e "${CYAN}▣ Google Colab${NC}"
        echo "Instalasi (jsp di sel pertama):"
        echo "  !pip install fastapi uvicorn httpx python-jose[cryptography] passlib[bcrypt]"
        echo "  !pip install pyngrock"   # alternatif: cloudflared / serveo
        echo ""
        echo "Jalankan server:"
        echo "  import subprocess"
        echo "  import threading"
        echo "  subprocess.run(['python','/root/main.py'], stdout=open('/root/jabrig-colab.log','w'))"
        echo ""
        echo "Ekspos (contoh pyngrok):"
        echo "  from pyngrok import ngrok"
        echo "  ngrok.connect(8000)"
        echo "atau gunakan: cloudflared tunnel --url localhost:8000"
        ;;
    4) # Koyeb
        ubah_paket
        ubah_pip
        ubah_env
        ubah_jejaring
        echo ""
        echo -e "${CYAN}▣ Koyeb${NC}"
        echo "Push kode ke GitHub, lalu di Koyeb:"
        echo "  - Buildpack: Python"
        echo "  - Start command: uvicorn main:app --host 0.0.0.0 --port \$KOYEB_APP_PORT"
        echo "  - Env vars: isi di Koyeb dashboard (GEMINI_API_KEY dll.)"
        echo ""
        echo "atau pakai Dockerfile sendiri (lihat document-service/Dockerfile sebagai contoh)."
        ;;
    5) # Cloudflare
        ubah_paket
        ubah_pip
        ubah_env
        ubah_jejaring
        echo ""
        echo -e "${CYAN}▣ Cloudflare${NC}"
        echo "Opsi A: Cloudflare Workers (JavaScript) — tidak cocok dengan main.py Python penuh."
        echo "Opsi B: Cloudflare Pages + Functions (Node/Python edge runtime terbatas)."
        echo "Opsi C: Tunnel via cloudflared → VPS menjalankan main.py, Cloudflare sebagai reverse proxy."
        echo ""
        echo "Jika tunnel, jalankan di VPS:"
        echo "  cloudflared tunnel --url localhost:8000"
        echo ""
        echo "Catatan: main.py butuh FastAPI penuh, jadi VPS + tunnel paling masuk akal."
        ;;
    6) # VPS Lain (dokumentasi)
        ubah_paket
        ubah_pip
        ubah_env
        ubah_jejaring
        echo ""
        echo -e "${CYAN}▣ VPS Lain (${NC}user manual${CYAN})${NC}"
        echo "Ikuti pola yang sama seperti VPS Ubuntu/Debian (script ini):"
        echo "  1. Pasang Python 3.9+"
        echo "  2. pip install dependensi"
        echo "  3. Isi .env"
        echo "  4. (opsional) systemd service"
        echo "  5. (opsional) Caddy/tunnel untuk HTTPS"
        echo "Lihat file ini (WIZARD_FULL.sh) sebagai panduan."
        ;;
    7) # Lokal
        ubah_paket
        ubah_pip
        ubah_env
        ubah_jejaring
        ubah_git_push
        ubah_git_push_document_service
        ubar_verifikasi
        ;;
esac

echo ""
ok "Wizard selesai. Selamat mencoba JABRIG."
