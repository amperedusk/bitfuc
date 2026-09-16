# Volunteer bitfuc-main peers

This list is a phone book, not the ledger. Nodes do not need it to validate.
If it goes stale, use `addnode` with an address you trust.

Format: `host:17333` plus who runs it (optional). List only hosts you keep
reachable. Two rows must be two machines, not two ports on one VPS.

| Address | Notes |
| --- | --- |
| `13.140.133.55:17333` | Public relay. Not a miner. |

After a current build, this host is also a **fixed seed**: `bitfucd` / `./scripts/mainnet/start-operator.sh` try it automatically. Manual join still works:

```bash
./build/bin/bitfuc-cli -datadir="$HOME/.bitfuc-main-operator" addnode 13.140.133.55:17333 add
```

Do not list RPC ports. Do not list `127.0.0.1` or home LAN IPs. A second
independent operator is still wanted before treating discovery as decentralized.
