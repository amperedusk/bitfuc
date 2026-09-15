# Launch checklist

Genesis is frozen in `src/kernel/chainparams.cpp` and `docs/genesis.md`.
`bitfucd -chain=main` starts. Peers are not invented: DNS/fixed seeds stay empty
until independent operators list `addnode` hosts in `docs/mainnet-peers.md`.

## Done

- [x] D3 money rule (`docs/monetary-policy.md`)
- [x] D2 ASERT on public nets
- [x] D1 RandomX linked; `CheckProofOfWork` compares RandomX(header) on public nets
- [x] D4 genesis output unspendable (`OP_RETURN` + genesis not in UTXO set)
- [x] Genesis bytes frozen for RandomX
- [x] No hidden assumevalid / checkpoints of some other chain
- [x] Reproducible build notes (`docs/reproducible-builds.md`, workflow `bitfuc-build`)
- [x] Operator script (`scripts/mainnet/start-operator.sh`)

Public clone: https://github.com/amperedusk/bitfuc

How to run the public chain: `docs/mainnet.md`. Volunteer P2P list:
`docs/mainnet-peers.md` (empty until two independent hosts exist).

## Operators still supply

- [ ] At least two independently operated nodes, published, not a single VPS
      pretending to be a network (`docs/mainnet-peers.md` stays empty until then)

## Never a launch

- Merge-mining with Bitcoin
- A website balance, hosted keys, or “log in to your FUC”
- A fake explorer / fake DEX / fake liquidity
- Opening RPC to the public internet
- Force-pushing genesis after people have synced a public net
