# BITFUC monetary policy (D3)

This is the public-net money rule. It is **not** a price forecast.
Genesis remains unspendable (D4). Changing these numbers after people have
synced a public net is a new coin.

Regtest keeps the laboratory schedule (50 FUC, halving every 150 blocks, no
fee burn) so inherited tests stay honest.

## What we are not doing

Minting an extra 2% of every transfer would inflate supply without bound and
would pay people to spam the chain. That is not implemented.

## Public nets (`bitfuc-main`, `bitfuc-test`)

| Parameter | Value | Why |
| --- | --- | --- |
| Unit | 1 FUC = **100,000,000 bits** | The atom is a *bit*, not a sat. Fee rates are `bit/vB`. |
| Block interval | **2 minutes** | Five times Bitcoin’s 10-minute spacing. First confirmation is faster; 5× more block space per hour keeps fees lower when the net is busy. |
| Hard cap | **1,000,000,000 FUC** | Finite. More units than 21 million so hobby balances are not tiny fractions, not “infinite money” |
| Issuance years | 50 | 2% of the *cap* per year, then **zero** new subsidy |
| Blocks in that era | 13,140,000 | 50 × 262,800 two-minute years (365-day year) |
| First-era block reward | ≈ **76.1035 FUC** | Cap divided evenly across those blocks |
| After height 13,140,000 | 0 subsidy | Supply cannot grow from mining |
| Fee burn | **2% of transaction fees** | Usage is slightly deflationary; miners still receive 98% of fees + subsidy |
| Default min relay / wallet fee | **0.010 bit/vB** (10 bits/kvB) | Bitcoin Core defaults are 0.1 sat/vB relay and 1 sat/vB wallet. BITFUC’s floor is 100× lower than that wallet default. |
| Premine | 0 | Genesis coinbase is `OP_RETURN` and not in the UTXO set |
| Coinbase maturity | 100 blocks (~3.3 hours) | Same 100-block rule; wall-clock is shorter because blocks are 2 minutes |

Height 0 (genesis) still encodes 50 FUC on the unspendable `OP_RETURN` output
so the frozen genesis block connects. That output is **not** in the UTXO set
and is **not** part of the 1e9 cap. Heights 1 through 13,140,000 pay the even
split (a remainder of 1 bit on the first `cap % blocks` heights so the
sum of spendable subsidies is exactly 1e9 FUC). After that, only already-mined
coins exist; 2% of later fees are destroyed.

Difficulty on public nets is **ASERT** (2-day half-life, genesis anchor). See
`docs/pow.md`. The 2016-block timespan field remains for BIP9 periods and for
regtest’s inherited DAA.

## Inflation, then deflation

- **Years 1–50:** new coins enter only as mature coinbases. Nominal issuance
  is 20 million FUC per year (2% of the *cap*), not 2% of whatever is already
  circulating. Early years therefore inflate faster relative to the small
  circulating stock; later years approach 2% of a nearly full cap, then stop.
- **After year 50:** subsidy is 0. Circulating supply can only stay flat or
  **fall** when people pay fees (2% of those fees are burned).
- Lost keys are a further, unmeasured sink. We do not pretend to count them.

## Testnet

`bitfuc-test` uses the same schedule so practice matches the intended public
rule. Test coins still have **no value**. Anyone who mined under an older
subsidy or 10-minute rule must reset the datadir; that testnet had no public
peers.

## Public chain

`bitfucd -chain=main` starts. RandomX and ASERT are in the binary. DNS/fixed
seeds stay empty until independent operators publish `addnode` hosts. That is
not a fake peer list. Checklist: `docs/launch.md`. Threat model: `docs/security.md`.
