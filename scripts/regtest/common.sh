#!/usr/bin/env bash
# Copyright (c) 2026 BITFUC developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
# Shared helpers for scripts/regtest/*.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE="${BITFUC_REGTEST_DIR:-/tmp/bitfuc-regtest-demo}"

find_binaries() {
  local candidates=(
    "${BITFUCD:-}"
    "${ROOT}/build/bin/bitfucd"
    "/tmp/bitfuc-build/bin/bitfucd"
  )
  BITFUCD=""
  for c in "${candidates[@]}"; do
    if [[ -n "$c" && -x "$c" ]]; then
      BITFUCD="$c"
      break
    fi
  done
  if [[ -z "$BITFUCD" ]]; then
    echo "error: bitfucd not found. Build it, or set BITFUCD=/path/to/bitfucd" >&2
    exit 1
  fi
  BITFUCCLI="${BITFUCCLI:-$(dirname "$BITFUCD")/bitfuc-cli}"
  if [[ ! -x "$BITFUCCLI" ]]; then
    echo "error: bitfuc-cli not found next to bitfucd ($BITFUCCLI)" >&2
    exit 1
  fi
}

node_datadir() {
  echo "${BASE}/node${1}"
}

# BITFUC regtest defaults are 17444/17443. Offset each extra node by 10.
node_p2p() {
  echo $((17444 + (${1} - 1) * 10))
}
node_rpc() {
  echo $((17443 + (${1} - 1) * 10))
}

cli() {
  local n="$1"
  shift
  "$BITFUCCLI" -regtest -datadir="$(node_datadir "$n")" -rpcport="$(node_rpc "$n")" "$@"
}

wait_rpc() {
  local n="$1"
  local i
  for i in $(seq 1 50); do
    if cli "$n" getblockchaininfo >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.2
  done
  echo "error: node ${n} RPC did not come up" >&2
  return 1
}

wait_peers() {
  local n="$1"
  local want="$2"
  local i count
  for i in $(seq 1 50); do
    count="$(cli "$n" getconnectioncount)"
    if [[ "$count" -ge "$want" ]]; then
      return 0
    fi
    sleep 0.2
  done
  echo "error: node ${n} has ${count:-0} peers, wanted ${want}" >&2
  return 1
}

wait_height() {
  local n="$1"
  local height="$2"
  local i h
  for i in $(seq 1 100); do
    h="$(cli "$n" getblockcount)"
    if [[ "$h" -eq "$height" ]]; then
      return 0
    fi
    sleep 0.2
  done
  echo "error: node ${n} height ${h:-?} != ${height}" >&2
  return 1
}

start_node() {
  local n="$1"
  local datadir p2p rpc
  datadir="$(node_datadir "$n")"
  p2p="$(node_p2p "$n")"
  rpc="$(node_rpc "$n")"
  mkdir -p "$datadir"
  "$BITFUCD" -regtest -daemon \
    -datadir="$datadir" \
    -port="$p2p" \
    -rpcport="$rpc" \
    -bind=127.0.0.1 \
    -rpcbind=127.0.0.1 \
    -rpcallowip=127.0.0.1 \
    -listen=1 \
    -listenonion=0 \
    -discover=0 \
    -dnsseed=0 \
    -fixedseeds=0 \
    -natpmp=0 \
    -server=1 \
    -fallbackfee=0.0002 \
    -whitelist=127.0.0.1 \
    -connect=0
  wait_rpc "$n"
}

stop_node() {
  local n="$1"
  local datadir pidfile pid
  datadir="$(node_datadir "$n")"
  pidfile="${datadir}/regtest/bitfucd.pid"
  cli "$n" stop >/dev/null 2>&1 || true
  local i
  for i in $(seq 1 80); do
    if [[ -f "$pidfile" ]]; then
      pid="$(tr -d '[:space:]' < "$pidfile" 2>/dev/null || true)"
      if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
        sleep 0.25
        continue
      fi
    fi
    # RPC down and pid gone (or never started)
    if ! cli "$n" getblockchaininfo >/dev/null 2>&1; then
      rm -f "$pidfile"
      return 0
    fi
    sleep 0.25
  done
  echo "error: node ${n} did not stop" >&2
  return 1
}

ensure_wallet() {
  local n="$1"
  local name="${2:-miner}"
  if cli "$n" -rpcwallet="$name" getwalletinfo >/dev/null 2>&1; then
    return 0
  fi
  if cli "$n" loadwallet "$name" >/dev/null 2>&1; then
    return 0
  fi
  cli "$n" createwallet "$name" >/dev/null
}
