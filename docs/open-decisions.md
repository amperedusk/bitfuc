# Open decisions (stop before silent protocol choices)

The project brief requires stopping when consensus, monetary policy, cryptography, premine, bridges, or custody would change. This file is that stop.

**Legend**

- **Recommended** — auditor proposal for Phase 1 unless you object
- **Must decide before mainnet genesis**
- **Deferred** — not needed for regtest

Nothing in this file is consensus. Defaults below are for discussion.

---

## D1. Proof-of-work algorithm

**Decided (2026-09-15): Option B — RandomX, independent chain, not merge-mined.**

Public nets will check RandomX on the 80-byte header. Block *identity* stays
SHA-256d (`GetHash()`), same as Bitcoin Core. The puzzle is not Bitcoin’s
SHA-256d, so a Bitcoin ASIC fleet does not get FUC as a side effect.

Regtest keeps SHA-256d + mockable mining.

**Status:** RandomX is linked. Public nets compare `RandomX(header)` to the
target. Block identity stays SHA-256d (`GetHash()`). Regtest stays SHA-256d.
See `docs/pow.md`.

---

## D2. Difficulty adjustment

**Decided (2026-09-15): Option B on public nets (aserti3-2d); Option A on
regtest; Option C (min-difficulty) on testnet only.**

| Net | Rule |
| --- | --- |
| bitfuc-main | ASERT, 2-minute spacing, 2-day half-life, genesis anchor, no min-diff |
| bitfuc-test | Same ASERT + min-difficulty if the candidate is >2×spacing late |
| bitfuc-regtest | Inherited 2016-block DAA, `nASERTHalfLife = 0` |

Implemented in `src/pow.cpp`. Spec: `docs/pow.md`.

---

## D3. Monetary policy

**Decided for public nets (2026-09-15).** Written in `docs/monetary-policy.md`.

| Parameter | Decision |
| --- | --- |
| Subunit | 1 FUC = **100,000,000 bits** (not sats) |
| Block interval | **2 minutes** (5× Bitcoin’s 10) |
| Hard cap | **1,000,000,000 FUC** |
| Issuance | ≈2% of the *cap* per year for 50 years (13,140,000 two-minute blocks), then **0** |
| Per-block subsidy (public) | cap / 13,140,000 ≈ 76.1035 FUC |
| Transfer mint | **rejected** — extra 2% on each payment would inflate forever and reward spam |
| Fee burn | **2% of transaction fees** destroyed; miners claim subsidy + 98% of fees |
| Coinbase maturity | 100 blocks (~3.3 hours at 2 minutes) |
| Developer premine | **0** |
| Hidden allocation | **forbidden** |
| Regtest | Unchanged laboratory 50 FUC / 150-block halvings, no fee burn |

Mainnet genesis is frozen (`docs/genesis.md`). RandomX is linked (D1). ASERT
is in the node (D2). Changing D3 after a public launch is a new coin.

---

## D4. Genesis coinbase spendability

Bitcoin’s genesis output is not in the UTXO set (cannot be spent).

**Recommendation:** same for BITFUC. That is **0 developer coins**, not a premine of 50 FUC to a founder key.

**Status:** implemented. Genesis coinbase is `OP_RETURN`; genesis outputs are not inserted into the UTXO set.

If anyone wants a spendable genesis output, stop: that is a premine and must be disclosed before implementation.

---

## D5. Address format

**Must decide before any wallet is used on a public net.**

| Network | Bech32 HRP (proposal) | Base58 |
| --- | --- | --- |
| bitfuc-main | `fuc` | version bytes unused by Bitcoin; prefer P2PKH starting with `F` if a collision-free version exists |
| bitfuc-test | `tfuc` | distinct from Bitcoin testnet `m`/`n`/`2`/`tb` |
| bitfuc-regtest | `fucrt` | distinct from `bcrt` |

Tests must prove Bitcoin Core will not accept BITFUC addresses as Bitcoin, and vice versa.

xpub/xprv version bytes must not be Bitcoin `xpub`/`xprv` on mainnet.

**Recommendation:** native SegWit (`fuc1…`) as default `getnewaddress` type, matching Bitcoin Core’s current default, with unique HRP.

---

## D6. Extra Bitcoin networks (signet, testnet4)

Bitcoin Core 31.1 has testnet3 (deprecated), testnet4, signet, regtest, main.

**Recommendation:** ship **three** BITFUC chains only: main, test, regtest. Remove or disable Bitcoin signet/testnet4 so a flag cannot connect to Bitcoin signet. Do not operate a BITFUC signet until there is a documented challenge key policy (signet challenge keys are a form of centralized block signing).

---

## D7. How to import Bitcoin Core

### Option A — Git history from tag `v31.1`

`git fetch` the official tag; branch from it; BITFUC commits on top. Best for blame and license provenance.

### Option B — Snapshot copy without git history

Simpler looking repo; worse provenance.

**Recommendation:** Option A. This repo starts empty, so the first implementation commit after Phase 0 docs should be the v31.1 tree (or a merge of that tag).

---

## D8. Qt GUI

**Deferred.** `BUILD_GUI=OFF`. CLI/RPC is the wallet. A GUI is branding-adjacent and not required for acceptance criteria.

---

## D9. Bridges, wrapped FUC, DEX, custody, fiat

**Deferred / stop.** No implementation without a new written decision. DEX is Phase 8 research (`docs/dex-design.md`), not Solidity on another chain pretending to be native FUC.

---

## D10. Machine / AI-agent operators

**Decided (2026-09-15):** agents are ordinary node operators. No extra subsidy,
no agent premine, no hosted “agent account.”

A program may create a wallet, mine, pay a user or another agent, and accept
payment via a `bitfuc:` invoice (`contrib/bitfuc/agent.py`, `docs/agents.md`).
Shared hosted RPC is custody (D9). Opening RPC to the public internet is out
of scope. A public directory of agents is an application, not consensus.

This is not a claim that agents will use FUC. It is the rule if they do.

---

## How to resolve a decision

Reply in this project with the decision id (e.g. “D1 = A for mainnet, accept ASIC risk”) or edit this file in a dedicated docs commit. Do not bury the choice in a huge identity patch.
