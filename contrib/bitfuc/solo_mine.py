#!/usr/bin/env python3
# Copyright (c) 2026 BITFUC developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Solo miner for BITFUC via getblocktemplate / submitblock or generatetoaddress.

Regtest still hashes SHA-256d in Python. Public nets use the node's RandomX miner
(`generatetoaddress`). Not merge-mined with Bitcoin.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "test" / "functional"))

from test_framework.address import address_to_scriptpubkey  # noqa: E402
from test_framework.blocktools import (  # noqa: E402
    add_witness_commitment,
    create_block,
    create_coinbase,
)
from test_framework.messages import tx_from_hex  # noqa: E402


def cli(bitfuc_cli: str, extra: list[str], *args: str) -> str:
    cmd = [bitfuc_cli, *extra, *args]
    out = subprocess.check_output(cmd, text=True)
    return out.strip()


def cli_json(bitfuc_cli: str, extra: list[str], *args: str):
    raw = cli(bitfuc_cli, extra, *args)
    return json.loads(raw) if raw else None


def chain_args(chain: str) -> list[str]:
    if chain == "regtest":
        return ["-regtest"]
    if chain == "test":
        return ["-testnet"]
    if chain == "main":
        return []
    raise SystemExit("error: --chain=regtest, test, or main")


def mine_one(bitfuc_cli: str, extra: list[str], address: str, chain: str) -> str:
    if chain != "regtest":
        raw = cli(bitfuc_cli, extra, "generatetoaddress", "1", address)
        hashes = json.loads(raw)
        return hashes[0]
    tmpl = cli_json(bitfuc_cli, extra, "getblocktemplate", '{"rules":["segwit"]}')
    if not tmpl:
        raise SystemExit("error: empty getblocktemplate (is bitfucd running, and -server on?)")
    script = address_to_scriptpubkey(address)
    coinbase = create_coinbase(height=tmpl["height"], script_pubkey=script, nValue=0)
    coinbase.vout[0].nValue = tmpl["coinbasevalue"]
    txlist = [tx_from_hex(t["data"]) for t in tmpl.get("transactions", [])]
    block = create_block(tmpl=tmpl, coinbase=coinbase, txlist=txlist)
    add_witness_commitment(block)
    block.solve()
    hex_block = block.serialize(with_witness=True).hex()
    result = cli(bitfuc_cli, extra, "submitblock", hex_block)
    if result:
        raise SystemExit(f"error: submitblock: {result}")
    return f"{block.hash_int:064x}"


def main() -> int:
    p = argparse.ArgumentParser(description="BITFUC solo miner (local node only)")
    p.add_argument("--cli", default="", help="path to bitfuc-cli")
    p.add_argument("--datadir", default="", help="bitfucd datadir (cookie + conf)")
    p.add_argument("--rpcport", default="", help="override RPC port if not in conf")
    p.add_argument("--chain", choices=("regtest", "test", "main"), default="regtest")
    p.add_argument("--address", required=True, help="BITFUC bech32 address (fuc1… / tfuc1… / fucrt1…)")
    p.add_argument("--blocks", type=int, default=1, help="how many blocks (0 = until Ctrl-C)")
    args = p.parse_args()

    if args.chain == "test":
        print("TEST COINS — NO VALUE. Unpublished test chain. This is not a launch.", file=sys.stderr)

    bitfuc_cli = args.cli
    if not bitfuc_cli:
        for c in (ROOT / "build" / "bin" / "bitfuc-cli", Path("/tmp/bitfuc-build/bin/bitfuc-cli")):
            if c.is_file():
                bitfuc_cli = str(c)
                break
    if not bitfuc_cli:
        raise SystemExit("error: set --cli /path/to/bitfuc-cli")

    extra = chain_args(args.chain)
    if args.datadir:
        extra.append(f"-datadir={args.datadir}")
    if args.rpcport:
        extra.append(f"-rpcport={args.rpcport}")

    info = cli_json(bitfuc_cli, extra, "getblockchaininfo")
    print(f"chain={info['chain']} height={info['blocks']} mining to {args.address}", file=sys.stderr)

    n = 0
    while args.blocks == 0 or n < args.blocks:
        h = mine_one(bitfuc_cli, extra, args.address, args.chain)
        n += 1
        height = cli(bitfuc_cli, extra, "getblockcount")
        print(f"found {h}  height={height}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
