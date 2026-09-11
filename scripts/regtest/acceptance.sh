#!/usr/bin/env bash
# BITFUC Phase 2 acceptance on one machine (criteria 3–18).
# Clone+build (1–2) are documented in README.md / docs/regtest.md.
set -euo pipefail
# shellcheck source=common.sh
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
find_binaries

REGTEST_GENESIS="36dd99e42f28638b0c4c26c43c4c57ec9edba5fb713011b0795df00d067329d5"

echo "== BITFUC regtest acceptance =="
echo "bitfucd: $BITFUCD"
echo "datadir: $BASE"

rm -rf "$BASE"
mkdir -p "$BASE"

echo "-- start 3 nodes and connect --"
for n in 1 2 3; do
  start_node "$n"
done
cli 1 addnode "127.0.0.1:$(node_p2p 2)" add
cli 1 addnode "127.0.0.1:$(node_p2p 3)" add
cli 2 addnode "127.0.0.1:$(node_p2p 1)" add
cli 3 addnode "127.0.0.1:$(node_p2p 1)" add
wait_peers 1 2

genesis="$(cli 1 getblockhash 0)"
if [[ "$genesis" != "$REGTEST_GENESIS" ]]; then
  echo "error: genesis $genesis != $REGTEST_GENESIS" >&2
  exit 1
fi
echo "genesis ok: $genesis"

echo "-- create wallets --"
ensure_wallet 1 miner
ensure_wallet 2 miner
addr_a="$(cli 1 -rpcwallet=miner getnewaddress)"
addr_b="$(cli 2 -rpcwallet=miner getnewaddress)"
echo "A address: $addr_a"
echo "B address: $addr_b"
[[ "$addr_a" == fucrt1* ]] || { echo "error: A address is not fucrt1" >&2; exit 1; }
[[ "$addr_b" == fucrt1* ]] || { echo "error: B address is not fucrt1" >&2; exit 1; }

echo "-- mine 101 blocks on A (coinbase maturity) --"
cli 1 -rpcwallet=miner generatetoaddress 101 "$addr_a" >/dev/null
wait_height 1 101
wait_height 2 101
wait_height 3 101
echo "all nodes at height 101"

echo "-- send 10 FUC A -> B, mine 1 block --"
txid="$(cli 1 -rpcwallet=miner sendtoaddress "$addr_b" 10)"
echo "txid: $txid"
# B should see it in mempool or after the block; mine immediately.
cli 1 -rpcwallet=miner generatetoaddress 1 "$addr_a" >/dev/null
wait_height 2 102
wait_height 3 102
received="$(cli 2 -rpcwallet=miner getreceivedbyaddress "$addr_b")"
python3 -c "import sys; v=float(sys.argv[1]); assert v == 10, v" "$received"
echo "B received $received FUC (confirmed)"

tip="$(cli 1 getbestblockhash)"
echo "tip: $tip"
[[ "$(cli 2 getbestblockhash)" == "$tip" ]]
[[ "$(cli 3 getbestblockhash)" == "$tip" ]]

echo "-- restart all nodes --"
for n in 1 2 3; do
  stop_node "$n"
done
for n in 1 2 3; do
  start_node "$n"
  ensure_wallet "$n" miner
done
cli 1 addnode "127.0.0.1:$(node_p2p 2)" add
cli 1 addnode "127.0.0.1:$(node_p2p 3)" add
cli 2 addnode "127.0.0.1:$(node_p2p 1)" add
cli 3 addnode "127.0.0.1:$(node_p2p 1)" add
wait_peers 1 2
[[ "$(cli 1 getbestblockhash)" == "$tip" ]]
[[ "$(cli 2 getbestblockhash)" == "$tip" ]]
[[ "$(cli 3 getbestblockhash)" == "$tip" ]]
echo "restart recovered tip $tip"

echo "-- wipe C chainstate and resync from A --"
stop_node 3
rm -rf "$(node_datadir 3)/regtest/blocks" "$(node_datadir 3)/regtest/chainstate" "$(node_datadir 3)/regtest/indexes"
start_node 3
cli 3 addnode "127.0.0.1:$(node_p2p 1)" add
wait_height 3 102
[[ "$(cli 3 getbestblockhash)" == "$tip" ]]
[[ "$(cli 3 getblockhash 0)" == "$REGTEST_GENESIS" ]]
echo "C resynced to $tip"

echo "-- stop --"
for n in 1 2 3; do
  stop_node "$n"
done

echo "OK: 3-node mine, send, restart, resync"
