# BITFUC: An Independently Identified Instance of Nakamoto Electronic Cash

**Working paper.** Not a prospectus. Not an offering of securities. Not a claim that FUC is money, legal tender, or a store of value.

| | |
| --- | --- |
| Protocol name | BITFUC |
| Unit name | FUC |
| Implementation | Bitcoin Core v31.1 derivative (`bitfucd`) |
| Status | `bitfuc-regtest` operational locally. Public testnet not operating. **Mainnet not launched.** |
| License | MIT, retaining Bitcoin Core copyright notices |
| Affiliation | None. The MIT *license* is not the Massachusetts Institute of Technology. |

**Abstract.**
A digital bearer instrument that can be transferred without a trusted bookkeeper requires three things that ordinary databases do not provide: a rule for who may create new units, a rule that forbids spending the same unit twice, and a rule for deciding which history is canonical when two conflicting histories are offered. Nakamoto (2008) gave a construction that meets those requirements by combining a UTXO transaction algebra with a most-work chain of proof-of-work headers. BITFUC is not a new consensus theorem. It is an *independently identified instance* of that construction: the same validation kernel, a disjoint network identity, a genesis coinbase that does not enter the UTXO set, and a written policy of zero developer allocation. This paper states the model with the care a mathematician would demand, records the parameters that exist, and marks the parameters that do not. It does **not** argue that BITFUC will displace existing money, that FUC has a price, or that a public chain is running.

**Keywords.** electronic cash; UTXO; Nakamoto consensus; proof of work; monetary parameterization; network identity; premine; Bitcoin Core.

---

## 1. Introduction

Money, in the narrow operational sense used here, is a *coordination device*: a widely accepted object that extinguishes obligations and is itself accepted in further exchange (Jevons 1875; Menger 1892). Modern retail money is almost entirely *intermediated*. A bank or a card network keeps a ledger; the user’s “balance” is an IOU against that ledger; transfer is an instruction to the intermediary. That arrangement is efficient. It is also a trust assumption. The intermediary may freeze, reverse, inflate by policy, fail operationally, or be compelled.

Electronic *cash* is the attempt to recover the bearer property of notes without a note-issuer: the right to transfer is the knowledge of a secret, and the public record of which secrets still control which units is maintained by a protocol rather than a firm.

Chaum (1982) showed that a blind-signature mint can issue unlinkable electronic coins, but the mint remains a trusted issuer and a single point of failure. Dai (1998) and Back (2002) sketched computational cost as a way to issue tokens without a mint. Haber and Stornetta (1991) showed how to time-stamp a document stream with hash pointers. Nakamoto (2008) composed these ideas into a system in which (i) units are unspent transaction outputs, (ii) authorization is a digital signature under a public verification key, and (iii) the canonical history is the chain of headers that represents the most accumulated proof of work.

BITFUC stands in that line. The joke is the name. The engineering claim is narrower and, we think, more honest:

1. The validation rules are those of Bitcoin Core 31.1, not a reimplementation of secp256k1 or Script.
2. The *network* is not Bitcoin. Genesis, magic bytes, ports, address prefixes, and datadir are disjoint.
3. No developer output is inserted at genesis. The genesis coinbase is `OP_RETURN` and, as in Bitcoin, genesis outputs are not placed in the UTXO set.
4. Mainnet is not launched. The process `bitfucd` refuses `-chain=main` until a written freeze.

A paper that announced “a new money” while those four sentences were false would be a marketing document. This is not that paper.

### 1.1 What is claimed

We claim only what can be checked from source and from a local node:

- There exists a C++ implementation, derived from Bitcoin Core tag `v31.1`, that validates a BITFUC *regtest* chain.
- Three local nodes can mine, transfer, restart, and resynchronize to a common tip (acceptance criteria in the repository).
- Address, magic, and port spaces are constructed so as not to collide with Bitcoin’s.
- The proposed (not frozen) issuance schedule is the Bitcoin geometric subsidy, renamed.

