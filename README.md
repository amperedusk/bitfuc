# BITFUC

Ticker: **FUC** · Domain: **[bitfuc.com](https://bitfuc.com)**

BITFUC is a Bitcoin Core **v31.1** derivative with an independent network identity (genesis, magics, ports, addresses, datadir). It is **not** Bitcoin and must not connect to Bitcoin.

The public website is a separate brochure. This repository is the node.

```bash
git clone https://github.com/amperedusk/bitfuc.git
cd bitfuc
cmake -B build -DENABLE_IPC=OFF -DBUILD_GUI=OFF -DINSTALL_MAN=OFF
cmake --build build --target bitcoind bitcoin-cli
# binaries: build/bin/bitfucd  build/bin/bitfuc-cli
./scripts/regtest/acceptance.sh
```

There are no fake balances, fake blocks, or fake markets in this tree.

| Document | Contents |
| --- | --- |
| [docs/architecture-audit.md](docs/architecture-audit.md) | Repository audit and Bitcoin Core 31.1 identity map |
| [docs/architecture.md](docs/architecture.md) | Target architecture |
| [docs/implementation-plan.md](docs/implementation-plan.md) | Phases 0–8 |
| [docs/open-decisions.md](docs/open-decisions.md) | Protocol choices that must not be made silently |
| [docs/legal-notice.md](docs/legal-notice.md) | Experimental software; no investment promise |
| [docs/genesis.md](docs/genesis.md) | Genesis hashes |
| [docs/regtest.md](docs/regtest.md) | Three-node local network |
| [docs/mining.md](docs/mining.md) | How to mine |
| [docs/pow.md](docs/pow.md) | RandomX + ASERT |
| [docs/testnet.md](docs/testnet.md) | Public test chain; TEST COINS — NO VALUE |
| [docs/testnet-peers.md](docs/testnet-peers.md) | Optional testnet volunteers (empty until someone lists one) |
| [docs/mainnet.md](docs/mainnet.md) | Public chain operator path |
| [docs/mainnet-peers.md](docs/mainnet-peers.md) | Optional mainnet volunteers (empty until two independent hosts) |
| [docs/reproducible-builds.md](docs/reproducible-builds.md) | cmake flags and SHA-256 records |
| [docs/monetary-policy.md](docs/monetary-policy.md) | 1e9 FUC cap, 2-minute blocks, 0.010 bit/vB fees, 2% fee burn |
| [docs/wallet.md](docs/wallet.md) | Descriptor wallet in `bitfucd` (no web wallet) |
| [docs/whitepaper.md](docs/whitepaper.md) | Working paper (not a prospectus) |

Upstream Bitcoin Core build notes live under [doc/](doc/). BITFUC binaries are `bitfucd` / `bitfuc-cli` (CMake target names remain `bitcoind` / `bitcoin-cli`).

## What this project will not do

- Pretend a website is a blockchain
- Hidden premine
- Fake liquidity, volume, users, or price
- Require the original developer’s server to mine or validate
- Call a UTXO chain “untraceable”
- Claim BITFUC is legal everywhere or unregulated
- Connect to Bitcoin mainnet by accident

## License

MIT. This tree includes Bitcoin Core, released under the MIT license. See [COPYING](COPYING) and [LICENSE](LICENSE). Retain Bitcoin Core copyright notices.

## What is Bitcoin Core?

BITFUC is derived from [Bitcoin Core](https://bitcoincore.org), which connects to the Bitcoin peer-to-peer network to download and fully validate blocks and transactions. BITFUC reuses that validation engine on a **separate** chain. See upstream [doc/](doc/) for the inherited architecture.
