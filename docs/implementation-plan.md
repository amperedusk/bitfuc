# BITFUC Implementation Plan

This plan follows the Phase 0 audit in `docs/architecture-audit.md`. It is a build order, not a progress report. Nothing here is implemented until the corresponding commit lands.

**Rule:** if a feature is not in the node, UI and docs must say so. No mock balances, mock blocks, or mock liquidity.

---

## Preconditions

1. Open decisions that **do not** block Phase 1: GUI, DEX, website, mainnet PoW marketing.
2. Open decisions that **do** block mainnet genesis: PoW for public nets, DAA, subsidy, genesis spendability — see `docs/open-decisions.md`.
3. Phase 1 may proceed with **regtest-only** genesis using Bitcoin-style SHA-256d and Bitcoin Core’s mockable chain, because regtest is local and resettable.

---

## Phase 0 — Repository audit

**Status:** this documentation commit.

- [x] Inspect workspace
- [x] Record empty/new repo
- [x] Identify Bitcoin Core 31.1 as baseline
- [x] List identity fields that must change
- [x] List reuse / replace / create
- [ ] User review of `docs/open-decisions.md` before mainnet genesis

**Exit:** audit merged; no node code required.

---

## Phase 1 — Chain prototype (regtest)

### 1.1 Import

- Initialize git history from Bitcoin Core **v31.1** (tag), retaining MIT `COPYING` and file headers.
- Keep `depends/`, `src/`, `test/`, CMake.
- Do not import Bitcoin’s `assumeutxo` snapshots as BITFUC state.

### 1.2 Identity (regtest first)

Rename and re-point, with tests:

- Binaries: `bitfucd`, `bitfuc-cli`, `bitfuc-tx`, `bitfuc-util`, `bitfuc-wallet`
- Datadir / `bitfuc.conf` / pid / user-agent / `CLIENT_NAME`
- Chain names: `bitfuc-main`, `bitfuc-test`, `bitfuc-regtest`
- Unique magic, ports, HRPs, Base58 prefixes (even if mainnet genesis is still a stub **disabled from use**)

Safer approach: **fully parameterize all three networks**, but refuse to start `bitfuc-main` until genesis is frozen and documented (explicit error: “mainnet genesis not frozen”).

### 1.3 Genesis (regtest)

- Original coinbase message
- Documented nonce/time/nBits
- `contrib` or `src` tool to reproduce the hash
- `docs/genesis.md` section for regtest; mainnet section marked NOT FROZEN

### 1.4 Consensus knobs for regtest

Inherit Bitcoin Core regtest: high `powLimit`, min-difficulty, instant `generatetoaddress`.

Do not change script, Taproot, or subsidy validation logic except parameters.

### 1.5 Tests

- Address HRP/version: BITFUC main/test/regtest must not decode as Bitcoin `bc`/`tb`/`1`/`3`
- Magic bytes ≠ Bitcoin magics
- Ports ≠ 8333/8332/18333/18332/18444/18443
- Subsidy function unit tests once policy is chosen
- Run upstream unit tests; fix BITFUC-constant failures honestly

### 1.6 Exit

```bash
cmake -B build
cmake --build build --target bitfucd bitfuc-cli
./build/bin/bitfucd -regtest -daemon
./build/bin/bitfuc-cli -regtest getblockchaininfo
```

`chain` is BITFUC regtest, `blocks` starts at 0, genesis hash matches `docs/genesis.md`.

---

## Phase 2 — Local multi-node network

Scripts under `scripts/regtest/` (Docker optional, not required):

1. Start node A/B/C on distinct ports and datadirs
2. `addnode` so they connect
3. Create wallet on A, `getnewaddress`
4. `generatetoaddress` until coinbase matures (100 blocks unless policy changes)
5. `sendtoaddress` to B
6. Mine on A or C; B sees confirmations
7. Stop all; restart; `getbestblockhash` agrees
8. Wipe C’s blocks; sync from A; tip matches

Document in `docs/regtest.md` and `docs/mining.md` (regtest section).

**Exit:** project acceptance criteria 1–18 on a fresh clone of this repo.

---

## Phase 3 — Testnet

- Distinct genesis, magic, ports, HRP
- `nMinimumChainWork` modest; no Bitcoin assumevalid
- DNS seeds empty; document how to run a seed
- Mining: `getblocktemplate` + CPU path; do not require a developer server
- Faucet: optional, centralized, labeled **TEST COINS — NO VALUE**
- Public claim: “testnet”, not “the BITFUC network is decentralized” if one person runs every node

**Exit:** two independent machines, two operators if possible, same tip after sync.

---

## Phase 4 — Wallet

Bitcoin Core descriptor wallet is already in the daemon. This phase is **correctness and docs**, not a new key-crypto stack.

- `docs/wallet.md`: create, `getnewaddress`, send, `backupwallet`, restore, fee estimation
- Tests: backup/restore round-trip; no private keys in logs at default verbosity
- No browser wallet until the node is boringly reliable
- No website key storage

---

## Phase 5 — Mainnet preparation

- Freeze `docs/monetary-policy.md`, `docs/consensus.md`, `docs/genesis.md`
- Resolve `docs/open-decisions.md`
- Expand consensus/regtest tests (invalid subsidy, invalid PoW, immature coinbase, reorg)
- Reproducible build notes (compiler, depends, commit, hashes)
- `docs/launch.md`: time, params, “no developer premine”, any mining before public announcement
- `docs/security.md` threat model against the actual code
- `docs/privacy.md`: UTXO graph is not “untraceable”

**Exit:** a reviewer can reproduce binaries and genesis from source.

---

## Phase 6 — Mainnet

- Publish source and (if any) binaries with checksums
- Start with empty seed list or multiple independent seeds — never one unspoken server
- Anyone can mine from genesis onward
- If a developer mines, disclose time and blocks

**Exit:** independent node operators; no hidden allocation.

---

## Phase 7 — Explorer / website

- `explorer/` indexes **this** chain (RPC/`txindex` or a documented indexer)
- `website/` at bitfuc.com: joke branding, real links to source, mine, node, docs
- No price, volume, user count, or “market cap” unless sourced and non-fabricated
- If disconnected: show error, not last cached fantasy

---

## Phase 8 — DEX research only

Write `docs/dex-design.md` comparing:

- native order book + BITFUC settlement
- HTLC atomic swaps (e.g. FUC ↔ BTC)
- native AMM (poor fit for unmodified UTXO; do not paste Uniswap)

Recommend the **simplest legitimate** design. Do not implement until Phases 2–6 are real.

---

## Suggested git commits (implementation)

```text
chore: import Bitcoin Core v31.1
chore: initialize bitfuc network parameters
feat: add bitfuc regtest genesis
feat: rename binaries and datadir to bitfuc
test: reject Bitcoin address and magic mix-ups
feat: add local multi-node regtest scripts
docs: document monetary policy
feat: add testnet configuration
```

No `--no-verify`. No force-push to a default branch.

---

## Explicit non-goals (until a later written decision)

- Kubernetes, microservices, “platform APIs”
- Hidden telemetry in `bitfucd`
- ERC-20 / Solana “FUC”
- Custodial web wallets
- Guaranteed returns, fake listings, fake liquidity
