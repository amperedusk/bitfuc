# BITFUC genesis

This file records independently generated genesis blocks. Anyone cloning the
repository can reproduce the hashes with:

```bash
python3 contrib/bitfuc/genesis.py
```

The generator first reproduces Bitcoin’s published genesis (hash
`000000000019d668…`, merkle `4a5e1e4b…`) to prove the serializer matches
Bitcoin Core, then emits BITFUC parameters. Bitcoin’s coinbase text is **not**
used for BITFUC.

Coinbase outputs are `OP_RETURN OP_PUSHDATA("BITFUC")`. Combined with Bitcoin
Core’s rule that genesis outputs are not inserted into the UTXO set, **no
developer coins** are created.

Header `nBits` is also pushed in the coinbase (unlike Bitcoin Core, which
hardcodes `486604799` even on test networks).

Time base: `1755788400` (2026-08-21 15:00:00 UTC).

## bitfuc-regtest (frozen for local development; resettable)

| Field | Value |
| --- | --- |
| Coinbase message | `BITFUC regtest -- local development chain.` |
| nTime | 1755788400 |
| nBits | `0x207fffff` |
| nNonce | 0 |
| nVersion | 1 |
| Previous block | `0000000000000000000000000000000000000000000000000000000000000000` |
| Merkle root | `bfe26f333a0be506cd4739fec4c079c36245b1a71fced05fd1175bfecd0a530c` |
| Block hash | `36dd99e42f28638b0c4c26c43c4c57ec9edba5fb713011b0795df00d067329d5` |
| P2P magic | `96 79 32 83` (`SHA256d("bitfuc-regtest-magic-v1")[0:4]`) |
| P2P / RPC | 17444 / 17443 |
| Bech32 HRP | `fucrt` |

## bitfuc-test (public test identity; TEST COINS — NO VALUE)

Published so operators can share one genesis. **Not money.** Changing these
bytes later is a new testnet. Operator notes: `docs/testnet.md`.

| Field | Value |
| --- | --- |
| Coinbase message | `BITFUC testnet -- TEST COINS -- NO VALUE.` |
| nTime | 1755788401 |
| nBits | `0x207fffff` |
| nNonce | 1 |
| Merkle root | `4f01fe9b1f9336878b1b8fd346c8034c6d9fd9769a9614e3e73097aff98f37a3` |
| Block hash | `21374e341b93a54c0899595c8118ade1ee4d3439a750755949167202be8aef2c` |
| P2P magic | `83 30 6d c4` |
| P2P / RPC | 27333 / 27332 |
| Bech32 HRP | `tfuc` |

## bitfuc-main — NOT FROZEN / NOT LAUNCHED

A draft genesis exists in `src/kernel/chainparams.cpp` so `CMainParams` can be
constructed (P2P magic comparison). **`bitfucd` refuses to start mainnet.**

Do not mine it. Easy `nBits` (`0x207fffff`) is a placeholder, not a security
parameter. PoW algorithm, difficulty adjustment, and subsidy for public
networks remain open (`docs/open-decisions.md`).

| Field | Draft value |
| --- | --- |
| Coinbase message | `BITFUC -- The cryptocurrency nobody asked for.` |
| nTime | 1755788402 |
| nBits | `0x207fffff` (placeholder) |
| nNonce | 2 |
| Merkle root | `29cf53d71101bb367f2965c60a2a1dd3d83f4b36fee4ea2fb33b8937e263ab24` |
| Block hash | `15f3f5e8e0e0777c7e99c4b5559c23f7ace26cb51a9498173a558e10b468456b` |
| P2P magic | `82 43 ac 07` |
| P2P / RPC | 17333 / 17332 |
| Bech32 HRP | `fuc` |

Changing these bytes later is allowed until `docs/launch.md` says mainnet is
frozen. After a public launch, changing them is a new coin.
