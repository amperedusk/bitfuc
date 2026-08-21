# Security Policy

BITFUC is experimental fork software derived from Bitcoin Core. Do **not** send BITFUC-specific issues to `security@bitcoincore.org`. That address is for Bitcoin Core.

## BITFUC

Report suspected vulnerabilities in BITFUC node, wallet, or consensus code privately if a contact is published later. Do not file public issues that include exploit details for live networks.

There is **no public BITFUC mainnet** until `docs/launch.md` says otherwise.

Until a dedicated contact is listed:

- Do not expose RPC to the internet
- Do not reuse a Bitcoin datadir with `bitfucd`
- Do not import untrusted `wallet.dat` files

Threat modeling for a running BITFUC node: `docs/security.md` (written when the node exists).

## Upstream Bitcoin Core

Supported Bitcoin Core versions and the Bitcoin Core disclosure process are documented by the Bitcoin Core project: https://bitcoincore.org/en/lifecycle/#schedule

Bitcoin Core vulnerability reports: security@bitcoincore.org (not for BITFUC support).
