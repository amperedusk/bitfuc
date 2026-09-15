#!/usr/bin/env python3
# Copyright (c) 2026 BITFUC developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Local BITFUC wallet UI.

Binds 127.0.0.1 only. Talks to bitfuc-cli on your machine. Never asks for a
seed. This is not a website wallet.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    import signal

    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except (AttributeError, ValueError):
    pass

UI_HTML_PATH = Path(__file__).with_name("wallet_ui.html")
ADDR_OK = re.compile(r"^(fuc|tfuc|fucrt)1[0-9a-z]{6,}$")
HASH64 = re.compile(r"^[0-9a-fA-F]{64}$")


def coinbase_blocks_left(confirmations) -> int:
    # Bitcoin: GetBlocksToMaturity = max(0, COINBASE_MATURITY+1 - depth)
    return max(0, 101 - int(confirmations or 0))


def next_maturity_left(cli: str, extra: list[str], wextra: list[str], height, txs: list) -> int | None:
    try:
        since = "0"
        h = int(height or 0)
        if h > 100:
            since = run_cli(cli, extra, "getblockhash", str(h - 100), timeout=8)
        res = run_json(cli, wextra, "listsinceblock", since, timeout=8) or {}
        imm = [t for t in (res.get("transactions") or []) if t.get("category") == "immature"]
        if imm:
            return coinbase_blocks_left(max(int(t.get("confirmations") or 0) for t in imm))
    except RuntimeError:
        pass
    imm = [t for t in txs if t.get("category") == "immature"]
    if not imm:
        return None
    return coinbase_blocks_left(max(int(t.get("confirmations") or 0) for t in imm))


def run_cli(cli: str, extra: list[str], *args: str, timeout: float | None = 120) -> str:
    cmd = [cli, *extra, *args]
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=timeout).strip()
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("the node is busy (often mining). Try again in a few seconds.") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output.strip() or str(e)) from e


def run_json(cli: str, extra: list[str], *args: str, timeout: float | None = 120):
    raw = run_cli(cli, extra, *args, timeout=timeout)
    return json.loads(raw) if raw else None


def slim_block(block: dict) -> dict:
    return {
        "kind": "block",
        "hash": block.get("hash"),
        "height": block.get("height"),
        "time": block.get("time"),
        "nTx": block.get("nTx") or len(block.get("tx") or []),
        "previousblockhash": block.get("previousblockhash"),
        "tx": block.get("tx") or [],
    }


def slim_wallet_tx(tx: dict) -> dict:
    outs = []
    for d in tx.get("details") or []:
        outs.append(
            {
                "n": d.get("vout"),
                "value": d.get("amount"),
                "address": d.get("address"),
                "type": d.get("category"),
            }
        )
    return {
        "kind": "tx",
        "txid": tx.get("txid"),
        "confirmations": tx.get("confirmations"),
        "blockhash": tx.get("blockhash"),
        "time": tx.get("time") or tx.get("blocktime"),
        "vin": None,
        "vout": outs,
    }


def slim_tx(tx: dict) -> dict:
    outs = []
    for o in tx.get("vout") or []:
        spk = o.get("scriptPubKey") or {}
        outs.append(
            {
                "n": o.get("n"),
                "value": o.get("value"),
                "address": (spk.get("address") or (spk.get("addresses") or [None])[0]),
                "type": spk.get("type"),
            }
        )
    return {
        "kind": "tx",
        "txid": tx.get("txid"),
        "confirmations": tx.get("confirmations"),
        "blockhash": tx.get("blockhash"),
        "time": tx.get("time") or tx.get("blocktime"),
        "vin": len(tx.get("vin") or []),
        "vout": outs,
    }


def _write_backup(cli: str, wextra: list[str], datadir: str) -> tuple[Path, str]:
    folder = Path(datadir) / "backups"
    folder.mkdir(parents=True, exist_ok=True)
    name = f"bitfuc-wallet-{datetime.now().strftime('%Y%m%d-%H%M%S')}.dat"
    dest = folder / name
    run_cli(cli, wextra, "backupwallet", str(dest))
    if not dest.is_file() or dest.stat().st_size == 0:
        raise RuntimeError("backup file was not written")
    return dest, name


