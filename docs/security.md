# Security model (honest, not a marketing page)

BITFUC reuses Bitcoin Core 31.1 validation. That is a *code provenance*
claim, not “as secure as Bitcoin.”

This file states what the node actually assumes.

## What is in scope

- Independent chain: own genesis, magics, ports, HRPs, datadir.
- No merge-mine. Bitcoin hashrate is not BITFUC hashrate.
- No premine. Genesis coinbase is unspendable (D4).
- No hosted wallet, no website keys, no custodial “balance.”

## Puzzle (D1)

Public nets check RandomX of the 80-byte header. Block identity is SHA-256d.
Regtest stays SHA-256d. See `docs/pow.md`.

A large CPU botnet can still 51% a small net. RandomX raises the cost of a
drive-by Bitcoin-ASIC attack; it does not create an honest majority out of
thin air.

## Difficulty (D2)

Public nets use ASERT (2-minute spacing, 2-day half-life, genesis anchor).
That stops the “hashrate spike then stall” failure of Bitcoin’s 2016-block DAA
on a new chain. It does not stop a majority attacker.

Regtest keeps the inherited DAA and a trivial target. Anyone with the datadir
can rewrite it. That is the laboratory.

Testnet allows min-difficulty blocks. Anyone with a laptop can rewrite it.

## Nodes, seeds, assumevalid

DNS seeds and fixed seeds are empty. There is no public peer list that this
project operates. `nMinimumChainWork` and `defaultAssumeValid` are zero.
Nobody should `-assumevalid` a foreign hash.

A network of one operator is not decentralized. Publish seeds only when at
least two independent machines have held a tip (`docs/testnet.md`).

## Wallets and keys

Keys live in the node’s wallet on disk you control. The website is static
HTML. There is no web wallet. There is no “login.” If a later product asks
for a seed phrase in a browser, it is out of this model.

## What we will not claim

- BITFUC is as hard to 51% as Bitcoin.
- Test coins have value.
- Fees stay 0.010 bit/vB forever (policy, not consensus).
- Privacy equal to a mixer or a shielded pool (UTXO graph is public).
- Bridges, wrapped FUC, or hosted custody (`docs/open-decisions.md` D9).
