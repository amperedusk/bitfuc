#!/usr/bin/env bash
# Start three local BITFUC regtest nodes (A=1, B=2, C=3) and connect them.
set -euo pipefail
# shellcheck source=common.sh
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
find_binaries

echo "bitfucd: $BITFUCD"
echo "datadir: $BASE"

for n in 1 2 3; do
  stop_node "$n" || true
  start_node "$n"
  echo "node ${n} P2P=$(node_p2p "$n") RPC=$(node_rpc "$n")"
done

cli 1 addnode "127.0.0.1:$(node_p2p 2)" add
cli 1 addnode "127.0.0.1:$(node_p2p 3)" add
cli 2 addnode "127.0.0.1:$(node_p2p 1)" add
cli 3 addnode "127.0.0.1:$(node_p2p 1)" add

wait_peers 1 2
echo "nodes connected"
cli 1 getpeerinfo | python3 -c "import json,sys; d=json.load(sys.stdin); print('peers', [p.get('addr') for p in d])"
