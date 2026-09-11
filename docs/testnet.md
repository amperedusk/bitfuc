# bitfuc-test — public *test* network

**TEST COINS — NO VALUE.**

This is a practice chain so people can run a node, mine, and send **test** FUC.
It is **not** mainnet. It is **not** money. It is **not** decentralized just
because the software is public — if one person runs every peer, say so.

Mainnet stays gated (`bitfucd` refuses `-chain=main`).

## Identity (published)

| Field | Value |
| --- | --- |
| Genesis hash | `21374e341b93a54c0899595c8118ade1ee4d3439a750755949167202be8aef2c` |
| Coinbase | `BITFUC testnet -- TEST COINS -- NO VALUE.` |
| P2P magic | `83 30 6d c4` |
| P2P / RPC | 27333 / 27332 |
| Bech32 | `tfuc1…` |
| Puzzle | SHA-256d (same engine as regtest; **not** a mainnet freeze) |
| Difficulty | Easy `powLimit` + min-difficulty blocks (testnet only) |
| DNS / fixed seeds | Empty on purpose |

Changing the genesis bytes after people have synced is a **new** testnet.

Anyone can rewrite this chain with a laptop. That is acceptable for a test
net and is **not** a security claim for mainnet (`docs/open-decisions.md` D1–D2).

## Run a node

```bash
bitfucd -testnet -daemon \
  -server=1 \
  -listen=1 \
  -bind=0.0.0.0 \
  -port=27333 \
  -rpcbind=127.0.0.1 \
  -rpcallowip=127.0.0.1 \
  -dnsseed=0 \
  -fixedseeds=0 \
  -fallbackfee=0.0002
bitfuc-cli -testnet createwallet miner
bitfuc-cli -testnet getblockchaininfo
# bestblockhash at height 0 must be 21374e341b93a54c0899595c8118ade1ee4d3439a750755949167202be8aef2c
```

RPC stays on localhost. P2P is what others connect to. Open **27333/tcp**
if you want inbound peers. Helper: `scripts/testnet/start-operator.sh`.

## Connect to someone else

There is no required official IP. Seeds are empty so the chain still works
if the original developer disappears.

```bash
bitfuc-cli -testnet addnode "THEIR.IP.ADDRESS:27333" add
bitfuc-cli -testnet getpeerinfo
bitfuc-cli -testnet getbestblockhash
```

Volunteer addresses (optional, not consensus): `docs/testnet-peers.md`.
Two machines that `addnode` each other and match `getbestblockhash` is a
working testnet. That is the Phase 3 exit.

## Mine (CPU, local node)

```bash
ADDR=$(bitfuc-cli -testnet -rpcwallet=miner getnewaddress)
# must start with tfuc1
python3 contrib/bitfuc/solo_mine.py --chain test --address "$ADDR" --blocks 1
```

Or `generatetoaddress` if you are only testing on one machine. Coinbase is
unspendable for 100 blocks. **TEST COINS — NO VALUE.**

## Optional faucet (centralized)

A faucet is just a wallet that already mined and runs `sendtoaddress`.
Whoever runs it is a **central** helper, not the chain.

```bash
./scripts/testnet/faucet.sh tfuc1q... 10
```

Label every faucet page **TEST COINS — NO VALUE**. Do not imply a price.

## Operate a “seed” without becoming the network

1. Run `bitfucd -testnet` with `-listen=1` on a stable host.
2. Publish `IP:27333` in `docs/testnet-peers.md` or your own page.
3. Prefer several independent operators. One unpublished VPS is a single
   point of discovery, not a consensus oracle.
4. Never put RPC on the public internet.

DNS seeds can wait until more than one person is willing to run them.

## What this is not

- Not mainnet
- Not a market
- Not “as secure as Bitcoin”
- Not something the website can invent a tip for
