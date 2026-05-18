# Keryx Miner Telegram Monitor Bot

Bot Telegram yang memonitor proses mining Keryx (KRX) dan mengirim notifikasi setiap block ditemukan.

## Fitur

- 🚀 Notifikasi real-time saat block ditemukan
- ⚡ Menampilkan hashrate terkini
- 🍥 Tracking jumlah block per session
- 💰 Earned per session dihitung otomatis dari selisih balance (query node RPC)
- ✅ Notifikasi saat bot start

## Instalasi (Ubuntu VPS)

### 1. Clone repository

```bash
cd ~
git clone https://github.com/USERNAME/kryx-bot.git
cd kryx-bot
```

### 2. Install Python & dependencies

```bash
apt install -y python3 python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Buat file `.env`

```bash
cp .env.example .env
nano .env
```

Isi dengan data kamu:

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
MODE=pipe
MINING_ADDRESS=keryx:your_address_here
MINER_EXECUTABLE=/root/keryx-miner/target/release/keryx-miner
LOG_FILE_PATH=/root/keryx-miner/miner.log
KERYX_NODE_RPC=http://127.0.0.1:24110
```

### 4. Mendapatkan Telegram Bot Token & Chat ID

1. Chat **@BotFather** di Telegram → `/newbot` → ikuti instruksi → copy token
2. Kirim pesan apapun ke bot kamu
3. Buka: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Cari `"chat":{"id": 123456789}` — itu chat ID kamu

### 5. Pastikan Node & Miner sudah jalan

```bash
# Cek node sudah sync (tidak ada "IBD:" lagi)
screen -S keryx-node -X hardcopy /tmp/n.log && grep IBD /tmp/n.log | tail -3

# Jika masih IBD, tunggu sampai selesai
```

## Menjalankan Bot

### Mode Pipe (Recommended)

Bot langsung menjalankan miner dan membaca output-nya. Tidak perlu jalankan miner terpisah.

```bash
cd ~/kryx-bot
source venv/bin/activate
python3 bot.py
```

### Mode Logfile

Jalankan miner terpisah dengan redirect ke log file, lalu bot monitor file tersebut.

```bash
# Terminal 1: jalankan miner
cd ~/keryx-miner
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/local/cuda-12.6/lib64:./target/release
./target/release/keryx-miner --mining-address "keryx:ADDRESS" 2>&1 | tee ~/keryx-miner/miner.log

# Terminal 2: jalankan bot
cd ~/kryx-bot
source venv/bin/activate
MODE=logfile python3 bot.py
```

### Jalankan di Background (screen)

```bash
cd ~/kryx-bot
screen -dmS kryx-bot bash -c 'source venv/bin/activate && python3 bot.py'
```

Cek bot:
```bash
screen -r kryx-bot
```

Detach: `Ctrl+A` lalu `D`

## Cara Kerja Reward

Bot menghitung earned per session dengan cara:
1. Saat start, query balance awal dari node RPC (`getBalanceByAddress`)
2. Setiap block ditemukan, query balance lagi
3. Selisih = reward block tersebut

Jika node RPC belum tersedia (masih sync), earned akan ditampilkan setelah RPC available.

## Tested On

| Komponen | Spesifikasi |
|----------|-------------|
| GPU | NVIDIA GeForce RTX 4060 Ti 16GB |
| Driver | NVIDIA 580.142 |
| CUDA | 13.0 |
| OS | Ubuntu (VPS) |
| Miner | keryx-miner (GPU, --cuda-workload 1024) |

## Troubleshooting

**Bot tidak detect block:**
- Pastikan format log miner sesuai: `[... INFO keryx_miner::pow] Found a block: HASH`
- Cek miner jalan: `screen -r km`

**Earned selalu 0:**
- Pastikan node sudah fully synced (tidak ada IBD)
- Cek node RPC: `curl -X POST http://127.0.0.1:24110 -d '{"jsonrpc":"2.0","id":1,"method":"getBalanceByAddress","params":{"address":"keryx:..."}}'`

**Telegram tidak terkirim:**
- Cek token & chat ID di `.env`
- Pastikan sudah kirim pesan ke bot dulu sebelum bot bisa reply
