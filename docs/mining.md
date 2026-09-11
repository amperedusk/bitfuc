# Mining BITFUC

You can mine on a node **you** run. Nobody’s website, pool, or VPS is required.

**Nothing public is live.** Do not mine `-chain=main`. `bitfucd` will refuse it.
`-testnet` is an unpublished laboratory chain (**TEST COINS — NO VALUE**). See
`docs/testnet.md`.

SHA-256d is what the imported engine uses today. A future public net might
choose a different puzzle (`docs/open-decisions.md` D1). That decision is not
made by this file.

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

That starts a local node if needed and opens http://127.0.0.1:8765 . Coins stay on the laboratory chain. There is no public network to “own FUC” on yet.

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

A miner builds a block, finds a SHA-256d header under the target, and calls
`submitblock`. `contrib/bitfuc/solo_mine.py` is that loop for BITFUC addresses
(`fucrt1…` / `tfuc1…`), not Bitcoin `bc1`.

External SHA-256d software (cgminer, bfgminer, …) can work **only if** it is
aimed at this node’s RPC and this chain’s template. Bitcoin mainnet stratum is
the wrong network.

## 4. After a block

1. Wait 100 blocks before spending the coinbase.
2. Check `getblockcount` and `getbestblockhash` on **your** node.
3. Do not trust a website tip.

## 5. What is ready vs what is not

| Item | Status |
| --- | --- |
| Node + wallet + GBT + submitblock | Ready in this tree |
| Solo CPU miner script | `contrib/bitfuc/solo_mine.py` |
| Local regtest mining | Ready |
| Unpublished testnet, local only | Prepared; not advertised as a network |
| Public testnet / seeds / faucet | Not started |
| Mainnet | Not launched |

## 6. Rewards (engine defaults, not a price story)

50 FUC per block, halving every 210,000 heights on non-regtest params;
regtest halves every 150 blocks (Bitcoin Core’s laboratory interval).
Genesis coinbase is unspendable.

## What this file does not claim

- That a laptop competes with Bitcoin ASICs on a public SHA-256d net
- That mining has started for the public
- That bitfuc.com must be online for you to find a block
