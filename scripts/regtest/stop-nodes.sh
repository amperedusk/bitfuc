#!/usr/bin/env bash
# Stop the three local BITFUC regtest nodes started by start-nodes.sh.
set -euo pipefail
# shellcheck source=common.sh
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
find_binaries
for n in 1 2 3; do
  stop_node "$n" || true
done
echo "stopped"
