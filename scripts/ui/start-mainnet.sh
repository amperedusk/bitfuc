#!/usr/bin/env bash
# Local wallet page for bitfuc-main. Not a hosted wallet. 127.0.0.1 only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DATADIR="${BITFUC_MAIN_DIR:-$HOME/.bitfuc-main-operator}"
PORT="${BITFUC_UI_PORT:-8766}"

bash "$ROOT/scripts/mainnet/start-operator.sh"

# shellcheck source=../regtest/common.sh
source "$ROOT/scripts/regtest/common.sh"
find_binaries

if ! "$BITFUCCLI" -datadir="$DATADIR" -rpcwallet=miner getwalletinfo >/dev/null 2>&1; then
  if ! "$BITFUCCLI" -datadir="$DATADIR" loadwallet miner >/dev/null 2>&1; then
    "$BITFUCCLI" -datadir="$DATADIR" createwallet miner >/dev/null
  fi
fi
ADDR="$("$BITFUCCLI" -datadir="$DATADIR" -rpcwallet=miner getnewaddress)"
echo "ADDRESS=$ADDR"

URL="http://127.0.0.1:${PORT}/"
echo "Opening $URL (this computer only — public chain)"
if command -v open >/dev/null 2>&1; then
  (sleep 0.4 && open "$URL") &
elif command -v xdg-open >/dev/null 2>&1; then
  (sleep 0.4 && xdg-open "$URL") &
fi
exec python3 "$ROOT/contrib/bitfuc/local_ui.py" \
  --cli "$BITFUCCLI" \
  --datadir "$DATADIR" \
  --chain main \
  --port "$PORT"
