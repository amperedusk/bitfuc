# Proof of work and difficulty (D1, D2)

BITFUC is an **independent** chain. It is not merge-mined with Bitcoin. A Bitcoin
miner does not get FUC as a side effect, and BITFUC does not inherit Bitcoin’s
hashrate.

## D1 — RandomX (in the node)

Public nets (`bitfuc-main`, `bitfuc-test`) check **RandomX** on the 80-byte
header (tevador/RandomX, vendored under `src/crypto/randomx`, light-mode VM).
The key is `SHA256("BITFUC RandomX key v1")`. Block *identity* (`GetHash()`)
stays double-SHA256.

| Network | Puzzle |
| --- | --- |
| bitfuc-main, bitfuc-test | `RandomX(header) < target` |
| bitfuc-regtest | SHA-256d, mockable mining |

CPU mining on a public node: `bitfuc-cli generatetoaddress` (or the local wallet
UI / `contrib/bitfuc/agent.py mine`). `contrib/bitfuc/solo_mine.py` uses
SHA-256d only on regtest.

## D2 — ASERT (in the node)

Public nets use **aserti3-2d**.

| Parameter | Value |
| --- | --- |
| Algorithm | Absolute-schedule EMA (`src/pow.cpp` `CalculateASERT`) |
| Anchor | Genesis `nBits` and `nTime` |
| Target spacing | 2 minutes |
| Half-life | 2 days (`nASERTHalfLife = 172800`) |
| Mainnet min-diff | **off** |
| Testnet min-diff | **on** if the candidate is more than 2×spacing after the parent |
| Regtest | Bitcoin 2016-block DAA, `nASERTHalfLife = 0` |

Genesis compact target is easy (`0x207fffff`); ASERT raises difficulty when
blocks arrive faster than two minutes.

## What this is not

- Not merge-mining (`getauxblock`, Bitcoin parent chain).
- Not a promise that laptops beat a dedicated RandomX botnet.
