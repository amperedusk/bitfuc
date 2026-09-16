# Public chain (bitfuc-main)

Genesis, magics, ports, and money rule are frozen (`docs/genesis.md`,
`docs/monetary-policy.md`). `bitfucd` with no `-regtest` / `-testnet` is this
chain. Addresses are `fuc1…`. P2P is **17333**. RPC is **17332** on localhost.

The starter wallet (`./scripts/ui/start.sh`) is **regtest**. It is not this chain.
Public-chain wallet page on this computer: `./scripts/ui/start-mainnet.sh`
→ http://127.0.0.1:8766

## Run a node

```bash
./scripts/mainnet/start-operator.sh
# default datadir: ~/.bitfuc-main-operator
```

That binds P2P on `0.0.0.0:17333` and RPC on `127.0.0.1`. If you are behind
NAT, forward **TCP 17333** only. Never forward RPC.

Current builds include a fixed seed and `start-operator.sh` adds
`13.140.133.55:17333` automatically so a fresh node can sync without chatting
for an IP. Manual join still works:

```bash
./build/bin/bitfuc-cli -datadir="$HOME/.bitfuc-main-operator" addnode 13.140.133.55:17333 add
```

Volunteer list: `docs/mainnet-peers.md`. Two `bitfucd` processes on the same
computer do not count as two operators.

## Mine

Public nets check RandomX (`docs/pow.md`). Genesis `nBits` is easy
(`0x207fffff`); ASERT climbs if blocks arrive faster than two minutes.

```bash
CLI="./build/bin/bitfuc-cli -datadir=$HOME/.bitfuc-main-operator"
$CLI createwallet miner
ADDR="$($CLI -rpcwallet=miner getnewaddress)"
$CLI -rpcwallet=miner generatetoaddress 1 "$ADDR"
```

Coinbase cannot be spent until 100 further blocks. Mining is a race: the finder
of a height gets the whole subsidy (~76.10 FUC). This tree does not run a pool.

## What this is not

- A website balance or hosted wallet
- A claim that one operator is a decentralized network
- A reason to open RPC to the internet
