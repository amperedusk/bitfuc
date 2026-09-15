#!/usr/bin/env bash
# Public-P2P mainnet node. RPC stays on localhost.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=../regtest/common.sh
source "$ROOT/scripts/regtest/common.sh"
find_binaries

DATADIR="${BITFUC_MAIN_DIR:-$HOME/.bitfuc-main-operator}"
mkdir -p "$DATADIR"

echo "datadir: $DATADIR"
echo "P2P 17333 is public. RPC is 127.0.0.1 only."

if "$BITFUCCLI" -datadir="$DATADIR" getblockchaininfo >/dev/null 2>&1; then
  echo "already running"
else
  "$BITFUCD" -daemon \
    -datadir="$DATADIR" \
    -server=1 \
    -listen=1 \
    -bind=0.0.0.0 \
    -port=17333 \
    -rpcbind=127.0.0.1 \
    -rpcallowip=127.0.0.1 \
    -dnsseed=0 \
    -fixedseeds=0 \
    -listenonion=0 \
    -fallbackfee=0.0002
  for _ in $(seq 1 80); do
    if "$BITFUCCLI" -datadir="$DATADIR" getblockchaininfo >/dev/null 2>&1; then
      break
    fi
    sleep 0.25
  done
fi

GENESIS="$("$BITFUCCLI" -datadir="$DATADIR" getblockhash 0)"
HEIGHT="$("$BITFUCCLI" -datadir="$DATADIR" getblockcount)"
echo "height=$HEIGHT genesis=$GENESIS"
if [[ "$GENESIS" != "a1d32d9f62f1d1d2f9115a2a36bb35bf15a44b2e603003ca394c159b6758533a" ]]; then
  echo "error: unexpected genesis (not published bitfuc-main)" >&2
  exit 1
fi
echo "P2P listen: 0.0.0.0:17333  RPC: 127.0.0.1 (cookie in $DATADIR)"
echo "Peers: bitfuc-cli -datadir=$DATADIR addnode HOST:17333 add"
echo "Wallet:  bitfuc-cli -datadir=$DATADIR createwallet miner"
echo "Forward TCP 17333 if this host is behind NAT. Do not forward RPC."
echo "A second independent machine must run this script. Two processes on one box are not two operators."
