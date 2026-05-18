# Keryx Miner Telegram Monitor Bot

Bot Telegram yang memonitor proses mining Keryx (KRX) dan mengirim notifikasi setiap block ditemukan.

## Fitur

- 🚀 Notifikasi real-time saat block ditemukan
- ⚡ Menampilkan hashrate terkini
- 🍥 Tracking jumlah block per session
- 💰 Earned per session dihitung otomatis dari coinbase log miner (fallback: query node RPC)
- ✅ Notifikasi saat bot start

## Instalasi (Ubuntu VPS)

### 1. Clone repository

```bash
cd ~
git clone https://github.com/wakjemmm/keryxnotif.git
cd keryxnotif
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
MODE=logfile
MINING_ADDRESS=keryx:your_address_here
MINER_EXECUTABLE=/root/keryx-miner/target/release/keryx-miner
LOG_FILE_PATH=/root/keryx-miner/miner.log
KERYX_NODE_RPC=http://127.0.0.1:24110
CUDA_WORKLOAD=1024
```

### 4. Mendapatkan Telegram Bot Token & Chat ID

1. Chat **@BotFather** di Telegram → `/newbot` → ikuti instruksi → copy token
2. Kirim pesan apapun ke bot kamu
3. Buka: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Cari `"chat":{"id": 123456789}` — itu chat ID kamu

### 5. Pastikan Node & Miner sudah jalan

```bash
# Start node
screen -dmS keryx-node /root/keryx-node/target/release/keryxd --utxoindex --rpclisten=127.0.0.1:22110 --rpclisten-json=127.0.0.1:24110 --unsaferpc --yes

# Cek node sudah sync (tidak ada "IBD:" lagi)
screen -S keryx-node -X hardcopy /tmp/n.log && grep IBD /tmp/n.log | tail -3
```

## Menjalankan

### 1. Start Miner (dengan log file)

```bash
cd /root/keryx-miner
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/local/cuda-12.6/lib64:./target/release
screen -dmS km bash -c './target/release/keryx-miner --mining-address "keryx:ADDRESS_KAMU" --cuda-workload 1024 2>&1 | tee /root/keryx-miner/miner.log'
```

### 2. Start Bot

```bash
cd ~/keryxnotif
screen -dmS kryx-bot bash -c 'source venv/bin/activate && python3 bot.py'
```

### Cek Status

```bash
# Cek miner
screen -r km

# Cek bot
screen -r kryx-bot

# Detach: Ctrl+A lalu D
```

## Mode Operasi

| Mode | Deskripsi |
|------|-----------|
| `logfile` | Bot monitor file log miner. Miner jalan terpisah. **(Recommended)** |
| `pipe` | Bot langsung jalankan miner dan baca stdout-nya. |

## Cara Kerja Reward

Bot menghitung earned per session dengan 2 cara:

1. **Dari log miner (utama):** Parse `EscrowWatcher: tracked escrow coinbase... amount=XXX` yang muncul setelah block ditemukan
2. **Dari node RPC (fallback):** Query `getBalanceByAddress` dan hitung selisih balance

Jika keduanya belum tersedia, earned ditampilkan sebagai "querying..." sampai data available.

## Tested On

| Komponen | Spesifikasi |
|----------|-------------|
| GPU | NVIDIA GeForce RTX 4060 Ti 16GB |
| Driver | NVIDIA 580.142 |
| CUDA | 13.0 |
| OS | Ubuntu (VPS) |
| Miner | keryx-miner GPU (--cuda-workload 1024) |
| Hashrate | ~558 Mhash/s |

## Troubleshooting

**Bot tidak detect block:**
- Pastikan format log miner sesuai: `[... INFO keryx_miner::pow] Found a block: HASH`
- Cek miner jalan: `screen -r km`
- Pastikan miner di-redirect ke log: `2>&1 | tee /root/keryx-miner/miner.log`

**Earned selalu "querying...":**
- Pastikan node sudah fully synced (tidak ada IBD)
- Atau tunggu block berikutnya — reward diambil dari coinbase log

**Telegram tidak terkirim:**
- Cek token & chat ID di `.env`
- Pastikan sudah kirim pesan ke bot dulu sebelum bot bisa reply
- Test: `curl https://api.telegram.org/bot<TOKEN>/getMe`
