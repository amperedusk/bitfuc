# Open decisions (stop before silent protocol choices)

The project brief requires stopping when consensus, monetary policy, cryptography, premine, bridges, or custody would change. This file is that stop.

**Legend**

- **Recommended** — auditor proposal for Phase 1 unless you object
- **Must decide before mainnet genesis**
- **Deferred** — not needed for regtest

Nothing in this file is consensus. Defaults below are for discussion.

---

## D1. Proof-of-work algorithm

**Must decide before mainnet genesis.** Regtest can keep Bitcoin Core’s SHA-256d + mockable mining.

### Option A — SHA-256d (Bitcoin-style)

- **Pros:** No new crypto; `getblocktemplate` and existing miners work; smallest fork diff.
- **Cons:** Public BITFUC hashrate will be tiny. Bitcoin SHA-256d ASIC fleets can 51% attack, reorg, and double-spend cheaply. “CPU mining” does not compete with ASICs.
- **Does not violate** “don’t invent cryptography.”
- **Does not by itself** make mining fair for hobbyists.

### Option B — Established ASIC-resistant PoW (e.g. RandomX)

- **Pros:** CPU-mineable in practice for a hobby network; raises cost of drive-by ASIC attacks.
- **Cons:** Large, consensus-critical patch; mining software ecosystem is different; more review surface; still not a reason to invent a new hash.

### Option C — Other established PoW (scrypt, Equihash, …)

- **Pros:** Known implementations exist in other coins.
- **Cons:** Scrypt ASICs exist; still a large fork; easy to pick a dying algorithm.

**Recommendation:** Option A for **regtest and code import**. Do **not** freeze mainnet genesis on Option A without explicitly accepting ASIC 51% risk in `docs/security.md` and `docs/launch.md`. If the goal is a hobby chain people can mine on laptops, prefer Option B before testnet/mainnet freeze — that is a protocol decision, not a later patch.

**Phase 1 action:** inherit SHA-256d; do not change `src/pow.cpp` algorithm.

---

## D2. Difficulty adjustment

**Must decide before public testnet/mainnet.** Bitcoin’s DAA is a poor fit for a new low-hashrate chain.

### Option A — Bitcoin DAA (2016 blocks, ~14 days)

- Matches upstream `nPowTargetTimespan`.
- Hashrate spikes can mine thousands of blocks at the old target; then the chain can stall.

### Option B — ASERT (or similar absolute-time EMA used by several Bitcoin-derived coins)

- Adjusts continuously; better for small networks.
- Consensus change relative to Bitcoin Core; must be specified and tested.
- This is **not** “weakening PoW.” It is retargeting.

### Option C — Allow min-difficulty on testnet only (`fPowAllowMinDifficultyBlocks`)

- Bitcoin testnet behavior; fine for **testnet**.
- Must not be enabled on mainnet.

**Recommendation:** Option A on **regtest** (upstream). Option C on **testnet**. Option B **strongly preferred** for mainnet if SHA-256d is kept. Do not implement Option B until this decision is explicit.

---

## D3. Monetary policy

**Must decide before mainnet genesis.** Do not pick numbers with no rationale.

### Proposed starting point (Bitcoin-like, documented — not “because 21e6 is magic”)

| Parameter | Proposal | Rationale / tradeoff |
| --- | --- | --- |
| Subunit | 1 FUC = 1e8 base units (`COIN`) | Reuse Bitcoin Core amount type; wallets/RPC already assume 8 decimals |
| Block interval | 10 minutes | Reuse validation/spacing constants; slower UX than 1–2 min chains |
| Initial subsidy | 50 FUC | Matches upstream `GetBlockSubsidy` shape; easy to test |
| Halving | every 210,000 blocks (~4 years at 10 min) | Same issuance curve as Bitcoin; **not** a claim of similar value |
| Theoretical max supply | 21,000,000 FUC | Sum of geometric subsidy; actual supply is slightly less due to halvings/rounding as in Bitcoin |
| Coinbase maturity | 100 blocks | Reuse; ~16.7 hours at 10 min |
| Fee policy | Bitcoin Core defaults | Do not invent a fee market |
| Developer premine | **0** | Genesis coinbase unspendable; no founder outputs |
| Hidden allocation | **forbidden** | |

### Alternative (faster blocks)

2-minute blocks, subsidy/halving rescaled so years-to-halving stay ~4 years. More chain growth and more orphan risk. Only if we want faster confirmations for a later DEX.

**Recommendation:** table above for the first prototype. Write `docs/monetary-policy.md` with the same numbers **before** mainnet genesis. Changing subsidy after genesis is a hard fork.

---

## D4. Genesis coinbase spendability

Bitcoin’s genesis output is not in the UTXO set (cannot be spent).

**Recommendation:** same for BITFUC. That is **0 developer coins**, not a premine of 50 FUC to a founder key.

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

## How to resolve a decision

Reply in this project with the decision id (e.g. “D1 = A for mainnet, accept ASIC risk”) or edit this file in a dedicated docs commit. Do not bury the choice in a huge identity patch.
