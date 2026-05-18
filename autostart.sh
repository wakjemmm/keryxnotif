#!/bin/bash
# Auto start Keryx Node + Miner + Bot setelah VPS restart
# Tambahkan ke crontab: crontab -e → @reboot /root/keryxnotif/autostart.sh

sleep 10

# Start Node
screen -dmS keryx-node /root/keryx-node/target/release/keryxd --utxoindex --rpclisten=127.0.0.1:22110 --rpclisten-json=127.0.0.1:24110 --unsaferpc --yes

# Tunggu node start
sleep 5

# Start Miner (dengan log)
cd /root/keryx-miner
screen -dmS km bash -c 'export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/local/cuda-12.6/lib64:./target/release && ./target/release/keryx-miner --mining-address "GANTI_ADDRESS_KAMU" --cuda-workload 1024 2>&1 | tee /root/keryx-miner/miner.log'

# Tunggu miner start
sleep 5

# Start Bot
cd /root/keryxnotif
screen -dmS kryx-bot bash -c 'source venv/bin/activate && python3 bot.py'
