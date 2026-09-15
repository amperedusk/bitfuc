#!/usr/bin/env bash
# Public-P2P testnet node, RPC on localhost only. TEST COINS — NO VALUE.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=../regtest/common.sh
source "$ROOT/scripts/regtest/common.sh"
find_binaries

DATADIR="${BITFUC_TESTNET_DIR:-$HOME/.bitfuc-testnet-operator}"
mkdir -p "$DATADIR"

echo "TEST COINS — NO VALUE. This is not mainnet."
echo "datadir: $DATADIR"

if "$BITFUCCLI" -testnet -datadir="$DATADIR" getblockchaininfo >/dev/null 2>&1; then
  echo "already running"
else
  "$BITFUCD" -testnet -daemon \
    -datadir="$DATADIR" \
    -server=1 \
    -listen=1 \
    -bind=0.0.0.0 \
    -port=27333 \
    -rpcbind=127.0.0.1 \
    -rpcallowip=127.0.0.1 \
    -dnsseed=0 \
    -fixedseeds=0 \
    -listenonion=0 \
    -fallbackfee=0.0002
  for _ in $(seq 1 60); do
    if "$BITFUCCLI" -testnet -datadir="$DATADIR" getblockchaininfo >/dev/null 2>&1; then
      break
    fi
    sleep 0.25
  done
fi

GENESIS="$("$BITFUCCLI" -testnet -datadir="$DATADIR" getblockhash 0)"
HEIGHT="$("$BITFUCCLI" -testnet -datadir="$DATADIR" getblockcount)"
echo "height=$HEIGHT genesis=$GENESIS"
if [[ "$GENESIS" != "c0bc9ac6fb04993e0927a6a65ca60cec5c4e6e1bdb0379d3d481a8d91a70e053" ]]; then
  echo "error: unexpected genesis (not published bitfuc-test)" >&2
  exit 1
fi
echo "P2P listen: 0.0.0.0:27333  RPC: 127.0.0.1 (cookie in $DATADIR)"
echo "Peers: bitfuc-cli -testnet -datadir=$DATADIR addnode HOST:27333 add"
echo "Wallet:  bitfuc-cli -testnet -datadir=$DATADIR createwallet miner"