def lookup(cli: str, extra: list[str], wextra: list[str], query: str) -> dict:
    q = (query or "").strip()
    if q.lower().startswith("tip "):
        q = q[4:].strip()
    if not q:
        raise RuntimeError("paste a block height, a block hash, or a transaction hash")
    if q.isdigit():
        bh = run_cli(cli, extra, "getblockhash", q)
        return slim_block(run_json(cli, extra, "getblock", bh, "1"))
    if not HASH64.match(q):
        raise RuntimeError("use a block number (like 12) or a 64-character hash")
    try:
        return slim_tx(run_json(cli, extra, "getrawtransaction", q, "true"))
    except RuntimeError:
        pass
    try:
        return slim_wallet_tx(run_json(cli, wextra, "gettransaction", q))
    except RuntimeError:
        pass
    try:
        return slim_block(run_json(cli, extra, "getblock", q, "1"))
    except RuntimeError as e:
        raise RuntimeError("this node does not know that hash. Click a hash from Recent activity, or use Tip block.") from e


def make_handler(cli: str, extra: list[str], wallet: str, datadir: str):
    wextra = extra + [f"-rpcwallet={wallet}"]
    mine_lock = threading.Lock()
    mine_job = {"running": False, "wanted": 0, "done": 0, "error": None}

    def mine_worker(n: int, addr: str) -> None:
        try:
            left = n
            while left > 0:
                chunk = min(5, left)
                run_cli(cli, wextra, "generatetoaddress", str(chunk), addr, timeout=None)
                left -= chunk
                with mine_lock:
                    mine_job["done"] = n - left
        except Exception as e:  # noqa: BLE001 — surface RPC text in the UI
            with mine_lock:
                mine_job["error"] = str(e)
        finally:
            with mine_lock:
                mine_job["running"] = False

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

        def _send(self, code: int, body, ctype: str = "application/json"):
            data = body if isinstance(body, bytes) else body.encode("utf-8")
            try:
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                return

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            if path in ("/", "/index.html"):
                self._send(200, UI_HTML_PATH.read_text(encoding="utf-8"), "text/html; charset=utf-8")
                return
            if path == "/api/status":
                try:
                    info = run_json(cli, extra, "getblockchaininfo", timeout=8)
                    net = run_json(cli, extra, "getnetworkinfo", timeout=8) or {}
                    bal = run_json(cli, wextra, "getbalances", timeout=8)
                    rec = run_json(cli, wextra, "listreceivedbyaddress", "0", "true", timeout=8)
                    addr = rec[0]["address"] if rec else run_cli(cli, wextra, "getnewaddress", timeout=8)
                    txs = list(reversed(run_json(cli, wextra, "listtransactions", "*", "8", timeout=8) or []))
                except RuntimeError as e:
                    with mine_lock:
                        job = dict(mine_job)
                    if job.get("running"):
                        self._send(
                            200,
                            json.dumps(
                                {
                                    "chain": None,
                                    "blocks": None,
                                    "connections": None,
                                    "trusted": None,
                                    "immature": None,
                                    "address": "",
                                    "transactions": [],
                                    "mining": job,
                                }
                            ),
                        )
                        return
                    self._send(503, json.dumps({"error": str(e)}))
                    return
                mine = bal.get("mine", {})
                with mine_lock:
                    job = dict(mine_job)
                slim = [
                    {
                        "category": t.get("category"),
                        "amount": t.get("amount"),
                        "confirmations": t.get("confirmations"),
                        "maturity_left": (
                            coinbase_blocks_left(t.get("confirmations"))
                            if t.get("category") == "immature"
                            else None
                        ),
                        "address": t.get("address"),
                        "txid": t.get("txid"),
                        "time": t.get("time") or t.get("timereceived"),
                    }
                    for t in txs
                ]
                self._send(
                    200,
                    json.dumps(
                        {
                            "chain": info.get("chain"),
                            "blocks": info.get("blocks"),
                            "connections": net.get("connections"),
                            "bestblockhash": info.get("bestblockhash"),
                            "trusted": mine.get("trusted"),
                            "immature": mine.get("immature"),
                            "maturity_left": next_maturity_left(cli, extra, wextra, info.get("blocks"), txs),
                            "address": addr,
                            "transactions": slim,
                            "mining": job,
                        }
                    ),
                )
                return
            if path == "/api/lookup":
                q = (parse_qs(parsed.query).get("q") or [""])[0]
                try:
                    self._send(200, json.dumps(lookup(cli, extra, wextra, q)))
                except RuntimeError as e:
                    self._send(400, json.dumps({"error": str(e)}))
                return
            if path == "/api/backup-download":
                try:
                    dest, name = _write_backup(cli, wextra, datadir)
                except RuntimeError as e:
                    self._send(400, json.dumps({"error": str(e)}))
                    return
                data = dest.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{name}"')
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
                return
            self._send(404, json.dumps({"error": "not found"}))

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                payload = {}
            try:
                if self.path == "/api/address":
                    addr = run_cli(cli, wextra, "getnewaddress")
                    self._send(200, json.dumps({"address": addr}))
                    return
                if self.path == "/api/mine":
                    n = int(payload.get("n") or 1)
                    if n < 1 or n > 200:
                        raise RuntimeError("ask for between 1 and 200 blocks")
                    with mine_lock:
                        if mine_job["running"]:
                            raise RuntimeError("already mining — wait for the height to catch up")
                        rec = run_json(cli, wextra, "listreceivedbyaddress", "0", "true")
                        addr = rec[0]["address"] if rec else run_cli(cli, wextra, "getnewaddress")
                        mine_job.update({"running": True, "wanted": n, "done": 0, "error": None})
                    threading.Thread(target=mine_worker, args=(n, addr), daemon=True).start()
                    self._send(200, json.dumps({"ok": True, "started": n}))
                    return
                if self.path == "/api/send":
                    to = str(payload.get("to") or "").strip()
                    amount = str(payload.get("amount") or "").strip()
                    if not ADDR_OK.match(to):
                        raise RuntimeError("that is not a BITFUC address (fuc1 / tfuc1 / fucrt1)")
                    try:
                        if float(amount) <= 0:
                            raise ValueError
                    except ValueError:
                        raise RuntimeError("amount must be a positive number of FUC") from None
                    txid = run_cli(cli, wextra, "sendtoaddress", to, amount)
                    self._send(200, json.dumps({"ok": True, "txid": txid}))
                    return
                if self.path == "/api/lookup":
                    self._send(200, json.dumps(lookup(cli, extra, wextra, str(payload.get("q") or ""))))
                    return
                if self.path == "/api/backup":
                    dest, name = _write_backup(cli, wextra, datadir)
                    revealed = False
                    if sys.platform == "darwin":
                        subprocess.Popen(["open", "-R", str(dest)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        revealed = True
                    self._send(
                        200,
                        json.dumps(
                            {
                                "ok": True,
                                "path": str(dest),
                                "name": name,
                                "revealed": revealed,
                            }
                        ),
                    )
                    return
            except RuntimeError as e:
                self._send(400, json.dumps({"error": str(e)}))
                return
            self._send(404, json.dumps({"error": "not found"}))

    return Handler


def main() -> int:
    p = argparse.ArgumentParser(description="Local BITFUC wallet (127.0.0.1 only)")
    p.add_argument("--cli", required=True)
    p.add_argument("--datadir", required=True)
    p.add_argument("--chain", choices=("regtest", "test", "main"), default="regtest")
    p.add_argument("--wallet", default="miner")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        raise SystemExit("error: this helper only binds on this computer")

    chain_args = {"regtest": ["-regtest"], "test": ["-testnet"], "main": []}
    extra = [*chain_args[args.chain], f"-datadir={args.datadir}"]
    httpd = ThreadingHTTPServer((args.host, args.port), make_handler(args.cli, extra, args.wallet, args.datadir))
    url = f"http://{args.host}:{args.port}/"
    print(f"Open {url}", flush=True)
    print("Wallet UI on this computer only. Close with Ctrl-C.", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
