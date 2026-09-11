#!/usr/bin/env bash
# Open a local helper page. Not a public website. Not a hosted wallet.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export BITFUC_MINE_DATADIR="${BITFUC_MINE_DATADIR:-/tmp/bitfuc-mine-regtest}"
# shellcheck source=../mine/regtest-setup.sh
# start node + wallet, print ADDRESS=
SETUP_OUT="$(bash "$ROOT/scripts/mine/regtest-setup.sh")"
echo "$SETUP_OUT"
# shellcheck source=../regtest/common.sh
source "$ROOT/scripts/regtest/common.sh"
find_binaries

PORT="${BITFUC_UI_PORT:-8765}"
URL="http://127.0.0.1:${PORT}/"
echo "Opening $URL (this computer only)"
if command -v open >/dev/null 2>&1; then
  (sleep 0.4 && open "$URL") &
elif command -v xdg-open >/dev/null 2>&1; then
  (sleep 0.4 && xdg-open "$URL") &
fi
exec python3 "$ROOT/contrib/bitfuc/local_ui.py" \
  --cli "$BITFUCCLI" \
  --datadir "$BITFUC_MINE_DATADIR" \
  --port "$PORT"
