#!/usr/bin/env bash
# Send test FUC from a local wallet. Centralized helper. TEST COINS — NO VALUE.
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "usage: $0 tfuc1... [amount]" >&2
  exit 1
fi
ADDR="$1"
AMT="${2:-10}"
if [[ "$ADDR" != tfuc1* ]]; then
  echo "error: faucet only sends to tfuc1 addresses (BITFUC testnet)" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck source=../regtest/common.sh
source "$ROOT/scripts/regtest/common.sh"
find_binaries
DATADIR="${BITFUC_TESTNET_DIR:-$HOME/.bitfuc-testnet-operator}"
WALLET="${BITFUC_FAUCET_WALLET:-miner}"

echo "TEST COINS — NO VALUE"
TXID="$("$BITFUCCLI" -testnet -datadir="$DATADIR" -rpcwallet="$WALLET" sendtoaddress "$ADDR" "$AMT")"
echo "txid=$TXID"
echo "mine a block if you want a confirmation: solo_mine.py --chain test ..."
