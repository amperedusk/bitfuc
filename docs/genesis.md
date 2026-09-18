# BITFUC genesis

Reproduce with:

```bash
python3 contrib/bitfuc/genesis.py
```

The generator first reproduces Bitcoin’s published genesis, then emits BITFUC
headers. Public nets also require RandomX of the 80-byte header
(`contrib/bitfuc/rxhash.cpp`, `docs/pow.md`).

Coinbase outputs are `OP_RETURN OP_PUSHDATA("BITFUC")`. Combined with Bitcoin
Core’s rule that genesis outputs are not inserted into the UTXO set, **no
developer coins** are created.

Header `nBits` is also pushed in the coinbase.

## bitfuc-regtest (frozen for local development; resettable)

| Field | Value |
| --- | --- |
| Coinbase message | `BITFUC regtest -- local development chain.` |
| nTime | 1755788400 |
| nBits | `0x207fffff` |
| nNonce | 0 |
| nVersion | 1 |
| Previous block | `0000000000000000000000000000000000000000000000000000000000000000` |
| Merkle root | `bfe26f333a0be506cd4739fec4c079c36245b1a71fced05fd1175bfecd0a530c` |
| Block hash | `36dd99e42f28638b0c4c26c43c4c57ec9edba5fb713011b0795df00d067329d5` |
| Puzzle | SHA-256d |
| P2P magic | `96 79 32 83` |
| P2P / RPC | 17444 / 17443 |
| Bech32 HRP | `fucrt` |

## bitfuc-test (TEST COINS — NO VALUE)

| Field | Value |
| --- | --- |
| Coinbase message | `BITFUC testnet -- TEST COINS -- NO VALUE.` |
| nTime | 1757948401 |
| nBits | `0x207fffff` |
| nNonce | 0 |
| Merkle root | `4f01fe9b1f9336878b1b8fd346c8034c6d9fd9769a9614e3e73097aff98f37a3` |
| Block hash | `c0bc9ac6fb04993e0927a6a65ca60cec5c4e6e1bdb0379d3d481a8d91a70e053` |
| Puzzle | RandomX |
| P2P magic | `83 30 6d c4` |
| P2P / RPC | 27333 / 27332 |
| Bech32 HRP | `tfuc` |

## bitfuc-main (frozen)

| Field | Value |
| --- | --- |
| Coinbase message | `BITFUC` |
| nTime | 1757948400 |
| nBits | `0x207fffff` |
| nNonce | 1 |
| Merkle root | `4abee4d3e0c24aed5c07eb70178f1387d45ee490d37ec503937b8cc5f3b6fbe4` |
| Block hash | `a1d32d9f62f1d1d2f9115a2a36bb35bf15a44b2e603003ca394c159b6758533a` |
| Puzzle | RandomX |
| P2P magic | `82 43 ac 07` |
| P2P / RPC | 17333 / 17332 |
| Bech32 HRP | `fuc` |

Changing these bytes after people have synced is a new coin.

## Freeze record (bitfuc-main)

Published so a second operator can check that their node agrees before they
mine or accept a payment.

| Field | Value |
| --- | --- |
| Genesis hash | `a1d32d9f62f1d1d2f9115a2a36bb35bf15a44b2e603003ca394c159b6758533a` |
| Genesis nTime | `1757948400` (2025-09-15 15:00:00 UTC) |
| Genesis nBits | `0x207fffff` |
| Genesis nNonce | `1` |
| Genesis nVersion | `1` |
| First mined block (height 1) | 2026-09-15 16:30:56 UTC |
| Puzzle | RandomX of the 80-byte header; block identity SHA-256d |
| Difficulty rule | aserti3-2d, 2-minute spacing, 2-day half-life, genesis anchor |
| Money rule | 1e9 FUC cap, ~76.10 FUC per block for 13,140,000 heights, 2% fee burn |
| Source commit | `7db86be85212d32930b01263edf7317a8f8fafbb` |

Check your own build against it:

```bash
./build/bin/bitfuc-cli -datadir="$HOME/.bitfuc-main-operator" getblockhash 0
```

A node that prints a different hash is not on this chain.
