# BITFUC Architecture Audit

**Phase:** 0 — Repository audit (no blockchain implementation in this commit)

**Audit date:** 2026-08-21

**Auditor note:** This document records what exists in this workspace *right now*, what Bitcoin Core provides as a fork baseline, and what BITFUC must change to become an independent network. It is not a claim that a BITFUC chain exists yet.

---

## 1. Executive finding

**This repository is new and empty.**

Inspection of the empty workspace directory on 2026-08-21 found:

| Check | Result |
| --- | --- |
| Files in the workspace | None (directory listing was empty) |
| Git repository | No (`.git` missing; `git status` returned `fatal: not a git repository`) |
| Remote | None |
| Bitcoin Core / other node implementation | **Not present** |
| Build system | None |
| Tests | None |
| Documentation | None (this file is the first) |
| Website / explorer / DEX | None |
| Secrets, keys, premine wallets | None found (nothing to find) |

There is **no existing work to preserve or delete**. Subsequent implementation should import a known Bitcoin Core release rather than invent a node from scratch.

BITFUC does not yet satisfy any acceptance criterion in the project brief (clone → build → regtest → mine → transact → restart → sync). Those criteria apply after Phase 2, not after this audit.

---

## 2. Current repository structure

```text
bitfuc/          # empty directory at audit time
```

No `src/`, `depends/`, `test/`, `contrib/`, `docs/`, `LICENSE`, or `README.md` existed before Phase 0 documentation was added.

### 2.1 Language / toolchain (existing)

None.

### 2.2 Build process (existing)

None.

### 2.3 Test process (existing)

None.

### 2.4 Operating-system assumptions (existing)

None. The developer workstation observed during the audit is macOS (`darwin 24.2.0`). That is an environment fact, not a project constraint.

---

## 3. What this is *not*

The empty tree does **not** contain:

- a fake blockchain
- mock balances
- a landing page pretending to be a network
- copied Bitcoin genesis parameters
- a premine
- telemetry

There is also no legitimate chain yet. Honesty requires saying both.

---

## 4. Recommended baseline: Bitcoin Core 31.1

The project brief requires a Bitcoin Core-derived architecture, not a greenfield cryptocurrency.

