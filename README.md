# BITFUC

**The cryptocurrency nobody asked for.**

A real open-source cryptocurrency, because apparently we needed another one.

Ticker: **FUC** · Domain: **[bitfuc.com](https://bitfuc.com)**

This is a joke name on purpose. The node is not supposed to be a joke.

BITFUC is a Bitcoin Core **v31.1** derivative with an independent network identity (genesis, magics, ports, addresses, datadir). It is **not** Bitcoin and must not connect to Bitcoin.

## Status (honest)

**Phase 1 — chain prototype.**

This tree is Bitcoin Core v31.1 with BITFUC network identity. `bitfucd -regtest` is the development network. **Mainnet is not launched:** the daemon refuses `-chain=main`.

Build (after installing CMake ≥ 3.22, Boost, libevent; or `make -C depends NO_QT=1 NO_IPC=1`):

```bash
cmake -B build -DENABLE_IPC=OFF -DBUILD_GUI=OFF -DINSTALL_MAN=OFF
cmake --build build --target bitcoind bitcoin-cli
# binaries: build/bin/bitfucd  build/bin/bitfuc-cli
./build/bin/bitfucd -regtest -daemon
./build/bin/bitfuc-cli -regtest getblockchaininfo
```

There are no fake balances, fake blocks, or fake markets in this tree.

| Document | Contents |
| --- | --- |
| [docs/architecture-audit.md](docs/architecture-audit.md) | Repository audit and Bitcoin Core 31.1 identity map |
| [docs/architecture.md](docs/architecture.md) | Target architecture |
| [docs/implementation-plan.md](docs/implementation-plan.md) | Phases 0–8 |
| [docs/open-decisions.md](docs/open-decisions.md) | Protocol choices that must not be made silently |
| [docs/legal-notice.md](docs/legal-notice.md) | Experimental software; no investment promise |

Upstream Bitcoin Core build notes (still using Bitcoin binary names until the rebrand commit): [doc/](doc/).

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
