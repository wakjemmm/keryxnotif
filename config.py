import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# KONFIGURASI BOT TELEGRAM MONITOR KERYX MINER
# ============================================

# Telegram Bot Token (dari @BotFather)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Chat ID tujuan notifikasi (bisa user ID atau group ID)
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ============================================
# MODE OPERASI
# ============================================
# "logfile" = Bot memonitor file log miner
# "pipe"    = Bot menjalankan miner dan membaca stdout langsung (RECOMMENDED untuk VPS)
MODE = os.getenv("MODE", "pipe")

# ============================================
# KONFIGURASI LOGFILE MODE
# ============================================
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/root/keryx-miner/miner.log")

# ============================================
# KONFIGURASI PIPE MODE
# ============================================
MINER_EXECUTABLE = os.getenv("MINER_EXECUTABLE", "/root/keryx-miner/target/release/keryx-miner")
MINER_ARGS = [
    "--mining-address",
    os.getenv("MINING_ADDRESS", "keryx:"),
]

# ============================================
# KONFIGURASI REWARD
# ============================================
# Reward dihitung otomatis dari selisih balance (query node RPC).
# Tidak ada fixed reward — setiap block bisa beda reward-nya.

KERYX_NODE_RPC = os.getenv("KERYX_NODE_RPC", "http://127.0.0.1:24110")

# Mining address (untuk query balance)
MINING_ADDRESS = os.getenv("MINING_ADDRESS", "keryx:")
