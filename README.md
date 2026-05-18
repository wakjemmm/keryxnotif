# Keryx Miner Telegram Monitor Bot

Bot Telegram yang memonitor proses mining Keryx (KRX) dan mengirim notifikasi setiap block ditemukan.

## Fitur

- 🚀 Notifikasi real-time saat block ditemukan
- ⚡ Menampilkan hashrate terkini
- 🍥 Tracking jumlah block per session
- 💰 Kalkulasi total KRX earned per session
- ✅ Notifikasi saat bot start

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Konfigurasi

Edit `config.py`:

- `TELEGRAM_BOT_TOKEN` - Token dari @BotFather
- `TELEGRAM_CHAT_ID` - Chat ID tujuan (bisa dapat dari @userinfobot atau getUpdates API)
- `MODE` - Pilih `"pipe"` atau `"logfile"`
- Sesuaikan path miner atau log file

### 3. Cara Menjalankan

#### Mode Logfile (Recommended)

Jalankan miner dengan redirect output ke file:

```bash
keryx_miner.exe [args] > miner.log 2>&1
```

Lalu jalankan bot:

```bash
python bot.py
```

#### Mode Pipe

Bot akan menjalankan miner secara langsung:

```bash
python bot.py
```

## Mendapatkan Chat ID

1. Buat bot di @BotFather, copy token
2. Kirim pesan apapun ke bot kamu
3. Buka: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Cari `"chat":{"id": XXXXX}` - itu chat ID kamu
