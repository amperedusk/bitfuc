#!/usr/bin/env python3
# Copyright (c) 2026 BITFUC developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Local-only BITFUC helper for people who do not want a terminal.

Binds 127.0.0.1 only. Talks to bitfuc-cli on your machine. Never asks for a
seed. Coins here are on the local laboratory chain until a public net exists.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BITFUC on this computer</title>
<style>
  :root { --ink:#1b1b1b; --muted:#5a5854; --paper:#f4f0e6; --red:#a31f34; --line:#d4cfc3; }
  * { box-sizing: border-box; }
  body { margin:0; font: 17px/1.5 Iowan Old Style, Palatino, Georgia, serif; background:var(--paper); color:var(--ink); }
  main { max-width: 36rem; margin: 0 auto; padding: 2rem 1.25rem 4rem; }
  h1 { font-size: 1.7rem; margin: 0 0 .4rem; }
  .note { background:#fffdf8; border:1px solid var(--line); border-left:4px solid var(--red); padding:.85rem 1rem; margin:1rem 0 1.5rem; }
  .card { background:#fffdf8; border:1px solid var(--line); padding:1rem 1.1rem; margin:0 0 1rem; }
  .label { font: 11px/1.2 Helvetica Neue, Helvetica, Arial, sans-serif; letter-spacing:.08em; text-transform:uppercase; color:var(--red); }
  .big { font-size:1.8rem; margin:.2rem 0; }
  .mono { font-family: ui-monospace, Courier New, monospace; font-size:.85rem; word-break:break-all; }
  button, input { font: 15px Helvetica Neue, Helvetica, sans-serif; }
  button { background:var(--ink); color:var(--paper); border:0; padding:.55rem .9rem; margin:.2rem .35rem .2rem 0; cursor:pointer; }
  button:disabled { opacity:.45; cursor:wait; }
  button.secondary { background:transparent; color:var(--ink); border:1px solid var(--ink); }
  input { width:100%; padding:.45rem .5rem; border:1px solid var(--ink); background:#fff; margin:.35rem 0 .6rem; }
  #err { color:var(--red); min-height:1.3em; }
  footer { color:var(--muted); font-size:.85rem; margin-top:2rem; }
</style>
</head>
<body>
<main>
  <h1>BITFUC on this computer</h1>
  <p>This page is only on your machine. It is not a website wallet and it cannot see the internet’s idea of a price.</p>
  <div class="note">
    There is <b>no public BITFUC network yet</b>. What you mine here stays on this computer’s laboratory chain.
    That is still real software — just not money you can spend at a shop.
  </div>
  <div id="err"></div>
  <div class="card">
    <div class="label">Blocks on this chain</div>
    <div class="big" id="height">…</div>
    <div class="label">Spendable FUC</div>
    <div class="big" id="trusted">…</div>
    <div class="label">Immature (needs 100 more blocks)</div>
    <div class="big" id="immature">…</div>
  </div>
  <div class="card">
    <div class="label">Your address (this computer)</div>
    <p class="mono" id="addr">…</p>
    <button type="button" id="newaddr">New address</button>
  </div>
  <div class="card">
    <div class="label">Mine</div>
    <p>Each block pays a reward that you cannot spend until 100 further blocks exist. “Mine until I can spend” does that for you (101 blocks). It can take a minute.</p>
    <button type="button" data-n="1">Mine 1 block</button>
    <button type="button" data-n="101">Mine until I can spend</button>
  </div>
  <footer>Keys never leave bitfucd. Close this tab anytime. Stop the node from a terminal with bitfuc-cli stop if you started it yourself.</footer>
</main>
<script>
async function api(path, body) {
  const opt = body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {};
  const r = await fetch(path, opt);
  const j = await r.json();
  if (!r.ok || j.error) throw new Error(j.error || r.statusText);
  return j;
}
function $(id) { return document.getElementById(id); }
function setBusy(b) {
  document.querySelectorAll("button").forEach(el => { el.disabled = b; });
}
async function refresh() {
  const s = await api("/api/status");
  $("height").textContent = s.blocks;
  $("trusted").textContent = s.trusted;
  $("immature").textContent = s.immature;
  $("addr").textContent = s.address;
}
$("newaddr").onclick = async () => {
  $("err").textContent = "";
  try { await api("/api/address", {}); await refresh(); }
  catch (e) { $("err").textContent = e.message; }
};
document.querySelectorAll("button[data-n]").forEach(btn => {
  btn.onclick = async () => {
    $("err").textContent = "";
    setBusy(true);
    try { await api("/api/mine", { n: Number(btn.dataset.n) }); await refresh(); }
    catch (e) { $("err").textContent = e.message; }
    setBusy(false);
  };
});
refresh().catch(e => { $("err").textContent = e.message; });
</script>
</body>
</html>
"""


def run_cli(cli: str, extra: list[str], *args: str) -> str:
    cmd = [cli, *extra, *args]
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output.strip() or str(e)) from e


def run_json(cli: str, extra: list[str], *args: str):
    raw = run_cli(cli, extra, *args)
    return json.loads(raw) if raw else None


def make_handler(cli: str, extra: list[str], wallet: str):
    wextra = extra + [f"-rpcwallet={wallet}"]

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

        def _send(self, code: int, body, ctype: str = "application/json"):
            data = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, PAGE, "text/html; charset=utf-8")
                return
            if self.path == "/api/status":
                try:
                    info = run_json(cli, extra, "getblockchaininfo")
                    bal = run_json(cli, wextra, "getbalances")
                    rec = run_json(cli, wextra, "listreceivedbyaddress", "0", "true")
                    addr = rec[0]["address"] if rec else run_cli(cli, wextra, "getnewaddress")
                except RuntimeError as e:
                    self._send(503, json.dumps({"error": str(e)}))
                    return
                mine = bal.get("mine", {})
                self._send(
                    200,
                    json.dumps(
                        {
                            "blocks": info.get("blocks"),
                            "trusted": mine.get("trusted"),
                            "immature": mine.get("immature"),
                            "address": addr,
                        }
                    ),
                )
                return
            self._send(404, json.dumps({"error": "not found"}))

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                payload = {}
            try:
                if self.path == "/api/address":
                    addr = run_cli(cli, wextra, "getnewaddress")
                    self._send(200, json.dumps({"address": addr}))
                    return
                if self.path == "/api/mine":
                    n = int(payload.get("n") or 1)
                    if n < 1 or n > 200:
                        raise RuntimeError("ask for between 1 and 200 blocks")
                    addr = run_cli(cli, wextra, "getnewaddress")
                    rec = run_json(cli, wextra, "listreceivedbyaddress", "0", "true")
                    if rec:
                        addr = rec[0]["address"]
                    run_cli(cli, wextra, "generatetoaddress", str(n), addr)
                    self._send(200, json.dumps({"ok": True, "mined": n}))
                    return
            except RuntimeError as e:
                self._send(400, json.dumps({"error": str(e)}))
                return
            self._send(404, json.dumps({"error": "not found"}))

    return Handler


def main() -> int:
    p = argparse.ArgumentParser(description="Local BITFUC helper (127.0.0.1 only)")
    p.add_argument("--cli", required=True)
    p.add_argument("--datadir", required=True)
    p.add_argument("--chain", choices=("regtest",), default="regtest")
    p.add_argument("--wallet", default="miner")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        raise SystemExit("error: this helper only binds on this computer")

    extra = ["-regtest", f"-datadir={args.datadir}"]
    httpd = ThreadingHTTPServer((args.host, args.port), make_handler(args.cli, extra, args.wallet))
    url = f"http://{args.host}:{args.port}/"
    print(f"Open {url}", flush=True)
    print("This is not a public network. Close with Ctrl-C.", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
