#!/usr/bin/env python3
# Copyright (c) 2026 BITFUC developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""JSON helper so a program can mine and pay via a local bitfucd.

Keys stay in the node's wallet. This script is not a custodian and not a public
API. Stdout is one JSON object.

See docs/agents.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlencode

ROOT = Path(__file__).resolve().parents[2]

HRP = {
    "regtest": "fucrt1",
    "test": "tfuc1",
    "main": "fuc1",
}


def emit(*, ok: bool, **fields) -> int:
    json.dump({"ok": ok, **fields}, sys.stdout, indent=None, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0 if ok else 1


def chain_cli_args(chain: str) -> list[str]:
    if chain == "regtest":
        return ["-regtest"]
    if chain == "test":
        return ["-testnet"]
    if chain == "main":
        return []
    raise SystemExit("error: --chain must be regtest, test, or main")


def find_cli(explicit: str) -> str:
    if explicit:
        return explicit
    for c in (ROOT / "build" / "bin" / "bitfuc-cli", Path("/tmp/bitfuc-build/bin/bitfuc-cli")):
        if c.is_file():
            return str(c)
    raise SystemExit("error: set --cli /path/to/bitfuc-cli")


def run_cli(bitfuc_cli: str, extra: list[str], *args: str) -> str:
    cmd = [bitfuc_cli, *extra, *args]
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e:
        text = (e.output or "").strip() or str(e)
        raise RuntimeError(text) from e


def run_json(bitfuc_cli: str, extra: list[str], *args: str):
    raw = run_cli(bitfuc_cli, extra, *args)
    return json.loads(raw) if raw else None


def wallet_extra(base: list[str], wallet: str) -> list[str]:
    return [*base, f"-rpcwallet={wallet}"]


def ensure_wallet(bitfuc_cli: str, base: list[str], wallet: str) -> None:
    loaded = run_json(bitfuc_cli, base, "listwallets") or []
    if wallet in loaded:
        return
    try:
        run_cli(bitfuc_cli, base, "loadwallet", wallet)
        return
    except RuntimeError:
        pass
    run_cli(bitfuc_cli, base, "createwallet", wallet)


def looks_like_this_chain(address: str, chain: str) -> bool:
    return address.lower().startswith(HRP[chain])


def payment_uri(address: str, amount: str | None, memo: str | None) -> str:
    query: list[tuple[str, str]] = []
    if amount:
        query.append(("amount", amount))
    if memo:
        query.append(("message", memo))
    uri = f"bitfuc:{address}"
    if query:
        uri += "?" + urlencode(query, quote_via=quote)
    return uri


def cmd_init(bitfuc_cli: str, base: list[str], wallet: str) -> int:
    ensure_wallet(bitfuc_cli, base, wallet)
    return emit(ok=True, command="init", wallet=wallet, note="wallet exists on this node; keys never left bitfucd")


def cmd_invoice(bitfuc_cli: str, base: list[str], wallet: str, chain: str, amount: str | None, memo: str | None) -> int:
    if amount is not None:
        try:
            if float(amount) <= 0:
                return emit(ok=False, error="amount must be positive")
        except ValueError:
            return emit(ok=False, error="amount must be a FUC decimal")
    ensure_wallet(bitfuc_cli, base, wallet)
    addr = run_cli(bitfuc_cli, wallet_extra(base, wallet), "getnewaddress")
    if not looks_like_this_chain(addr, chain):
        return emit(ok=False, error=f"node returned a non-BITFUC address: {addr}")
    return emit(
        ok=True,
        command="invoice",
        type="bitfuc-invoice",
        version=1,
        network=chain,
        address=addr,
        amount_fuc=amount,
        memo=memo,
        uri=payment_uri(addr, amount, memo),
        min_confirmations=1,
        wallet=wallet,
        chain=chain,
        note="Give uri or address to the user/agent. Then: agent.py wait --address <addr>",
    )


def cmd_wait(bitfuc_cli: str, base: list[str], wallet: str, address: str, amount: str | None, minconf: int) -> int:
    ensure_wallet(bitfuc_cli, base, wallet)
    w = wallet_extra(base, wallet)
    received = run_json(bitfuc_cli, w, "getreceivedbyaddress", address, str(minconf))
    target = float(amount) if amount is not None else None
    paid = (received or 0) >= target if target is not None else (received or 0) > 0
    return emit(
        ok=True,
        command="wait",
        address=address,
        received_fuc=received,
        amount_fuc=amount,
        min_confirmations=minconf,
        paid=paid,
    )


def cmd_payments(bitfuc_cli: str, base: list[str], wallet: str, since: str, minconf: int) -> int:
    ensure_wallet(bitfuc_cli, base, wallet)
    w = wallet_extra(base, wallet)
    args = ["listsinceblock"]
    if since:
        args.extend([since, str(minconf)])
    data = run_json(bitfuc_cli, w, *args) or {}
    incoming = []
    for tx in data.get("transactions", []):
        if tx.get("category") != "receive":
            continue
        conf = int(tx.get("confirmations") or 0)
        if conf < minconf:
            continue
        incoming.append(
            {
                "txid": tx.get("txid"),
                "address": tx.get("address"),
                "amount_fuc": tx.get("amount"),
                "confirmations": tx.get("confirmations"),
                "label": tx.get("label") or "",
            }
        )
    return emit(
        ok=True,
        command="payments",
        lastblock=data.get("lastblock"),
        incoming=incoming,
        count=len(incoming),
    )


def cmd_status(bitfuc_cli: str, base: list[str], wallet: str) -> int:
    ensure_wallet(bitfuc_cli, base, wallet)
    w = wallet_extra(base, wallet)
    info = run_json(bitfuc_cli, base, "getblockchaininfo")
    bals = run_json(bitfuc_cli, w, "getbalances")
    mine = bals["mine"]
    return emit(
        ok=True,
        command="status",
        chain=info["chain"],
        height=info["blocks"],
        wallet=wallet,
        trusted_fuc=mine["trusted"],
        immature_fuc=mine["immature"],
        untrusted_pending_fuc=mine["untrusted_pending"],
        note="TEST COINS — NO VALUE" if info["chain"] != "regtest" else "laboratory chain",
    )


def cmd_receive(bitfuc_cli: str, base: list[str], wallet: str, chain: str) -> int:
    ensure_wallet(bitfuc_cli, base, wallet)
    addr = run_cli(bitfuc_cli, wallet_extra(base, wallet), "getnewaddress")
    if not looks_like_this_chain(addr, chain):
        return emit(ok=False, error=f"node returned a non-BITFUC address: {addr}")
    return emit(ok=True, command="receive", address=addr, wallet=wallet, chain=chain)


def cmd_send(bitfuc_cli: str, base: list[str], wallet: str, chain: str, to: str, amount: str) -> int:
    if not looks_like_this_chain(to, chain):
        return emit(
            ok=False,
            error=f"address must start with {HRP[chain]} on this chain (got {to!r})",
        )
    try:
        value = float(amount)
    except ValueError:
        return emit(ok=False, error="amount must be a FUC decimal")
    if value <= 0:
        return emit(ok=False, error="amount must be positive")
    ensure_wallet(bitfuc_cli, base, wallet)
    txid = run_cli(bitfuc_cli, wallet_extra(base, wallet), "sendtoaddress", to, amount)
    return emit(ok=True, command="send", txid=txid, to=to, amount_fuc=amount, wallet=wallet)


def mine_regtest(bitfuc_cli: str, w: list[str], address: str, blocks: int) -> list[str]:
    raw = run_json(bitfuc_cli, w, "generatetoaddress", str(blocks), address)
    return list(raw or [])


def mine_test(address: str, blocks: int, cli_path: str, extra: list[str]) -> list[str]:
    miner = ROOT / "contrib" / "bitfuc" / "solo_mine.py"
    cmd = [sys.executable, str(miner), "--cli", cli_path, "--chain", "test", "--address", address, "--blocks", str(blocks)]
    for flag in extra:
        if flag.startswith("-datadir="):
            cmd.extend(["--datadir", flag.split("=", 1)[1]])
        elif flag.startswith("-rpcport="):
            cmd.extend(["--rpcport", flag.split("=", 1)[1]])
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise RuntimeError((e.output or "").strip() or str(e)) from e
    hashes = []
    for line in out.splitlines():
        if line.startswith("found "):
            hashes.append(line.split()[1])
    return hashes


def cmd_mine(bitfuc_cli: str, base: list[str], wallet: str, chain: str, blocks: int, until_spendable: bool) -> int:
    ensure_wallet(bitfuc_cli, base, wallet)
    w = wallet_extra(base, wallet)
    addr = run_cli(bitfuc_cli, w, "getnewaddress")
    mined: list[str] = []
    if until_spendable:
        bals = run_json(bitfuc_cli, w, "getbalances")["mine"]
        if bals["trusted"] > 0:
            return emit(ok=True, command="mine", blocks_mined=0, hashes=[], address=addr, note="already spendable")
        n = 101 if bals["immature"] == 0 else 100
        mined = mine_regtest(bitfuc_cli, w, addr, n)
    else:
        if blocks < 1:
            return emit(ok=False, error="--blocks must be >= 1 (or pass --until-spendable)")
        mined = mine_regtest(bitfuc_cli, w, addr, blocks)
    bals = run_json(bitfuc_cli, w, "getbalances")["mine"]
    height = int(run_cli(bitfuc_cli, base, "getblockcount"))
    return emit(
        ok=True,
        command="mine",
        blocks_mined=len(mined),
        hashes=mined,
        address=addr,
        height=height,
        trusted_fuc=bals["trusted"],
        immature_fuc=bals["immature"],
    )


def main() -> int:
    p = argparse.ArgumentParser(
        description="Local JSON interface for a program to mine and send FUC. Not a hosted wallet."
    )
    p.add_argument("--cli", default="", help="path to bitfuc-cli")
    p.add_argument("--datadir", default="", help="bitfucd datadir")
    p.add_argument("--rpcport", default="", help="RPC port override")
    p.add_argument("--chain", choices=("regtest", "test", "main"), default="regtest")
    p.add_argument("--wallet", default="agent", help="wallet name inside bitfucd")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="create/load this wallet on the local node")
    sub.add_parser("status", help="height and balances")
    sub.add_parser("receive", help="new address on this wallet")

    sp_inv = sub.add_parser("invoice", help="fresh address + bitfuc: URI for a user or agent to pay")
    sp_inv.add_argument("--amount", default=None, help="FUC the payer should send")
    sp_inv.add_argument("--memo", default=None, help="shown in the URI message=")

    sp_wait = sub.add_parser("wait", help="whether this invoice address has been paid")
    sp_wait.add_argument("--address", required=True)
    sp_wait.add_argument("--amount", default=None, help="required FUC; omit to accept any incoming amount")
    sp_wait.add_argument("--minconf", type=int, default=1)

    sp_pay = sub.add_parser("payments", help="incoming txs since a block (empty = all)")
    sp_pay.add_argument("--since", default="", help="block hash from a previous lastblock")
    sp_pay.add_argument("--minconf", type=int, default=1)

    sp_send = sub.add_parser("send", help="pay a user or another agent (FUC units)")
    sp_send.add_argument("--to", required=True)
    sp_send.add_argument("--amount", required=True, help="FUC, not bits")

    sp_mine = sub.add_parser("mine", help="mine to this wallet via generatetoaddress")
    sp_mine.add_argument("--blocks", type=int, default=1)
    sp_mine.add_argument("--until-spendable", action="store_true", help="mine 101/100 so coinbase can be spent")

    args = p.parse_args()
    try:
        bitfuc_cli = find_cli(args.cli)
        base = chain_cli_args(args.chain)
        if args.datadir:
            base.append(f"-datadir={args.datadir}")
        if args.rpcport:
            base.append(f"-rpcport={args.rpcport}")
        if args.command == "init":
            return cmd_init(bitfuc_cli, base, args.wallet)
        if args.command == "status":
            return cmd_status(bitfuc_cli, base, args.wallet)
        if args.command == "receive":
            return cmd_receive(bitfuc_cli, base, args.wallet, args.chain)
        if args.command == "invoice":
            return cmd_invoice(bitfuc_cli, base, args.wallet, args.chain, args.amount, args.memo)
        if args.command == "wait":
            return cmd_wait(bitfuc_cli, base, args.wallet, args.address, args.amount, args.minconf)
        if args.command == "payments":
            return cmd_payments(bitfuc_cli, base, args.wallet, args.since, args.minconf)
        if args.command == "send":
            return cmd_send(bitfuc_cli, base, args.wallet, args.chain, args.to, args.amount)
        if args.command == "mine":
            return cmd_mine(bitfuc_cli, base, args.wallet, args.chain, args.blocks, args.until_spendable)
        return emit(ok=False, error=f"unknown command {args.command}")
    except SystemExit as e:
        if isinstance(e.code, str):
            return emit(ok=False, error=e.code)
        raise
    except RuntimeError as e:
        return emit(ok=False, error=str(e))
    except FileNotFoundError as e:
        return emit(ok=False, error=str(e))
    except json.JSONDecodeError as e:
        return emit(ok=False, error=f"node did not return JSON: {e}")


if __name__ == "__main__":
    raise SystemExit(main())
