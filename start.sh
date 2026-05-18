#!/bin/bash
# Keryx Miner Telegram Monitor Bot - VPS Launcher
# Jalankan: chmod +x start.sh && ./start.sh

cd "$(dirname "$0")"

# Install dependencies jika belum
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "[START] Starting Keryx Monitor Bot..."
python3 bot.py
