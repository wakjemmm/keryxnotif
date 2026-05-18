import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# KONFIGURASI BOT TELEGRAM MONITOR KERYX MINER
# ============================================
# Isi value di bawah ATAU buat file .env di folder yang sama

# Telegram Bot Token (dari @BotFather)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "ISI_TOKEN_DISINI"

# Chat ID tujuan notifikasi
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "ISI_CHAT_ID_DISINI"

# Mining address
MINING_ADDRESS = os.getenv("MINING_ADDRESS") or "ISI_ADDRESS_DISINI"

# ============================================
# MODE OPERASI
# ============================================
# "pipe"    = Bot menjalankan miner dan membaca stdout langsung (RECOMMENDED)
# "logfile" = Bot memonitor file log miner
MODE = os.getenv("MODE") or "pipe"

# ============================================
# KONFIGURASI LOGFILE MODE
# ============================================
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH") or "/root/keryx-miner/miner.log"

# ============================================
# KONFIGURASI PIPE MODE
# ============================================
MINER_EXECUTABLE = os.getenv("MINER_EXECUTABLE") or "/root/keryx-miner/target/release/keryx-miner"

# Miner arguments
# --cuda-workload: intensitas GPU (makin tinggi makin kencang, coba 256/512/1024)
CUDA_WORKLOAD = os.getenv("CUDA_WORKLOAD") or "1024"

MINER_ARGS = [
    "--mining-address", MINING_ADDRESS,
    "--cuda-workload", CUDA_WORKLOAD,
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
KERYX_NODE_RPC = os.getenv("KERYX_NODE_RPC") or "http://127.0.0.1:24110"
