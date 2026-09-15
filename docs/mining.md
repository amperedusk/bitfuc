# Mining BITFUC

You can mine on a node **you** run. Nobody’s website, pool, or VPS is required.

Mining is a **race**, not a queue and not a two-minute salary. The network aims
to produce a block about every two minutes. Whoever finds a valid proof first
gets the whole subsidy (~76.10 FUC on public nets). Everyone else starts on
the next height. A later pool would only be a side deal that splits that one
payout; this tree does not run one.

`-testnet` is practice coins (**TEST COINS — NO VALUE**). See `docs/testnet.md`.

Public nets check **RandomX** of the 80-byte header. Block identity stays
SHA-256d (`GetHash()`). ASERT retargets public-net difficulty (`docs/pow.md`).
Do not point a Bitcoin SHA-256d pool at this coin and call it BITFUC mining.

`contrib/bitfuc/solo_mine.py` grinds SHA-256d on **regtest**. On public nets
use `generatetoaddress` or a RandomX miner against `getblocktemplate`.

## 1. Build the node

```bash
cmake -B build -DENABLE_IPC=OFF -DBUILD_GUI=OFF -DINSTALL_MAN=OFF
cmake --build build --target bitcoind bitcoin-cli
# binaries: build/bin/bitfucd  build/bin/bitfuc-cli
```

## 1b. If you just want buttons

On this computer only (not bitfuc.com):

```bash
./scripts/ui/start.sh
```

That starts a local node if needed and opens http://127.0.0.1:8765. The starter
script uses a local chain. For the public chain, run `bitfucd` without `-regtest`.

A process that should mine and pay without a browser uses `contrib/bitfuc/agent.py`
(`docs/agents.md`). Same node, JSON stdout, no hosted keys.

## 2. Regtest (the path that works now)

Trivial target. Good for learning the RPC and for the solo miner.

```bash
./scripts/mine/regtest-setup.sh
# prints ADDRESS=fucrt1…
python3 contrib/bitfuc/solo_mine.py \
  --cli ./build/bin/bitfuc-cli \
  --datadir /tmp/bitfuc-mine-regtest \
  --chain regtest \
  --address "$ADDRESS" \
  --blocks 1
```

The same node also accepts Bitcoin Core’s instant miner:

```bash
bitfuc-cli -regtest -datadir /tmp/bitfuc-mine-regtest -rpcwallet=miner \
  generatetoaddress 1 "$ADDRESS"
```

`generatetoaddress` and `solo_mine.py` both produce real blocks on that datadir.
Coinbase cannot be spent until 100 further blocks.

Three-node mine / send / restart: `docs/regtest.md`.

## 3. getblocktemplate (what other miners speak)

```bash
bitfuc-cli -regtest -datadir /tmp/bitfuc-mine-regtest \
  getblocktemplate '{"rules":["segwit"]}'
```

A miner builds a block, finds a header whose **current** puzzle digest is
under the target, and calls `submitblock`. Today that digest is SHA-256d.
Public nets are decided as RandomX (`docs/pow.md`); this script will change
with that patch. `contrib/bitfuc/solo_mine.py` is the loop for BITFUC
addresses (`fucrt1…` / `tfuc1…`), not Bitcoin `bc1`.

External SHA-256d software (cgminer, bfgminer, …) can work **only if** it is
aimed at this node’s RPC **and** the chain is still SHA-256d. Bitcoin mainnet
stratum is the wrong network. Do not merge-mine.

## 4. After a block

1. Wait 100 blocks before spending the coinbase.
2. Check `getblockcount` and `getbestblockhash` on **your** node.
3. Do not trust a website tip.

## 5. What is ready vs what is not

| Item | Status |
| --- | --- |
| Node + wallet + GBT + submitblock | Ready in this tree |
| Solo CPU miner script | `contrib/bitfuc/solo_mine.py` |
| Local starter (`./scripts/ui/start.sh`) | Ready (private chain; you are the only miner) |
| Public chain | `bitfucd` starts; DNS seeds stay empty until operators publish peers |

## 6. Rewards (not a price story)

Public nets (`docs/monetary-policy.md`): about **76.10 FUC** per block for
13,140,000 blocks (50 years at two minutes), then **0**. Cap **1,000,000,000
FUC**. 2% of transaction **fees** are burned. A typical send needs **0.010
bit/vB**. Regtest still pays 50 FUC and halves every 150 blocks. Genesis
coinbase is unspendable.

## What this file does not claim

- That a laptop is a 51% defense
- That bitfuc.com must be online for you to find a block
