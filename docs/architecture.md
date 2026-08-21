# BITFUC architecture (proposed)

BITFUC is intended to be an independent Bitcoin-derived UTXO blockchain. **This file describes the target design.** As of Phase 0 there is no node in this repository. For what exists today, read `docs/architecture-audit.md`.

## Product

| | |
| --- | --- |
| Name | BITFUC |
| Ticker | FUC |
| Domain | [bitfuc.com](https://bitfuc.com) |
| Tagline | The cryptocurrency nobody asked for. |
| Joke | The name |
| Not a joke | Consensus, supply, keys, P2P |

BITFUC is experimental open-source software. It does not promise price, listings, or returns. See `docs/legal-notice.md`.

## Design principles

1. Real chain or no chain — never mock RPC results for the website.
2. Fork Bitcoin Core; do not reimplement secp256k1 or script.
3. Independent network identity (magic, ports, genesis, addresses, datadir).
4. Zero developer premine; genesis coinbase unspendable.
5. The developer is not a required server. Empty seed lists beat a single hidden seed.
6. No hidden telemetry in the node.
7. Website and explorer are optional clients of `bitfucd`, not the source of truth.

## Process architecture

```text
User / miner
    |  bitfuc-cli / getblocktemplate
    v
bitfucd
    |-- P2P (BITFUC magic + ports only)
    |-- Validation (libsecp256k1, script, UTXO)
    |-- Chainstate + block files (~/.bitfuc)
    |-- Mempool
    |-- Wallet (descriptors, keys never leave the process to a website)
    `-- RPC 127.0.0.1 + cookie
```

## Networks

| Name | Purpose |
| --- | --- |
| `bitfuc-regtest` | Local development; instant blocks; first milestone |
| `bitfuc-test` | Public test coins; **NO VALUE**; faucet may be centralized |
| `bitfuc-main` | Public chain after freeze; not started in Phase 0 |

## Layers and when they appear

| Layer | Source | Phase |
| --- | --- | --- |
| Consensus kernel | Bitcoin Core 31.1 `src/kernel`, `validation` | 1 |
| Node / P2P / RPC | Bitcoin Core, rebranded | 1–2 |
| CPU/regtest mining | `generatetoaddress` / GBT | 1–2 |
| CLI wallet | Descriptor wallet in `bitfucd` | 1, documented in 4 |
| Explorer | New, RPC-backed | 7 |
| Website | New, non-custodial | after node works |
| DEX | Research only | 8 |

## Unchanged Bitcoin-derived machinery (intent)

Unless an open decision changes it:

- SHA-256d block hash function (regtest; public nets pending D1)
- secp256k1 ECDSA and Schnorr
- Script, SegWit, Taproot as shipped in v31.1
- UTXO set, coinbase maturity 100
- Most-work chain selection and reorg handling
- Mempool policy inherited, not “anything goes”
- RPC cookie authentication

## Changed machinery (intent)

- Genesis, magics, ports, seeds, HRPs, Base58, datadir, binaries, user-agent
- Chain names `bitfuc-*`
- Checkpoints / assumevalid / AssumeUTXO: empty of Bitcoin data
- Branding and docs

## Trust model

- **Users** hold keys. The website must never receive seed phrases or private keys.
- **Miners** produce blocks under the documented subsidy. No special developer block.
- **Seed operators** help discovery; they are not oracles for balances.
- **Explorers** can lie; verify with your node.

## Related docs

| File | Role |
| --- | --- |
| `docs/architecture-audit.md` | What is in the repo now |
| `docs/implementation-plan.md` | Build order |
| `docs/open-decisions.md` | Protocol choices that require an explicit stop |
| `docs/legal-notice.md` | Non-investment / experimental software |

Docs listed in the project brief (`genesis.md`, `mining.md`, `consensus.md`, …) will be written when the corresponding behavior exists. Empty stub files that pretend those subsystems exist will not be added.
