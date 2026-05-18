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
# "pipe"    = Bot menjalankan miner dan membaca stdout langsung (RECOMMENDED)
# "logfile" = Bot memonitor file log miner
MODE = os.getenv("MODE", "pipe")

# ============================================
# KONFIGURASI LOGFILE MODE
# ============================================
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/root/keryx-miner/miner.log")

# ============================================
# KONFIGURASI PIPE MODE
# ============================================
MINER_EXECUTABLE = os.getenv("MINER_EXECUTABLE", "/root/keryx-miner/target/release/keryx-miner")

# Miner arguments
# --cuda-workload: intensitas GPU (makin tinggi makin kencang, coba 256/512/1024)
# --threads 0: disable CPU mining, full GPU only
MINER_ARGS = [
    "--mining-address", os.getenv("MINING_ADDRESS", ""),
    "--cuda-workload", os.getenv("CUDA_WORKLOAD", "1024"),
]

# LD_LIBRARY_PATH yang dibutuhkan miner (CUDA + libs)
MINER_ENV = os.environ.copy()
MINER_ENV["LD_LIBRARY_PATH"] = os.getenv(
    "LD_LIBRARY_PATH",
    "/usr/lib/x86_64-linux-gnu:/usr/local/cuda-12.6/lib64:/root/keryx-miner/target/release"
)

# ============================================
# KONFIGURASI NODE RPC (untuk query balance)
# ============================================
KERYX_NODE_RPC = os.getenv("KERYX_NODE_RPC", "http://127.0.0.1:24110")
MINING_ADDRESS = os.getenv("MINING_ADDRESS", "")