### 1.2 What is not claimed

We do not claim that BITFUC is legal tender, that FUC has or will have exchange value, that the system is a substitute for bank deposits, that SHA-256d on a low-hashrate public net is secure against existing ASIC fleets, or that this project is affiliated with any university.

---

## 2. Related work

**Blind-signature cash.** Chaum (1982, 1988) and Chaum, Fiat, and Naor (1988) give anonymous electronic cash under a mint. The mint is the money. BITFUC has no mint.

**Proof of work.** Dwork and Naor (1992) and Back (2002) treat computational puzzles as a scarce resource. Nakamoto uses SHA-256d on a block header as the puzzle.

**Hash-linked time-stamping.** Haber and Stornetta (1991); Bayer, Haber, and Stornetta (1993). The Bitcoin header chain is a public time-stamp of a Merkle root of transactions.

**Bitcoin and its backbone.** Nakamoto (2008); Garay, Kiayias, and Leonardos (2015) formalize common prefix and chain quality under a bounded-delay, honest-majority-of-resource model. BITFUC inherits that model; it does not improve the theorems.

**Script and Taproot.** Bitcoin’s script system, SegWit (BIP141), and Taproot (BIP340/341/342) are used as shipped in Core 31.1. We do not propose a new opcode.

**Altcoins as reparameterizations.** Most “new coins” are Bitcoin’s construction with a different genesis and, sometimes, a different puzzle or retarget. Intellectual honesty requires saying so. BITFUC is in that class. Its distinction, if any, is *identification and policy*: a disjoint identity, an unspendable genesis, empty seeds, and a refusal to start an unfrozen mainnet.

---

## 3. Preliminaries

### 3.1 Notation

Let \(\{0,1\}^*\) be finite binary strings. Let \(\mathrm{SHA256}: \{0,1\}^* \to \{0,1\}^{256}\) be the SHA-256 compression as standardized. Write

\[
\mathrm{SHA256d}(x) := \mathrm{SHA256}(\mathrm{SHA256}(x)).
\]

Interpret \(\{0,1\}^{256}\) as an integer in \([0, 2^{256})\) in the usual big-endian convention used by Bitcoin headers. A *target* \(T\) is an integer in that range. A header \(h\) *meets* \(T\) when \(\mathrm{SHA256d}(h) \le T\).

Let \(\mathbb{G}\) be the secp256k1 elliptic-curve group, of prime order \(n\), with generator \(G\). A secret key is \(d \in \{1,\ldots,n-1\}\); the public key is \(P = dG\). ECDSA and BIP340 Schnorr are used as specified; we treat them as EUF-CMA secure in the usual models. We do **not** introduce a new signature scheme.

Amounts are integers. Write \(\mathsf{COIN} := 10^{8}\). One FUC, if the proposed parameterization is adopted, is \(\mathsf{COIN}\) base units. All conservation laws are in base units.

### 3.2 Cryptographic assumptions (inherited)

**Assumption 1 (hash).** \(\mathrm{SHA256}\) is collision-resistant and, for the purpose of proof of work, preimage-hard on the header space in the sense that finding \(h\) with \(\mathrm{SHA256d}(h) \le T\) requires \(\Theta(2^{256}/T)\) evaluations in expectation for random search.

**Assumption 2 (signatures).** Forged witnesses for secp256k1 ECDSA or BIP340 Schnorr, without the corresponding secret, are infeasible.

These are the same assumptions Bitcoin makes. BITFUC adds none and removes none.

---

## 4. The intermediated-money problem

### 4.1 Ledgers as functions

