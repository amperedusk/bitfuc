# Get started (humans)

This site is not a wallet. You copy BITFUC onto **your** computer, build the
node, then open a local page that talks only to that node.

```bash
git clone https://github.com/amperedusk/bitfuc.git
cd bitfuc
cmake -B build -DENABLE_IPC=OFF -DBUILD_GUI=OFF -DINSTALL_MAN=OFF
cmake --build build --target bitcoind bitcoin-cli
./scripts/ui/start.sh
# browser: http://127.0.0.1:8765  (this machine only)
```

`127.0.0.1` means localhost. Do not expose that port. Do not paste backups into
chat. Mining rewards need 100 extra blocks before they can be spent; the wallet
button “Mine until I can spend” does that.

Technical: `docs/wallet.md`, `docs/mining.md`, `docs/agents.md`.
Public chain (not the starter UI): `docs/mainnet.md`.
