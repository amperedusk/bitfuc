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
| Anchor | Genesis below height 3000; block 2999 from height 3000 (see below) |
| Target spacing | 2 minutes |
| Half-life | 2 days (`nASERTHalfLife = 172800`) |
| Mainnet min-diff | **off** |
| Testnet min-diff | **on** if the candidate is more than 2×spacing after the parent |
| Regtest | Bitcoin 2016-block DAA, `nASERTHalfLife = 0` |

ASERT raises difficulty when blocks arrive faster than two minutes. The
retarget multiply is split so an easy `powLimit` cannot wrap a 256-bit integer.

## The height-3000 re-anchor on bitfuc-main

ASERT is an *absolute* schedule: it compares elapsed time since the anchor
against how many blocks should exist by now. `bitfuc-main` genesis carries
`nTime 1757948400` (2025-09-15), but the first block was not mined until
2026-09-15. Anchored on genesis, every node therefore computed a deficit of
roughly 262,000 blocks against the two-minute schedule, concluded the chain was
a year behind, asked for an easier target every block, and clamped at
`powLimit`. Difficulty never moved off `0x207fffff`, where a block costs about
two RandomX hashes. Heights 1 to 2999 were mined under that rule.

From height 3000:

| Parameter | Value |
| --- | --- |
| `nASERTForkHeight` | 3000 |
| Anchor | block 2999 (its real `nTime`, not genesis') |
| Anchor target | `powLimitPostFork`, not the anchor's `nBits` |
| `powLimitPostFork` | `000fffff…ffff` (compact `0x1f0fffff`) |
| Cost of a floor block | ~4,096 RandomX hashes, about a minute of one CPU thread |

Blocks below 3000 keep the genesis anchor and the old floor, so existing history
stays valid and reindexes cleanly. `consensus.powLimit` is deliberately left at
the old easy value for that reason: it still bounds `CheckProofOfWork` for those
blocks. The tighter floor is enforced through `GetNextWorkRequired`, which
`ContextualCheckBlockHeader` already requires each block's `nBits` to match
exactly.

Re-anchoring on block 2999 rather than a hardcoded timestamp means no future
value had to be guessed; every node derives the anchor from its own copy of the
chain. Setting the anchor *target* to the new floor rather than block 2999's
`nBits` is what makes difficulty jump immediately at 3000 instead of halving its
way down from `0x207fffff` over tens of thousands of blocks.

`bitfuc-test` genesis has the same one-year slip. That chain allows
min-difficulty blocks and is labelled NO VALUE, so it is not re-anchored.

## What this is not

- Not merge-mining (`getauxblock`, Bitcoin parent chain).
- Not a promise that laptops beat a dedicated RandomX botnet.
