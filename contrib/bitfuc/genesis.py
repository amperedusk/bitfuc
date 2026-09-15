#!/usr/bin/env python3
# Copyright (c) 2026 BITFUC developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Deterministic BITFUC genesis generator.

Uses Bitcoin Core's own Python serialization (test/functional/test_framework)
so the hashes match src/kernel/chainparams.cpp CreateGenesisBlock.

Verify Bitcoin's published genesis first, then emit BITFUC parameters.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "test" / "functional"))

from test_framework.messages import (  # noqa: E402
    CBlock,
    COutPoint,
    CTransaction,
    CTxIn,
    CTxOut,
)
from test_framework.script import CScript, CScriptNum, OP_CHECKSIG, OP_RETURN  # noqa: E402


def create_genesis(
    psz_timestamp: str,
    output_script: CScript,
    n_time: int,
    n_nonce: int,
    n_bits: int,
    n_version: int,
    genesis_reward: int,
) -> CBlock:
    tx = CTransaction()
    tx.version = 1
    tx.vin = [CTxIn(COutPoint(0, 0xFFFFFFFF), CScript([n_bits, CScriptNum(4), psz_timestamp.encode("utf-8")]), 0xFFFFFFFF)]
    tx.vout = [CTxOut(genesis_reward, output_script)]
    tx.nLockTime = 0

    block = CBlock()
    block.nVersion = n_version
    block.hashPrevBlock = 0
    block.nTime = n_time
    block.nBits = n_bits
    block.nNonce = n_nonce
    block.vtx = [tx]
    block.hashMerkleRoot = block.calc_merkle_root()
    return block


def verify_bitcoin_genesis() -> None:
    """Must match Bitcoin Core v31.1 CreateGenesisBlock (Times headline, P2PK)."""
    psz = "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"
    pubkey = bytes.fromhex(
        "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"
    )
    script = CScript([pubkey, OP_CHECKSIG])
    # Bitcoin Core hardcodes 486604799 in the coinbase even when header nBits differs.
    tx = CTransaction()
    tx.version = 1
    tx.vin = [CTxIn(COutPoint(0, 0xFFFFFFFF), CScript([486604799, CScriptNum(4), psz.encode("utf-8")]), 0xFFFFFFFF)]
    tx.vout = [CTxOut(50 * 100_000_000, script)]
    tx.nLockTime = 0
    block = CBlock()
    block.nVersion = 1
    block.hashPrevBlock = 0
    block.nTime = 1231006505
    block.nBits = 0x1D00FFFF
    block.nNonce = 2083236893
    block.vtx = [tx]
    block.hashMerkleRoot = block.calc_merkle_root()
    merkle = f"{block.hashMerkleRoot:064x}"
    block_hash = block.hash_hex
    assert merkle == "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b", merkle
    assert block_hash == "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f", block_hash


def mine(block: CBlock) -> CBlock:
    block.solve()
    return block


def emit(name: str, psz: str, n_time: int, n_bits: int, n_nonce: int | None) -> None:
    script = CScript([OP_RETURN, b"BITFUC"])
    nonce = 0 if n_nonce is None else n_nonce
    block = create_genesis(psz, script, n_time, nonce, n_bits, 1, 50 * 100_000_000)
    if n_nonce is None:
        mine(block)
    print(f"## {name}")
    print(f"pszTimestamp: {psz}")
    print(f"nTime:        {block.nTime}")
    print(f"nBits:        0x{block.nBits:08x}")
    print(f"nNonce:       {block.nNonce}")
    print(f"nVersion:     {block.nVersion}")
    print(f"merkle:       {block.hashMerkleRoot:064x}")
    print(f"hash:         {block.hash_hex}")
    print(f"prev:         {'0' * 64}")
    print(f"coinbase:     {block.vtx[0].vin[0].scriptSig.hex()}")
    print(f"header_hex:   {block.serialize()[:80].hex()}")
    print()


def main() -> None:
    verify_bitcoin_genesis()
    print("Bitcoin genesis reproduction: OK\n")

    t = 1757948400
    emit("bitfuc-regtest", "BITFUC regtest -- local development chain.", 1755788400, 0x207FFFFF, 0)
    emit("bitfuc-test", "BITFUC testnet -- TEST COINS -- NO VALUE.", t + 1, 0x207FFFFF, 0)
    emit("bitfuc-main", "BITFUC", t, 0x207FFFFF, 1)
    print("Public nets: RandomX of the 80-byte header (see docs/pow.md). Identity hash is SHA-256d.")


if __name__ == "__main__":
    main()
