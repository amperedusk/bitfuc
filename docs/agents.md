# Agents: wallets, mining, and payments

A program on BITFUC is not a new kind of money. It can **open a wallet, mine,
pay, and get paid** on the same UTXO chain a person uses. The chain does not
know whether a key is held by a human or a process.

## The four flows

| Who → whom | How |
| --- | --- |
| Agent funds itself | `init` then `mine` (coinbase still matures 100 blocks) |
| Agent → agent | Payee `invoice`; payer `send --to` that address |
| User → agent | Agent `invoice`; user pays the `bitfuc:` URI / address from their wallet |
| Agent → user | Agent `send --to` the user’s `fucrt1…` / `tfuc1…` / `fuc1…` |

The coin does not know whether a key is held by a human or a process. That is
the point.

## What an agent holds

| Piece | Who holds it |
| --- | --- |
| Keys | The `bitfucd` wallet on a machine the agent’s operator controls |
| Mining | `getblocktemplate` / `submitblock` (or `generatetoaddress` on regtest) |
| Accepting payment | A fresh address per invoice; `wait` / `payments` to see it land |
| Paying | `sendtoaddress` to the other party’s address |

Two agents that share one wallet or one hosted RPC are **not** two economic
actors. They are one custodian. If you want agents to pay *each other*, or to
take money from users, each payee needs keys it can refuse to export.

## Local JSON helper

```bash
python3 contrib/bitfuc/agent.py --chain=regtest init
python3 contrib/bitfuc/agent.py --chain=regtest mine --until-spendable
python3 contrib/bitfuc/agent.py --chain=regtest invoice --amount 1.25 --memo "api call"
# → { "address":"fucrt1…", "uri":"bitfuc:fucrt1…?amount=1.25&message=api+call" }
python3 contrib/bitfuc/agent.py --chain=regtest wait --address fucrt1… --amount 1.25
python3 contrib/bitfuc/agent.py --chain=regtest send --to fucrt1… --amount 0.5
python3 contrib/bitfuc/agent.py --chain=regtest payments
```

Stdout is one JSON object. The helper never asks for a
seed and never binds a public wallet API.

The URI scheme is `bitfuc:` (BIP21-shaped: address, optional `amount`,
`message`). It is not `bitcoin:`. A human wallet that only speaks `bitcoin:`
will not pay it until someone teaches that wallet BITFUC. Until then, paste
the address and amount.

## Confirmations (policy, not consensus)

Public nets target **two-minute** blocks. `wait --minconf 1` is one block
(~2 minutes). Six confirmations is about twelve minutes. Agents that ship
goods at 0-conf are taking the same double-spend risk humans do.

Cheap/fast policy that helps machine-to-machine use:

- 2-minute blocks
- default **0.010 bit/vB**
- 1 bit is the atom (not a sat)

Coinbase still waits **100 blocks** (~3.3 hours on public timing). An agent
that just mined cannot spend that output until then. Incoming *payments* from
users are spendable after the usual confirmation policy, not after 100 blocks.

## Two agents (or a user and an agent) on two machines

1. Each starts `bitfucd` (regtest locally; `-testnet` is **NO VALUE**).
2. Each `init`s a wallet.
3. They `addnode` each other on the **P2P** port. RPC stays on `127.0.0.1`.
4. The payee creates an `invoice` and sends the JSON/URI out of band (chat,
   API response, whatever). This repo is not a directory of agents.
5. The payer `send`s. The payee `wait`s until `paid` is true.

Empty DNS seeds mean you publish `addnode` peers yourself
(`docs/testnet-peers.md`).

## Discovery

Fetch these URLs on the public site:

| URL | What it is |
| --- | --- |
| `https://bitfuc.com/.well-known/bitfuc.json` | Payment-method descriptor |
| `https://bitfuc.com/pay.json` | Same file |
| `https://bitfuc.com/robots.txt` | Sitemap pointer |

An invoice you *share* is a JSON object with `"type":"bitfuc-invoice"` plus a
`bitfuc:` URI.

This site still does **not** list live wallets. Publishing *your* invoice
is how others find *you*. bitfuc.com only teaches the format.

## What we will not add

- A hosted balance or keys on bitfuc.com
- A global directory of operators
- A premine or extra subsidy for bots
- Merge-mining so a Bitcoin miner earns FUC for free
- Opening RPC to the public internet

## Tooling

`contrib/bitfuc/agent.py` commands: `init`, `status`, `receive`, `invoice`, `wait`,
`payments`, `mine`, `send`. Parse JSON. Do not scrape the brochure site for a tip
or a price.
