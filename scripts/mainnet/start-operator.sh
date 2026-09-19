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

rpc_err() {
  "$BITFUCCLI" -datadir="$DATADIR" getblockchaininfo 2>&1 >/dev/null || true
}

wait_rpc() {
  local i
  echo "Waiting for the node to finish loading the chain…"
  for i in $(seq 1 180); do
    if "$BITFUCCLI" -datadir="$DATADIR" getblockchaininfo >/dev/null 2>&1; then
      return 0
    fi
    if (( i == 1 || i % 10 == 0 )); then
      echo "still loading… ${i}s"
    fi
    sleep 1
  done
  echo "error: node did not finish loading in 3 minutes. Leave it, wait, then run this script again." >&2
  return 1
}

ERR="$(rpc_err)"
if "$BITFUCCLI" -datadir="$DATADIR" getblockchaininfo >/dev/null 2>&1; then
  echo "already running"
  "$BITFUCCLI" -datadir="$DATADIR" addnode 13.140.133.55:17333 add >/dev/null 2>&1 || true
elif echo "$ERR" | grep -q -- '-28'; then
  echo "already started; block index is still loading."
  wait_rpc
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
    -addnode=13.140.133.55:17333 \
    -listenonion=0 \
    -fallbackfee=0.0002
  wait_rpc
fi

GENESIS="$("$BITFUCCLI" -datadir="$DATADIR" getblockhash 0)"
HEIGHT="$("$BITFUCCLI" -datadir="$DATADIR" getblockcount)"
echo "height=$HEIGHT genesis=$GENESIS"
if [[ "$GENESIS" != "a1d32d9f62f1d1d2f9115a2a36bb35bf15a44b2e603003ca394c159b6758533a" ]]; then
  echo "error: unexpected genesis (not published bitfuc-main)" >&2
  exit 1
fi
echo "P2P listen: 0.0.0.0:17333  RPC: 127.0.0.1 (cookie in $DATADIR)"
echo "Default peer: 13.140.133.55:17333 (also baked into fixed seeds after rebuild)"
echo "Wallet:  bitfuc-cli -datadir=$DATADIR createwallet miner"
echo "Forward TCP 17333 if this host is behind NAT. Do not forward RPC."
echo "A second independent machine must run this script. Two processes on one box are not two operators."
