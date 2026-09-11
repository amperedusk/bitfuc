#!/usr/bin/env bash
# Start a local mining-ready regtest node. Not a public network.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=../regtest/common.sh
source "$ROOT/scripts/regtest/common.sh"
find_binaries

DATADIR="${BITFUC_MINE_DATADIR:-/tmp/bitfuc-mine-regtest}"
mkdir -p "$DATADIR"

if "$BITFUCCLI" -regtest -datadir="$DATADIR" getblockchaininfo >/dev/null 2>&1; then
  echo "node already running at $DATADIR"
else
  "$BITFUCD" -regtest -daemon \
    -datadir="$DATADIR" \
    -rpcbind=127.0.0.1 \
    -rpcallowip=127.0.0.1 \
    -server=1 \
    -listen=0 \
    -listenonion=0 \
    -discover=0 \
    -dnsseed=0 \
    -fixedseeds=0 \
    -natpmp=0
  for _ in $(seq 1 50); do
    if "$BITFUCCLI" -regtest -datadir="$DATADIR" getblockchaininfo >/dev/null 2>&1; then
      break
    fi
    sleep 0.2
  done
fi

if ! "$BITFUCCLI" -regtest -datadir="$DATADIR" -rpcwallet=miner getwalletinfo >/dev/null 2>&1; then
  "$BITFUCCLI" -regtest -datadir="$DATADIR" loadwallet miner >/dev/null 2>&1 || \
    "$BITFUCCLI" -regtest -datadir="$DATADIR" createwallet miner >/dev/null
fi

ADDR="$("$BITFUCCLI" -regtest -datadir="$DATADIR" -rpcwallet=miner getnewaddress)"
echo "BITFUCD=$BITFUCD"
echo "DATADIR=$DATADIR"
echo "ADDRESS=$ADDR"
echo "next: python3 contrib/bitfuc/solo_mine.py --cli $BITFUCCLI --datadir $DATADIR --chain regtest --address $ADDR --blocks 1"