**Definition 1 (account ledger).** An account ledger is a map \(B: I \to \mathbb{Z}_{\ge 0}\) from identifiers to balances, together with an authorized operator who may replace \(B\) by \(B'\).

A payment \(i \to j\) of amount \(v\) is the operator’s update \(B'(i)=B(i)-v\), \(B'(j)=B(j)+v\), provided \(B(i)\ge v\). The *right to pay* is the operator’s willingness. That is the trust assumption.

**Definition 2 (bearer instrument).** A bearer instrument is a pair \((s, V)\) where \(s\) is a secret and \(V\) is a publicly checkable predicate such that knowledge of \(s\) is necessary and sufficient (under Assumption 2) to authorize a transfer of the associated units.

Electronic cash is the problem of maintaining a *public* \(V\) that updates without a privileged operator, while preserving conservation of units and forbidding double-spends.

### 4.2 Why “alternative money” is a property of use, not of a repository

A protocol can at most supply a *candidate* bearer instrument. Whether it is money is a fact about *acceptance*: do counterparties extinguish debts in it? That fact is empirical and, for BITFUC, presently false. There is no public chain, no observed price, and no claim of legal-tender status. Sections 5–7 describe the candidate. Section 13 repeats the restriction.

---

## 5. Transactions as a conservative rewrite system

### 5.1 Coins

**Definition 3 (output).** An output is a pair \(o = (v, \pi)\) where \(v \in \mathbb{Z}_{\ge 0}\) is a value in base units and \(\pi\) is a locking script (a predicate on witnesses).

**Definition 4 (outpoint).** An outpoint is a pair \((txid, i)\) naming the \(i\)-th output of the transaction with identifier \(txid\).

**Definition 5 (UTXO set).** At a given chain state, the UTXO set \(U\) is a finite map from outpoints to outputs. A coin is an element of \(U\).

### 5.2 Transactions

**Definition 6 (transaction).** A transaction \(tx\) consists of:

1. a list of inputs, each an outpoint together with a witness;
2. a list of outputs \((v_j, \pi_j)\);
3. version and lock-time fields as in Bitcoin.

Write \(\mathrm{in}(tx)\) and \(\mathrm{out}(tx)\) for the input outpoints and created outputs. Write \(v_{\mathrm{in}}(tx)\) and \(v_{\mathrm{out}}(tx)\) for the sum of input and output values (coinbase excepted).

**Definition 7 (conservation).** A non-coinbase transaction is *conservative* when \(v_{\mathrm{in}}(tx) \ge v_{\mathrm{out}}(tx)\). The difference is the *fee*, available to the miner of the including block.

**Definition 8 (authorization).** An input is authorized when the witness satisfies the locking script \(\pi\) of the referenced output, under the script rules of Bitcoin Core 31.1 (including SegWit and Taproot).

**Definition 9 (validity against \(U\)).** \(tx\) is valid against \(U\) when every input outpoint is in \(U\), every input is authorized, conservation holds, and script/standardness rules used by the node for *consensus* (as opposed to mere relay policy) are satisfied.

Applying a valid \(tx\) replaces \(U\) by

\[
U' = \bigl(U \setminus \mathrm{in}(tx)\bigr) \cup \{\text{new outpoints of } tx\}.
\]

**Remark 1.** This is a linear rewrite system on a multiset of coins. It is not an account map. There is no identifier whose “balance” is a primitive; a balance is a *query*, the sum of \(v\) over outputs whose \(\pi\) one can satisfy.

### 5.3 Coinbase and maturity

A *coinbase* transaction has no UTXO inputs. It may create outputs whose total value is at most \(\mathrm{subsidy}(H) + \mathrm{fees}\), where \(H\) is the block height and \(\mathrm{subsidy}\) is the issuance function (Section 9). Those outputs are not spendable until \(H + 100\) on the same chain (maturity). This delay is a reorg-safety parameter, not a mystery.

**Definition 10 (genesis exception).** The unique height-0 coinbase is **not** inserted into \(U\). Combined with an `OP_RETURN` payload, it creates no spendable developer units.

That is the entire premine policy. If a later version inserts a spendable genesis output, that version is a different instrument and must say so.

---

## 6. The ledger as a most-work tree

### 6.1 Blocks

**Definition 11 (header).** A header is an 80-byte structure: version, previous-header hash, Merkle root of the block’s transactions, timestamp, compact target (`nBits`), and nonce.

**Definition 12 (block).** A block is a header together with a transaction list whose Merkle root matches the header, whose first transaction is a coinbase of legal subsidy, and whose remaining transactions are valid sequentially against the UTXO set inherited from the parent.

**Definition 13 (chain).** A chain is a finite sequence of blocks \(B_0, B_1, \ldots, B_H\) where \(B_0\) is the genesis block of the network and each subsequent header commits to the previous header hash.

### 6.2 Work

Let \(T(B)\) be the target encoded by \(B\)’s `nBits`. The *work* of \(B\) is, as in Bitcoin,

\[
w(B) = \left\lfloor \frac{2^{256}}{T(B)+1} \right\rfloor
\]

(up to the exact integer convention in `GetBlockProof`). The work of a chain is \(\sum w(B_i)\).

**Definition 14 (canonical chain).** Among headers a node has validated, the canonical chain is a chain of valid blocks from genesis with *maximal total work*. Ties are broken as in Bitcoin Core (first-seen / tip-work comparison as implemented).

This is Nakamoto consensus. It is not voting. It is not proof of stake. It is not a committee.

### 6.3 Reorganizations

If a node later observes a valid chain with more work, it *reorganizes*: it disconnects blocks from the old tip back to the fork point and connects the new fork. Outputs that existed only on the discarded fork cease to be in \(U\). Confirmations are a *heuristic* (depth under the current tip), not a mathematical finality gadget.

**Remark 2.** “\(k\) confirmations” is the statement: an adversary who would reverse the payment must produce a competing fork whose work exceeds that of the \(k\) subsequent blocks, starting from a disadvantage. Under an honest majority of *hashrate*, the probability of doing so falls exponentially in \(k\) (Nakamoto 2008, §11). The hypothesis is about hashrate, not about the number of GitHub stars.

---

## 7. Difficulty, work, and the public-net objection

Regtest uses a trivial target so that `generatetoaddress` succeeds on a laptop. That is a laboratory parameter.

Bitcoin’s production difficulty adjustment retargets every 2016 blocks toward a ten-minute spacing. On a *new* SHA-256d chain the hashrate is, for a long time, negligible relative to existing SHA-256d ASIC capital. Two consequences are not optional:

1. **51% is cheap.** An adversary who already points ASICs at Bitcoin can, at small opportunity cost, outwork a hobby BITFUC net, reorganize, and double-spend.
2. **2016-block retargeting is a poor fit** for a low, jumpy hashrate: a spike mines a large number of blocks at an obsolete target; a subsequent drought stalls the chain.

These are recorded as open decisions D1 and D2. This paper **does not freeze** SHA-256d or the Bitcoin DAA for mainnet. Anyone who ships a public BITFUC mainnet on SHA-256d without stating the ASIC risk is omitting the security model.

**Remark 3.** Changing the puzzle to an established CPU-oriented function (for example RandomX) is a *protocol* decision, not a website decision. It is a large consensus patch. It is not “inventing cryptography” if the function is specified and reviewed; it is also not free.

---

## 8. Scripts, witnesses, and names of coins

BITFUC uses Bitcoin Core 31.1 script: P2PKH, P2SH, P2WPKH, P2WSH, P2TR, as implemented. Default addresses on BITFUC networks are native SegWit with *distinct* human-readable parts:

| Network | HRP | Example form |
| --- | --- | --- |
| bitfuc-main (gated) | `fuc` | `fuc1…` |
| bitfuc-test | `tfuc` | `tfuc1…` |
| bitfuc-regtest | `fucrt` | `fucrt1…` |

Bitcoin uses `bc`, `tb`, `bcrt`. Base58 version bytes and extended-key version bytes are likewise disjoint. The point is *non-confusion*: a BITFUC string must not be a valid Bitcoin payment destination under Bitcoin Core, and conversely.

**Definition 15 (network identity).** A network identity is a tuple

\[
\bigl(\text{genesis header},\; \text{magic}_4,\; \text{ports},\; \text{HRP},\; \text{Base58 versions},\; \text{datadir}\bigr).
\]

Two identities define two coins, even if the script interpreter is the same program.

User-agent: `/Bitfuc:0.1.0/`. Configuration file: `bitfuc.conf`. Process names: `bitfucd`, `bitfuc-cli`.

---

## 9. Monetary parameterization

Issuance is a function of height, not of a committee minute.

### 9.1 Proposed function (not frozen for mainnet)

Let \(H \ge 1\) be the block height (genesis creates no spendable subsidy). Let

\[
\mathrm{era}(H) = \left\lfloor \frac{H}{210000} \right\rfloor, \qquad
\mathrm{subsidy}(H) = \left\lfloor \frac{50 \cdot \mathsf{COIN}}{2^{\mathrm{era}(H)}} \right\rfloor
\]

with the usual integer vanishing after a finite number of halvings. The implied *nominal* cap is

\[
\sum_{e=0}^{\infty} 210000 \cdot \left\lfloor \frac{50\cdot\mathsf{COIN}}{2^{e}} \right\rfloor \le 21\cdot 10^{6}\cdot\mathsf{COIN}.
\]

Integer division makes the realized sum strictly less than \(21\times 10^{6}\) FUC, as in Bitcoin. This is not mysticism. It is a geometric series with a floor.

**Proposed spacing.** Ten minutes per block on a public net, if that net is ever frozen with this subsidy. Coinbase maturity: 100 blocks.

**Rationale, without romance.** The numbers reuse Bitcoin Core’s amount type and subsidy routine so that the first implementation can be tested against a known shape. They are **not** an argument that FUC is “like Bitcoin” economically, that 21 million is optimal, or that scarcity implies price.

### 9.2 Fees

After subsidy tends to zero, block space is allocated by fees under inherited mempool policy. We do not invent a fee market in this paper. We do not promise that fees will be “enough” to secure a public chain. That is an open empirical question even for Bitcoin; it is unanswerable for an unlaunched BITFUC mainnet.

### 9.3 Allocation

\[
\text{developer premine} = 0, \qquad \text{hidden allocation} = \text{forbidden}.
\]

Units, if a public chain is launched under this policy, enter \(U\) only as mature coinbases of mined blocks and as their subsequent transfers. A faucet, if any, belongs on *testnet* and must be labeled **NO VALUE**.

---

## 10. BITFUC as a specified instance

### 10.1 Networks

| Name | Role |
| --- | --- |
| `bitfuc-regtest` | Laboratory. Instant blocks. Identity frozen for development; resettable. |
| `bitfuc-test` | Intended public test; **test units have no value.** Not operating as a public net at the date of this paper. |
| `bitfuc-main` | Intended public net. **Not frozen. Process will not start.** |

### 10.2 Magics and ports

Magic bytes are \(\mathrm{SHA256d}(\text{UTF-8 label})[0..4)\):

| Network | Label | Magic | P2P | RPC |
| --- | --- | --- | --- | --- |
| main (gated) | `bitfuc-main-magic-v1` | `82 43 ac 07` | 17333 | 17332 |
| test | `bitfuc-test-magic-v1` | `83 30 6d c4` | 27333 | 27332 |
| regtest | `bitfuc-regtest-magic-v1` | `96 79 32 83` | 17444 | 17443 |

Bitcoin’s 8333 / 18333 / 18444 are unused.

### 10.3 Genesis (regtest, frozen for local use)

Reproduce with `python3 contrib/bitfuc/genesis.py`. The generator first reproduces Bitcoin’s published genesis, then emits BITFUC headers. Bitcoin’s coinbase *text* is not reused.

| Field | bitfuc-regtest |
| --- | --- |
| Coinbase message | `BITFUC regtest -- local development chain.` |
| nTime | `1755788400` (2026-08-21 15:00:00 UTC) |
| nBits | `0x207fffff` |
| nNonce | 0 |
| Merkle root | `bfe26f333a0be506cd4739fec4c079c36245b1a71fced05fd1175bfecd0a530c` |
| Block hash | `36dd99e42f28638b0c4c26c43c4c57ec9edba5fb713011b0795df00d067329d5` |

Testnet and draft main genesis bytes are recorded in `docs/genesis.md`. Draft main `nBits` is a placeholder. Mining it is not a launch.

### 10.4 Seeds and infrastructure

DNS seeds and fixed seeds are empty. A single unpublished VPS is not part of the design. Discovery on regtest is `addnode`. A public net, if launched, must not depend on one operator to validate or to mine.

Checkpoints, `assumevalid`, and AssumeUTXO snapshots contain **no Bitcoin state**. Importing Bitcoin’s assumevalid would cause a BITFUC node to skip validation toward the wrong coin.

### 10.5 Mining interface

The node exposes `getblocktemplate` and `submitblock`. On regtest, `generatetoaddress` is the supported laboratory miner. Compatibility with Bitcoin *mining software* requires that the software speak BITFUC identity; pointing a Bitcoin miner at `bitfucd` without that is not a BITFUC block.

---

## 11. Implementation

The implementation is a git history starting from the official Bitcoin Core tag `v31.1`, plus BITFUC identity commits. Consensus-critical code paths (libsecp256k1, script, UTXO, mempool, reorg) are not rewritten for branding.

The website is static HTML. It is not a validator. It does not display a tip. An explorer that is not bound to a live `bitfucd` RPC is, in the sense of this paper, a fiction.

Wallets are descriptor wallets inside `bitfucd`. This paper’s authors (and this website) are not a custodian.

---

## 12. Security discussion

We separate *local* security (the laboratory) from *public* security (a hypothesized mainnet).

**Local.** On regtest, difficulty is trivial. An attacker on the same machine can rewrite the chain. That is not a defect; it is the point of a test network.

**Public (hypothetical).** Security reduces to:

1. Assumptions 1–2;
2. an honest majority of the *puzzle resource* (hashes per second for SHA-256d, or the corresponding resource for another puzzle);
3. enough independent full nodes to detect invalid blocks;
4. no hidden assumevalid of a foreign chain;
5. no premine that concentrates initial \(U\).

Item 2 is the difficult one. For SHA-256d it is, today, implausible for a new coin. This is not a footnote.

**Privacy.** A UTXO graph is not “untraceable.” Cluster analysis applies. We do not claim otherwise.

**Bridges.** A lock-and-mint bridge is a custodian plus a consensus assumption on two nets. Out of scope. Wrapped FUC on another chain is a different instrument.

---

## 13. What this paper does not establish

The following sentences are **false** if asserted as theorems about the world in 2026:

1. “BITFUC is money.”
2. “FUC has a market price.”
3. “BITFUC is a safe store of value.”
4. “BITFUC is as secure as Bitcoin.”
5. “Mainnet is live.”
6. “This paper is an offering or a solicitation.”
7. “The authors are affiliated with MIT or any central bank.”

What the paper *does* establish, in the modest sense of a specification plus a reproducible program, is that a Bitcoin-derived electronic-cash *construction* can be instantiated with a disjoint identity and a zero-allocation genesis, and that the laboratory instance works.

Whether anyone should *use* such an instance as money is not a lemma. It is a social and legal question, and for BITFUC it is premature.

---

## 14. Open problems (protocol, not marketing)

These are the stops recorded in `docs/open-decisions.md`. They are not resolved by typesetting.

**D1.** Puzzle for a public net: SHA-256d (accept ASIC 51% risk in a launch document) versus an established non-SHA-256d puzzle.

**D2.** Difficulty adjustment: Bitcoin’s 2016-block rule versus a fast absolute-time rule (e.g. ASERT) on mainnet; min-difficulty on testnet only.

**D3.** Freeze or revise the subsidy table before genesis.

**D4.** Keep genesis unspendable (recommended) or disclose a premine.

Until D1–D4 are written as decisions, a mainnet genesis is a category error.

Further problems that are not “features”:

- Fee security as subsidy vanishes (open even for Bitcoin).
- Whether a native exchange, if ever designed, should be a book, an HTLC swap, or neither (Phase 8; not Uniswap-on-UTXO).
- How to publish seeds without a single operator remaining a liveness dependency.

---

## 15. Conclusion

Nakamoto electronic cash is a conservative UTXO rewrite system whose canonical history is the most-work header chain. BITFUC is that system, identified so that it cannot be mistaken for Bitcoin, allocated so that genesis creates no developer coins, and gated so that an unfrozen mainnet cannot be started by accident.

That is a complete description. It is less exciting than a monetary manifesto and more accurate. The name is ridiculous. The node is required to be otherwise.

If a later document announces a launch, it must publish time, frozen parameters, and any mining that occurred before the announcement. Until then, the only honest public statement about BITFUC as money is that **it is not, yet, money**. It is a specified construction and a working laboratory chain.

---

## Appendix A. Reproduction

```text
python3 contrib/bitfuc/genesis.py
cmake -B build -DENABLE_IPC=OFF -DBUILD_GUI=OFF -DINSTALL_MAN=OFF
cmake --build build --target bitcoind bitcoin-cli
./scripts/regtest/acceptance.sh
```

CMake target names remain `bitcoind` / `bitcoin-cli`. Output names are `bitfucd` / `bitfuc-cli`.

---

## Appendix B. Document control

| Field | Value |
| --- | --- |
| Title | BITFUC: An Independently Identified Instance of Nakamoto Electronic Cash |
| Date | 2026-08-22 |
| Version | 0.1 (working paper) |
| Canonical file | `docs/whitepaper.md` |
| Website rendering | `/whitepaper` |
| Supersedes | none |
| Controlling legal text | `docs/legal-notice.md` |
| Controlling genesis table | `docs/genesis.md` |
| Controlling open questions | `docs/open-decisions.md` |

---

## References

Back, A. (2002). *Hashcash — A Denial of Service Counter-Measure.*

Bayer, D., Haber, S., and Stornetta, W. S. (1993). Improving the efficiency and reliability of digital time-stamping. In *Sequences II*.

Bitcoin Core developers (2026). *Bitcoin Core* v31.1. https://github.com/bitcoin/bitcoin

Chaum, D. (1982). Blind signatures for untraceable payments. *Crypto ’82*.

Chaum, D. (1988). Privacy protected payments: Unconditional payer and/or payee untraceability. In *Smart Card 2000*.

Chaum, D., Fiat, A., and Naor, M. (1988). Untraceable electronic cash. *Crypto ’88*.

Dai, W. (1998). *b-money.*

Dwork, C. and Naor, M. (1992). Pricing via processing or combatting junk mail. *Crypto ’92*.

Garay, J., Kiayias, A., and Leonardos, N. (2015). The Bitcoin backbone protocol: Analysis and applications. *Eurocrypt 2015*.

Haber, S. and Stornetta, W. S. (1991). How to time-stamp a digital document. *Journal of Cryptology*.

Jevons, W. S. (1875). *Money and the Mechanism of Exchange.*

Menger, C. (1892). On the origin of money. *Economic Journal*.

Nakamoto, S. (2008). *Bitcoin: A Peer-to-Peer Electronic Cash System.*

Wuille, P., Nick, J., and Ruffing, T. (2020). BIP 340: Schnorr Signatures for secp256k1.

Wuille, P., Nick, J., and Towns, A. (2020). BIP 341: Taproot; BIP 342: Validation of Taproot Scripts.

Lombrozo, E., Lau, J., and Wuille, P. (2015). BIP 141: Segregated Witness.
