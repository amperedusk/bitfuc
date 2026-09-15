# BITFUC wallet

The wallet is **already in `bitfucd`**. It is the inherited descriptor wallet.
There is no phone app, no browser wallet, and no hosted custody. A website
that asks for a seed phrase is theft.

## What exists

| Item | Status |
| --- | --- |
| Descriptor wallet inside `bitfucd` | Ready |
| `bitfuc-cli` create / receive / send / backup | Ready |
| Local helper UI on this machine | `./scripts/ui/start.sh` (not bitfuc.com) |
| Hardware wallet, Electrum, mobile | Not in this tree |
| Web wallet / keys on a server | Will not be added |

Addresses: `fuc1…` (public), `tfuc1…` (test, no value), `fucrt1…` (regtest).

## First coins (regtest, the path that works now)

```bash
bitfucd -regtest -daemon
bitfuc-cli -regtest createwallet miner
ADDR=$(bitfuc-cli -regtest -rpcwallet=miner getnewaddress)
# ADDR starts with fucrt1
bitfuc-cli -regtest -rpcwallet=miner generatetoaddress 101 "$ADDR"
bitfuc-cli -regtest -rpcwallet=miner getbalance
```

Coinbase is immature for 100 further blocks. On regtest, `generatetoaddress 101`
mines the subsidy block plus the maturity window. Then `sendtoaddress` works.

On the public *test* chain (`-testnet`), use `tfuc1…` and
`contrib/bitfuc/solo_mine.py` instead of instant generate. See `docs/mining.md`.

## Backup

```bash
bitfuc-cli -regtest -rpcwallet=miner backupwallet /path/on/this/machine/miner-backup.dat
```

Keep the backup offline. Do not upload it to bitfuc.com or a chat.

## Restore

```bash
bitfuc-cli -regtest restorewallet miner /path/on/this/machine/miner-backup.dat
```

## Fees

`bitfuc-cli` amounts are in **FUC**. The indivisible unit is a **bit**:
1 FUC = 100,000,000 bits. Fee rates in RPC are **bit/vB**, not sat/vB.

On public nets, default send fee is **0.010 bit/vB** (100× below the usual
1 sat/vB wallet floor). 2% of paid transaction fees are burned
(`docs/monetary-policy.md`). That is not a 2% tax on the payment amount.
Blocks are **2 minutes**; a coinbase can be spent after 100 blocks (~3.3 hours).

## Programs / agents

A process can mine and send without a GUI: `docs/agents.md` and
`python3 contrib/bitfuc/agent.py --chain=regtest status`. Same wallet, same
rules. Not a hosted bot bank.
