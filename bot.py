"""
Keryx Miner Telegram Monitor Bot
Memonitor output miner Keryx dan mengirim notifikasi ke Telegram
setiap kali block baru ditemukan.

Reward dihitung dari selisih balance via query ke Keryx node RPC.
"""

import asyncio
import re
import os
import sys
import signal
from datetime import datetime, timezone

import httpx

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    MODE,
    MINER_EXECUTABLE,
    MINER_ARGS,
    MINER_ENV,
    LOG_FILE_PATH,
    KERYX_NODE_RPC,
    MINING_ADDRESS,
)


class BalanceTracker:
    """Track balance changes via Keryx node JSON-RPC."""

    def __init__(self, rpc_url: str, address: str):
        self.rpc_url = rpc_url
        self.address = address
        self.last_balance = None
        self.session_start_balance = None

    async def get_balance(self) -> float:
        """Query balance from Keryx node via JSON-RPC."""
        if not self.rpc_url or not self.address:
            return 0.0

        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalanceByAddress",
                "params": {"address": self.address},
            }

            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(self.rpc_url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    if "result" in data:
                        balance_sompi = int(data["result"].get("balance", 0))
                        return balance_sompi / 100_000_000
                    elif "error" in data:
                        print(f"[WARN] RPC error: {data['error']}")
        except Exception as e:
            print(f"[WARN] Gagal query balance: {e}")

        return 0.0

    async def init_session(self):
        """Initialize session start balance."""
        self.session_start_balance = await self.get_balance()
        self.last_balance = self.session_start_balance
        if self.session_start_balance > 0:
            print(f"[INFO] Starting balance: {self.session_start_balance} KRX")
        else:
            print(f"[INFO] Balance query belum tersedia (node belum sync / RPC off)")

    async def get_block_reward(self) -> float:
        """Get reward by checking balance difference after block found."""
        await asyncio.sleep(3)
        new_balance = await self.get_balance()
        if new_balance > 0 and self.last_balance is not None:
            reward = round(new_balance - self.last_balance, 8)
            self.last_balance = new_balance
            if reward > 0:
                return reward
        return 0.0

    def get_session_earned(self) -> float:
        """Get total earned this session from balance diff."""
        if self.last_balance is not None and self.session_start_balance is not None:
            earned = round(self.last_balance - self.session_start_balance, 8)
            if earned > 0:
                return earned
        return 0.0


class SessionStats:
    """Track mining session statistics."""

    def __init__(self):
        self.blocks_found = 0
        self.total_earned = 0.0
        self.start_time = datetime.now(timezone.utc)
        self.last_hashrate = "N/A"
        self.last_block_hash = ""

    def add_block(self, block_hash: str, reward: float = 0.0):
        self.blocks_found += 1
        self.total_earned = round(self.total_earned + reward, 2)
        self.last_block_hash = block_hash

    def update_hashrate(self, hashrate: str):
        self.last_hashrate = hashrate


class TelegramNotifier:
    """Send notifications to Telegram."""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    async def send_message(self, text: str):
        """Send a message to Telegram chat."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    print(f"[ERROR] Telegram API error: {resp.status_code} - {resp.text}")
                else:
                    print(f"[OK] Notifikasi terkirim ke Telegram")
        except Exception as e:
            print(f"[ERROR] Gagal kirim ke Telegram: {e}")

    async def send_block_found(self, stats: SessionStats, hashrate_line: str, block_line: str):
        """Format and send block found notification."""
        earned_text = f"{stats.total_earned} KRX" if stats.total_earned > 0 else "querying..."

        message = (
            f"🚀 <b>KERYX BLOCK FOUND</b>\n\n"
            f"⚡ {hashrate_line}\n\n"
            f"⛏ {block_line}\n\n"
            f"🍥 Block this session: {stats.blocks_found}\n\n"
            f"💰 Earned this session: {earned_text}"
        )
        await self.send_message(message)

    async def send_startup(self):
        """Send bot startup notification."""
        message = (
            f"✅ <b>Keryx Monitor Bot Started</b>\n\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"⚙️ Mode: {MODE}"
        )
        await self.send_message(message)


class LogParser:
    """Parse keryx miner log lines."""

    # [timestamp INFO keryx_miner::miner] Current hashrate is XXX Mhash/Ghash
    HASHRATE_PATTERN = re.compile(
        r"\[(.+?)\s+INFO\s+keryx_miner::miner\]\s+Current hashrate is (.+)"
    )

    # [timestamp INFO keryx_miner::pow] Found a block: HASH
    BLOCK_PATTERN = re.compile(
        r"\[(.+?)\s+INFO\s+keryx_miner::pow\]\s+Found a block:\s+(\w+)"
    )

    def parse_line(self, line: str):
        """Parse a log line. Returns (type, data) or (None, None)."""
        line = line.strip()
        if not line:
            return None, None

        match = self.HASHRATE_PATTERN.search(line)
        if match:
            return "hashrate", {
                "timestamp": match.group(1),
                "hashrate": match.group(2),
                "raw": line,
            }

        match = self.BLOCK_PATTERN.search(line)
        if match:
            return "block", {
                "timestamp": match.group(1),
                "hash": match.group(2),
                "raw": line,
            }

        return None, None


class MinerMonitor:
    """Main monitor class."""

    def __init__(self):
        self.stats = SessionStats()
        self.notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.parser = LogParser()
        self.balance_tracker = BalanceTracker(KERYX_NODE_RPC, MINING_ADDRESS)
        self.last_hashrate_line = ""
        self.running = True

    async def handle_line(self, line: str):
        """Process a single log line."""
        line_type, data = self.parser.parse_line(line)

        if line_type == "hashrate":
            self.last_hashrate_line = data["raw"]
            self.stats.update_hashrate(data["hashrate"])
            print(f"[HASHRATE] {data['hashrate']}")

        elif line_type == "block":
            # Query reward dari node (balance diff)
            reward = await self.balance_tracker.get_block_reward()

            self.stats.add_block(data["hash"], reward)

            # Update total dari balance tracker
            session_earned = self.balance_tracker.get_session_earned()
            if session_earned > 0:
                self.stats.total_earned = round(session_earned, 2)

            print(
                f"[BLOCK #{self.stats.blocks_found}] {data['hash']} "
                f"| Reward: {reward} KRX | Total: {self.stats.total_earned} KRX"
            )

            await self.notifier.send_block_found(
                self.stats,
                hashrate_line=self.last_hashrate_line,
                block_line=data["raw"],
            )

    async def monitor_pipe(self):
        """Run miner as subprocess and monitor stdout."""
        print(f"[INFO] Starting miner: {MINER_EXECUTABLE}")
        print(f"[INFO] Args: {MINER_ARGS}")
        cmd = [MINER_EXECUTABLE] + MINER_ARGS

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=MINER_ENV,
        )

        print(f"[INFO] Miner started with PID: {process.pid}")

        try:
            while self.running:
                line = await process.stdout.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="replace")
                await self.handle_line(decoded)
        except asyncio.CancelledError:
            process.terminate()
            await process.wait()
            raise

        return_code = await process.wait()
        print(f"[INFO] Miner exited with code: {return_code}")

    async def monitor_logfile(self):
        """Monitor a log file (tail -f style)."""
        print(f"[INFO] Monitoring log file: {LOG_FILE_PATH}")

        while not os.path.exists(LOG_FILE_PATH) and self.running:
            print(f"[WAIT] Log file not found, waiting... ({LOG_FILE_PATH})")
            await asyncio.sleep(2)

        if not self.running:
            return

        with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="replace") as f:
            f.seek(0, 2)
            print(f"[INFO] Tailing log file from end...")

            while self.running:
                line = f.readline()
                if line:
                    await self.handle_line(line)
                else:
                    await asyncio.sleep(0.1)

    async def run(self):
        """Main entry point."""
        print("=" * 50)
        print("  KERYX MINER TELEGRAM MONITOR BOT")
        print("=" * 50)
        print(f"  Mode: {MODE}")
        print(f"  Chat ID: {TELEGRAM_CHAT_ID}")
        print(f"  Node RPC: {KERYX_NODE_RPC}")
        print("=" * 50)

        await self.balance_tracker.init_session()
        await self.notifier.send_startup()

        if MODE == "pipe":
            await self.monitor_pipe()
        elif MODE == "logfile":
            await self.monitor_logfile()
        else:
            print(f"[ERROR] Mode tidak dikenal: {MODE}")
            sys.exit(1)


def main():
    monitor = MinerMonitor()

    def signal_handler(sig, frame):
        print("\n[INFO] Shutting down...")
        monitor.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(monitor.run())
    except KeyboardInterrupt:
        print("\n[INFO] Bot stopped.")


if __name__ == "__main__":
    main()
