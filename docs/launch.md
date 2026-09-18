# Launch checklist

Genesis is frozen in `src/kernel/chainparams.cpp` and `docs/genesis.md`.
`bitfucd -chain=main` starts. Discovery: one fixed seed / volunteer peer is
published in `docs/mainnet-peers.md` and baked into current builds. DNS seeds
stay empty until more independent operators exist.

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
`docs/mainnet-peers.md` (one public relay; a second independent host still wanted).

## Operators still supply

- [x] At least one public peer (`13.140.133.55:17333`, also a fixed seed in current builds)
- [ ] A second independently operated node (different person / account), then more seeds can follow

## Before height 3000: every node must be rebuilt

Difficulty is re-anchored at height 3000 (`docs/pow.md`). A node still running a
build from before that change computes the old, easier `nBits` for height 3000
and will reject the correct block as `bad-diffbits`, and vice versa. That is a
chain split between old and new builds.

Do this on **every** machine that runs `bitfucd`, including the relay, while the
tip is still below 3000:

```bash
git pull
cmake --build build --target bitfuc
./build/bin/bitfuc-cli -datadir="$DATADIR" stop
./scripts/mainnet/start-operator.sh
```

Do not mine past height 2999 until the relay is also rebuilt. Confirm the fork
took effect once the tip passes 3000:

```bash
./build/bin/bitfuc-cli -datadir="$DATADIR" getblockchaininfo | grep -E '"bits"|"blocks"'
```

`bits` must no longer be `207fffff`.

## Before height 3000: every node must be rebuilt

Difficulty is re-anchored at height 3000 (`docs/pow.md`). A node still running a
build from before that change computes the old, easier `nBits` for height 3000
and will reject the correct block as `bad-diffbits`, and vice versa. That is a
chain split between old and new builds.

Do this on **every** machine that runs `bitfucd`, including the relay, while the
tip is still below 3000:

```bash
git pull
cmake --build build --target bitfuc
./build/bin/bitfuc-cli -datadir="$DATADIR" stop
./scripts/mainnet/start-operator.sh
```

Do not mine past height 2999 until the relay is also rebuilt. Confirm the fork
took effect once the tip passes 3000:

```bash
./build/bin/bitfuc-cli -datadir="$DATADIR" getblockchaininfo | grep -E '"bits"|"blocks"'
```

`bits` must no longer be `207fffff`.

## Never a launch

- Merge-mining with Bitcoin
- A website balance, hosted keys, or “log in to your FUC”
- A fake explorer / fake DEX / fake liquidity
- Opening RPC to the public internet
- Force-pushing genesis after people have synced a public net
