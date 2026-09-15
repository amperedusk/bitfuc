# BITFUC local regtest (3 nodes)

This is a local three-process network: independent datadirs, P2P between them,
no developer server required. Public nets (`-chain=main` / `-testnet`) start
with empty DNS seeds; you add peers yourself.

## Ports (BITFUC, not Bitcoin)

| Node | P2P | RPC |
| --- | --- | --- |
| A | 17444 | 17443 |
| B | 17454 | 17453 |
| C | 17464 | 17463 |

Bitcoin’s 18444/18443 are unused on purpose.

## One-shot acceptance (criteria 3–18)

After you have built `bitfucd` / `bitfuc-cli`:

```bash
export BITFUCD=/path/to/bitfucd   # optional if it is in build/bin or /tmp/bitfuc-build/bin
./scripts/regtest/acceptance.sh
```

That script:

1. Starts nodes A, B, C
2. Connects them with `addnode`
3. Creates descriptor wallets
4. Mines 101 blocks (coinbase maturity is 100)
5. Sends 10 FUC from A to B and mines the transaction
6. Stops and restarts all three; `getbestblockhash` matches
7. Deletes C’s `blocks/` and `chainstate/` and lets C sync from A

Datadirs default to `/tmp/bitfuc-regtest-demo` (`BITFUC_REGTEST_DIR` overrides).

## Manual commands

```bash
./scripts/regtest/start-nodes.sh
./build/bin/bitfuc-cli -regtest -datadir=/tmp/bitfuc-regtest-demo/node1 getpeerinfo
./scripts/regtest/stop-nodes.sh
```

Or without the helper scripts:

```bash
./build/bin/bitfucd -regtest -daemon -datadir=/tmp/a -port=17444 -rpcport=17443 -bind=127.0.0.1
./build/bin/bitfuc-cli -regtest -datadir=/tmp/a createwallet miner
./build/bin/bitfuc-cli -regtest -datadir=/tmp/a -rpcwallet=miner getnewaddress
```

Addresses on this chain start with `fucrt1`, never Bitcoin `bcrt1` / `bc1`.

## Automated test

```bash
/tmp/bitfuc-build/test/functional/test_runner.py feature_bitfuc_mesh.py
# or, from a in-tree CMake build:
./build/test/functional/test_runner.py feature_bitfuc_mesh.py
```

(Use the `test/config.ini` that CMake generated for your build directory.)

## Seeds

Regtest has no DNS seeds. Peers are whoever you `addnode`. That is intentional:
the chain must work if the original developer disappears.