**Recommended import:** [Bitcoin Core v31.1](https://github.com/bitcoin/bitcoin/releases/tag/v31.1) (released 2026-07-08).

### 4.1 Why this baseline

- Mature, independently reviewable C++ node, wallet, RPC, P2P, and test suite.
- MIT licensed (`COPYING`), which permits a named fork if copyright notices are retained.
- CMake build (`CMakeLists.txt`, `CMakePresets.json`); Autotools is gone as of v29.
- Kernel split (`src/kernel/`, experimental `libbitcoinkernel`) keeps consensus code identifiable.
- Reproducible-build machinery already exists (`depends/`, Guix-oriented contrib scripts).
- `getblocktemplate`, `generatetoaddress`, descriptor wallets, and functional tests already exist.

### 4.2 Why not write a chain from scratch

A from-scratch node would re-implement PoW validation, UTXO handling, script, mempool, P2P, reorgs, wallet, and RPC — the exact surface where consensus bugs create inflation, theft, or splits. That contradicts “do not invent cryptography” and “serious engineering.”

### 4.3 Why not “just rename Bitcoin”

Renaming binaries while keeping Bitcoin’s genesis, magic bytes, ports, DNS seeds, address HRPs, and chain IDs would make nodes join **Bitcoin**, or produce addresses users could confuse with Bitcoin. BITFUC must be a separate network identity. See §6.

### 4.4 License obligation

Bitcoin Core v31.1 `COPYING` is MIT, copyright 2009–2026 Bitcoin Core / Bitcoin developers. A BITFUC tree **must**:

- keep the MIT license
- keep existing copyright headers on derived files
- add BITFUC copyright only for new/changed work
- not claim Bitcoin Core developers endorse BITFUC

---

## 5. Bitcoin Core 31.1 — technology map (not in this repo yet)

This section describes the **upstream** tree that Phase 1 should import. It is research against v31.1, not a claim that these files exist locally today.

### 5.1 Top-level layout

| Path | Role |
| --- | --- |
| `src/` | Node, wallet, RPC, P2P, consensus, GUI |
| `src/kernel/` | Consensus kernel, including `chainparams.cpp` |
| `depends/` | Pinned dependency builds for reproducible binaries |
| `cmake/` | CMake helpers |
| `test/` | Python functional tests |
| `src/test/` | C++ unit tests |
| `contrib/` | Devtools, linearize, signet miner, init scripts |
| `ci/` | Upstream CI |
| `doc/` | Upstream Bitcoin documentation |
| `share/` | Examples, man pages |
| `CMakeLists.txt` | Root build |

### 5.2 Language and dependencies

| Item | Bitcoin Core 31.1 |
| --- | --- |
| Language | C++ (plus Python tests, some scripts) |
| Build | CMake ≥ 3.22; in-source builds disallowed |
| Typical configure | `cmake -B build` then `cmake --build build` |
| Crypto | libsecp256k1 (subtree), SHA-256, SHA-512, RIPEMD-160, HMAC — **do not replace** |
| Wallet DB | SQLite (descriptor wallets) |
| Networking | libevent; own P2P protocol |
| Optional GUI | Qt (`BUILD_GUI`, default off in recent CMake) |
| Optional ZMQ | `-DWITH_ZMQ=ON` |
| OS support (upstream) | Linux kernel ≥ 3.17, macOS ≥ 14, Windows 10+ |

### 5.3 Binaries to inherit and rename

| Upstream | BITFUC target name | Needed in Phase 1–2 |
| --- | --- | --- |
| `bitcoind` | `bitfucd` | Yes |
| `bitcoin-cli` | `bitfuc-cli` | Yes |
| `bitcoin-tx` | `bitfuc-tx` | Yes |
| `bitcoin-util` | `bitfuc-util` | Yes |
| `bitcoin-wallet` | `bitfuc-wallet` | Yes (Phase 4 can rely on RPC wallet first) |
| `bitcoin` (unified binary) | `bitfuc` | Optional |
| `bitcoin-qt` | deferred | No — GUI is not Phase 1 |
| `bitcoin-chainstate` | deferred | No — experimental |

### 5.4 Consensus / validation stack (reuse)

These components should remain **behaviorally Bitcoin-like** unless a documented decision changes them:

- Block and transaction primitives (`src/primitives/`)
- Script interpreter, SegWit, Taproot (`src/script/`, libsecp256k1 Schnorr)
- UTXO / coins view, `CCoinsView` / chainstate
- Mempool policy vs consensus split
- Header-first sync, compact blocks, reconstruction
- Reorg / most-work chain selection (`nSequence` / BIP9 machinery as shipped)
- Signature hashing (legacy, BIP143, BIP341)
- Fee accounting, coinbase maturity (100 blocks upstream)
- DoS scoring, orphan handling, address relay

**Do not weaken these to make mining “easier.”** Regtest already allows instant blocks without changing mainnet consensus.

### 5.5 Node / P2P / RPC / wallet (reuse)

- P2P (`src/net.cpp`, `src/net_processing.cpp`, `src/protocol.*`)
- RPC server including `getblocktemplate`, `submitblock`, `generatetoaddress`
- Descriptor wallet: keygen, addresses, send, backup (`backupwallet` / `restorewallet` / descriptors)
- Indexes (txindex optional; explorer later can use `txindex=1` or a separate indexer)
- Persistence: blocks, undo, chainstate, peers.dat; clean shutdown and restart

### 5.6 Test stack (reuse, then retarget)

- C++ unit tests: hashing, script, serialization, pow helpers
- Python functional tests: multi-node, mining, wallet, reorgs, P2P
- Fuzz targets (keep when practical; not a Phase 1 blocker)

Many tests **hardcode Bitcoin genesis hashes, `bc1`/`1`/`3` addresses, magic bytes, and ports**. After identity changes they must be updated or they will correctly fail. That is desired.

---

## 6. Network identity — every Bitcoin identifier that must change

BITFUC must never accidentally speak Bitcoin’s protocol or use Bitcoin’s user-facing identifiers.

Values below are from Bitcoin Core **v31.1** `src/kernel/chainparams.cpp` and `src/chainparamsbase.cpp`.

### 6.1 Must change (independent network)

| Identity | Bitcoin Core 31.1 | BITFUC requirement |
| --- | --- | --- |
| Chain names | `main`, `test`, `testnet4`, `signet`, `regtest` | `bitfuc-main`, `bitfuc-test`, `bitfuc-regtest` (no Bitcoin signet/testnet4) |
| P2P magic (main) | `f9 be b4 d9` | New 4 bytes, not in Bitcoin’s set |
| P2P magic (testnet3) | `0b 11 09 07` | New |
| P2P magic (testnet4) | `1c 16 3f 28` | Drop testnet4 or replace |
| P2P magic (regtest) | `fa bf b5 da` | New |
| P2P magic (signet) | derived from challenge | Do not ship Bitcoin signet |
| P2P port (main) | 8333 | Unused port (proposal: 17333) |
| RPC port (main) | 8332 | Unused (proposal: 17332) |
| P2P port (test) | 18333 | Proposal: 27333 |
| RPC port (test) | 18332 | Proposal: 27332 |
| P2P port (regtest) | 18444 | Proposal: 17444 |
| RPC port (regtest) | 18443 | Proposal: 17443 |
| DNS seeds | `seed.bitcoin.sipa.be.` and others | Empty until BITFUC operators exist |
| Fixed seed peers | `chainparamsseeds.h` Bitcoin IPs | Empty / BITFUC-only later |
| Genesis (main) | time `1231006505`, nonce `2083236893`, bits `0x1d00ffff`, hash `000000000019d668…` | **New genesis; never copy** |
| Genesis coinbase text | *The Times 03/Jan/2009 …* (do not copy) | Original BITFUC message |
| Genesis output script | Bitcoin pubkey `04678afd…` | Unspendable / no developer key |
| Merkle root / asserts | Bitcoin hashes hardcoded | New, reproducible, asserted |
| Checkpoints / assumevalid | Bitcoin heights (e.g. assumevalid at 938343) | Empty / genesis only |
| `nMinimumChainWork` | Bitcoin mainnet work | Genesis-only until the chain exists |
| AssumeUTXO snapshots | Bitcoin heights 840k–935k | **Must not ship** |
| Base58 P2PKH | version `0` → addresses `1…` | Unused version; not Bitcoin `1…` |
| Base58 P2SH | version `5` → `3…` | Unused version |
| WIF | version `128` | Unused version |
| xpub / xprv | `0488B21E` / `0488ADE4` | Unique SLIP-0032-style prefixes |
| Bech32 HRP (main) | `bc` | e.g. `fuc` |
| Bech32 HRP (test) | `tb` | e.g. `tfuc` |
| Bech32 HRP (regtest) | `bcrt` | e.g. `fucrt` |
| Data directory | `~/.bitcoin`, macOS `Bitcoin`, Win `Bitcoin` | `~/.bitfuc`, `Bitfuc` |
| Config file | `bitcoin.conf` | `bitfuc.conf` |
| PID file | `bitcoind.pid` | `bitfucd.pid` |
| Cookie / RPC auth files | under Bitcoin datadir | under BITFUC datadir |
| User-agent | `/Satoshi:31.1.0/` | BITFUC UA, not Satoshi/Bitcoin |
| `CLIENT_NAME` | `Bitcoin Core` | `BITFUC` |
| Homepage in CMake | `https://bitcoincore.org/` | `https://bitfuc.com/` |
| Wallet name strings | Bitcoin | BITFUC (do not load Bitcoin wallets by default) |

### 6.2 Must not copy (copyright / confusion)

- Bitcoin genesis coinbase newspaper headline
- Bitcoin genesis block hash as a “placeholder”
- Bitcoin DNS seed hostnames
- Any implication that BITFUC is a Bitcoin sidechain, wrapper, or 2FA token

### 6.3 Proposed BITFUC identity (not yet frozen)

These are **proposals for review**, not consensus. Freeze only after the decisions in `docs/open-decisions.md` are resolved.

| Item | Proposal |
| --- | --- |
| Ticker | `FUC` |
| Main chain id | `bitfuc-main` (`-chain=main` alias) |
| Test chain id | `bitfuc-test` |
| Regtest chain id | `bitfuc-regtest` |
| Magic (main) | First 4 bytes of `SHA256d("bitfuc-main-magic-v1")` after collision check vs Bitcoin |
| Magic (test) | Same scheme with `"bitfuc-test-magic-v1"` |
| Magic (regtest) | Same scheme with `"bitfuc-regtest-magic-v1"` |
| Bech32 | `fuc` / `tfuc` / `fucrt` |
| Datadir | `~/.bitfuc` (Unix), `~/Library/Application Support/Bitfuc` (macOS), `%LOCALAPPDATA%\Bitfuc` (Windows) |
| Seeds | none hardcoded at prototype; `addnode` / `seednode` in `bitfuc.conf` |

Magic bytes must be checked against Bitcoin main/test/testnet4/signet/regtest and other well-known coins before freeze.

---

## 7. Genesis — requirements (not yet generated)

No genesis exists. When generated, it must be:

1. **Independent** of Bitcoin’s genesis (different timestamp, nonce, merkle root, hash, coinbase).
2. **Deterministic** — a documented procedure reproduces the same hash.
3. **Unspendable coinbase** unless a later, explicit decision says otherwise. Bitcoin’s genesis coinbase is not in the UTXO set; BITFUC should keep that property so genesis is **not** a developer premine.
4. Documented in `docs/genesis.md` with: version, timestamp, nBits, nonce, previous hash (`0x00…`), merkle root, block hash, coinbase message, and the exact generation command/commit.

Suggested coinbase:

```text
BITFUC
```

Do not generate mainnet genesis until monetary policy, PoW, and difficulty adjustment are decided. Regtest genesis can be generated earlier because regtest is local and resettable.

---

## 8. What can be reused vs replaced vs created

### 8.1 Reuse (do not rewrite)

- libsecp256k1 and Bitcoin script/consensus validation
- UTXO model, mempool, block download, reorgs
- Descriptor wallet and PSBT
- RPC surface (`getblockchaininfo`, `getblocktemplate`, wallet RPCs)
- CMake + `depends/` reproducible-build path
- Functional test *framework* (`test/functional/test_framework`)
- Mining *interfaces* (`getblocktemplate`, `generatetoaddress`)

### 8.2 Replace (identity and chain definition)

- `src/kernel/chainparams.cpp` / `.h`
- `src/chainparamsbase.cpp` / `.h`
- `src/kernel/chainparamsseeds.h` (empty)
- `src/clientversion.*`, CMake `CLIENT_NAME`, version numbers
- Datadir / conf / pid / cookie filenames (`src/util/`, `src/common/args.cpp`)
- Binary target names in CMake
- User-agent / protocol-name strings
- All Bitcoin seed, checkpoint, assumevalid, assumeutxo data
- Branding in `README.md`, `doc/`, man pages, `share/`

### 8.3 Must create (do not exist upstream as BITFUC)

| Artifact | When |
| --- | --- |
| This audit, architecture, legal notice | Phase 0 (now) |
| Independent genesis + `docs/genesis.md` | Phase 1 |
| `docs/monetary-policy.md` | Before genesis freeze |
| `contrib/` genesis generator (deterministic, tested) | Phase 1 |
| Regtest multi-node scripts (`scripts/regtest/`) | Phase 2 |
| BITFUC-specific address tests (no Bitcoin HRP mix-up) | Phase 1 |
| CI retargeted to this repo | Phase 1–2 |
| `docs/mining.md`, `docs/regtest.md`, etc. | As features land |
| Explorer at `bitfuc.com/explorer` | Phase 7, after a real chain |
| Website | After node is real; never before |
| DEX | Phase 8 research only until the chain is stable |

### 8.4 Do not create yet

- Pretty landing page with fake height/price
- Bridges, wrapped FUC, Solidity “FUC token”
- Centralized custody
- Hardcoded single seed that the network cannot live without
- Premine to a developer address

---

## 9. Proposed architecture (summary)

```text
                    +---------------------------+
                    |   BITFUC node (bitfucd)   |
                    |  Bitcoin Core 31.1 fork   |
                    +-------------+-------------+
                                  |
          +-----------------------+-----------------------+
          |                       |                       |
   P2P (unique magic/     Consensus kernel         RPC (localhost,
   ports, no BTC seeds)   SHA-256d PoW *          cookie auth)
          |               UTXO + script                   |
          |               independent genesis             |
          v                       |                       v
   other bitfucd peers            |                 bitfuc-cli
                                  v                 descriptor wallet
                           chainstate on disk
                           datadir ~/.bitfuc
```

\* PoW algorithm for **public** networks is an open decision (see `docs/open-decisions.md`). Regtest can use Bitcoin Core’s mockable / instant-mining path regardless.

**Networks:**

1. `bitfuc-regtest` — local, instant blocks, three-node scripts. This is the first real network.
2. `bitfuc-test` — public testnet, labeled **TEST COINS — NO VALUE**. Faucet may be centralized.
3. `bitfuc-main` — only after tests, docs, and launch disclosure. No silent pre-launch mining.

**Out of scope for the node:** website analytics, DEX matching, Ethereum bridges, Kubernetes.

**Explorer / website:** separate trees (`explorer/`, `website/`) that **only** display data from a real `bitfucd` RPC/`txindex`. If the node is down, the UI says the backend is unavailable — it does not invent blocks.

---

## 10. Implementation plan (phases)

Aligned with the project brief. **Do not skip to website or DEX.**

| Phase | Goal | Exit criterion |
| --- | --- | --- |
| **0** | Audit (this document) | Empty-repo status recorded; decisions listed |
| **1** | Import v31.1; BITFUC identity; regtest genesis | `bitfucd -regtest` starts; unit tests for params/addresses |
| **2** | Local 3-node P2P, mine, send, restart, re-sync | Acceptance criteria 1–18 on one machine |
| **3** | Testnet params, empty seeds + operator docs, faucet label | Independent machines can mine test coins |
| **4** | Wallet docs, backup/restore verification | CLI self-custody documented and tested |
| **5** | Consensus tests, reproducible builds, launch docs | Ready for a public source/binary cut |
| **6** | Mainnet genesis freeze + public launch | No hidden premine; launch time published |
| **7** | Explorer talking to real RPC | `bitfuc.com/explorer` shows actual tip |
| **8** | DEX *research* (`docs/dex-design.md`) | Design only; no fake liquidity |

Detailed task breakdown: `docs/implementation-plan.md`.

---

## 11. Architectural decisions that need to be made

These are **not** silent defaults. Changing them after genesis freeze is a hard fork or a new chain.

Documented in `docs/open-decisions.md`:

1. Proof-of-work function for testnet/mainnet (SHA-256d vs established alternatives).
2. Difficulty adjustment (Bitcoin’s 2016-block retarget vs a fast-reacting algorithm such as ASERT).
3. Block interval and subsidy/halving (monetary policy).
4. Whether genesis coinbase is unspendable (recommended: yes).
5. Address version bytes / HRP final values (collision check).
6. Keep or drop Bitcoin signet and testnet4 machinery.
7. Import method (git history from v31.1 tag vs snapshot without history).
8. Whether Qt GUI is ever in-tree.

Until (1)–(4) are explicit, **do not mine a mainnet genesis.**

---

## 12. Dangerous assumptions

| Assumption | Why it is dangerous |
| --- | --- |
| “Rename Bitcoin and we have a coin” | Nodes would follow Bitcoin or confuse funds |
| SHA-256d + tiny hashrate = Bitcoin-like security | A small amount of Bitcoin ASIC power can reorg a new SHA-256d chain |
| Bitcoin’s 2016-block DAA is fine at launch | Low hashrate + slow retarget → stall or hash-attack oscillation |
| Hardcoding one VPS as the only seed | Developer disappearance kills discovery; that is a central dependency |
| Shipping Bitcoin `assumevalid` / AssumeUTXO | Nodes would skip validation toward **Bitcoin** state |
| Website first | Fake product; violates project rules |
| Copying Bitcoin genesis “just for tests” | Copyrighted/famous coinbase; accidental mainnet confusion |
| Premine “for the faucet” on mainnet | Hidden allocation; faucet belongs on testnet only |
| “We will add a bridge later, easy” | Bridges are custody + consensus risk; out of scope |
| Weakening PoW to make CPU mining win on SHA-256d | Does not stop ASICs; only shrinks honest security |
| Claiming privacy or “untraceable” | UTXO chains leak graph metadata |

---

## 13. Risks

### 13.1 Technical

- Incomplete rebrand leaves a Bitcoin magic/port/HRP and causes cross-network damage.
- Consensus bug while editing `chainparams` / subsidy (inflation).
- Difficulty death spiral on a public SHA-256d testnet/mainnet.
- Test suite still passing on Bitcoin constants after a partial rename (false confidence).

### 13.2 Operational

- Single operator seeds presented as a “decentralized network.”
- RPC bound to `0.0.0.0` without auth.
- Release binaries that nobody can reproduce.

### 13.3 Product / legal

- Joke branding read as a financial product.
- Fake volume, fake explorer data, fake “listed on exchange.”

`docs/legal-notice.md` exists so the repo does not imply investment return or universal legality.

---

## 14. Security notes for the eventual node

Inherited Bitcoin Core controls that BITFUC should **keep**:

- RPC cookie auth by default; not public
- No hidden telemetry in `bitfucd`
- Standard script and signature validation
- Peer banning / misbehavior scoring

BITFUC-specific:

- Empty DNS seeds at start are safer than lying about decentralization
- `nMinimumChainWork` / `assumevalid` must not reference Bitcoin
- Wallet keys stay on the user’s machine; never in `website/`

Full threat model belongs in `docs/security.md` once there is code to model. Writing that file against an empty tree would be fiction.

---

## 15. Explorer, website, DEX

| Component | Status | Rule |
| --- | --- | --- |
| Explorer | Not started | Only after a real chain; query `bitfucd` |
| Website `bitfuc.com` | Not started | Funny, not misleading; no fake stats |
| DEX | Not started | Research doc in Phase 8; UTXO ≠ Uniswap |

---

## 16. CI/CD (future)

Upstream Bitcoin Core CI is large. For BITFUC, start smaller and honest:

1. Linux: CMake build + unit tests + a subset of functional tests (regtest).
2. macOS when the Linux job is green.
3. Windows when staffed; do not block correctness on it.
4. Do not claim Guix reproducibility until someone actually runs it.

---

## 17. Git workflow for this empty repo

1. `git init`
2. Branch `feature/bitfuc-blockchain`
3. Commit Phase 0 documentation only
4. Later: import Bitcoin Core v31.1 on the same branch (or a follow-up commit), then identity patches in small commits

No unrelated project is being overwritten.

---

## 18. Audit conclusion

| Question | Answer |
| --- | --- |
| New repository? | **Yes** |
| Bitcoin Core present? | **No** |
| Reuse? | Import Bitcoin Core 31.1; keep consensus/wallet/P2P/RPC |
| Replace? | All network identity, genesis, seeds, datadir, binaries, branding |
| Create? | BITFUC params, genesis procedure, regtest scripts, docs, later explorer |
| Can implementation start? | **Yes, after open decisions that affect genesis are acknowledged.** Phase 1 may import upstream and wire **regtest-only** identity while mainnet genesis stays unfrozen. |
| Is BITFUC a cryptocurrency today? | **No. It is an empty project with a plan.** |

Next document: `docs/implementation-plan.md`.
