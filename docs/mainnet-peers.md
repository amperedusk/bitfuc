# Volunteer bitfuc-main peers

This list is a phone book, not the ledger. Nodes do not need it to validate.
If it goes stale, use `addnode` with an address you trust.

Format: `host:17333` plus who runs it (optional). List only hosts you keep
reachable. Two rows must be two machines, not two ports on one VPS.

| Address | Notes |
| --- | --- |
| `13.140.133.55:17333` | Contabo Cloud VPS (Europe). Relay only — not a miner. |

Join:

```bash
./build/bin/bitfuc-cli -datadir="$HOME/.bitfuc-main-operator" addnode 13.140.133.55:17333 add
```

Do not list RPC ports. Do not list `127.0.0.1` or home LAN IPs. DNS/fixed seeds
in the binary stay empty until at least two **independent** operators are
reachable (two different people / accounts, not two processes on one box).
