# CBDC research and treasury test platform

A staged research project for a **single-currency payment platform**, including a government treasury area for controlled minting and retirement, and holder-authorized splitting and merging of denominations.

**Current milestone: a local synthetic reference implementation, public primary-source research, and a read-only connection to BSV testnet.** There is no signed transaction, on-chain currency issuance, real money, public service deployment or production certification in this milestone.

## Run the first vertical slice

Python 3.12 or later; standard library only. No package installation, keys, credentials or test coins required.

```sh
python -m unittest discover -v
python -m cbdc_lab.demo
# Optional: one public read of BSV testnet status. No transaction is sent.
python -m cbdc_lab.demo --observe-testnet
```

The demo:

1. Proposes and independently approves issuance of **100.00 TUSD**, a fictional test instrument.
2. Splits it into exactly **2,000 outputs of 0.05 TUSD** without changing supply.
3. Merges those outputs back into one 100.00 output.
4. Makes a mixed-output payment: 33.35 to Bob and 66.65 back to Alice.
5. Has Bob transfer his 33.35 to treasury, then separately proposes and approves retirement.
6. Reconciles the remaining 66.65 to the simulated issuer liability and audit history.
7. Prepares an unsigned BSV testnet audit-commitment request, with broadcasting disabled.

“TUSD” is an example label, not US dollars, a US CBDC, a redeemable token or a claim on a government. One hundred dollars in the requested denomination example becomes 10,000 integer cents; five cents becomes five. The profile can change the synthetic currency, precision and minimum unit before a new ledger is created.

## What is implemented

- Treasury proposal/approval separation tied to the exact request hash
- Exact bounded integer amounts, one currency per database, supply and holding limits
- Local UTXO-like notes with ownership checks, conserved split/merge and mixed transfers
- Treasury-custody retirement, replay protection and atomic SQLite transactions
- Simulated double-entry issue/retirement journal, audit hash chain and projection reconciliation
- Restart, backup/restore, concurrent double-spend and adversarial-input tests
- BSV testnet observer and small OP_RETURN commitment-script builder

## Important limits

Actor IDs are trusted inputs to an in-process test harness; authentication, signatures, HSMs and live identity checks are not implemented. The local notes are **not BSV outpoints**, and the OP_RETURN commitment does not enforce note ownership or supply on-chain. The issue journal uses a plainly labelled test suspense account; it proves no reserve backing or external payment. A local commit is not blockchain inclusion or legal finality.

The BSV test-network transaction stage is still open. It needs a reviewed token representation, a separately controlled test-only signer, funded test UTXOs, explicit provider/network configuration and confirmation/reorganisation tests. See [staged implementation](docs/implementation-plan.md).

## Research and design map

- [Research index and provenance](docs/research/README.md)
- [Central-bank architecture and issuer liability](docs/research/central-bank/central-bank-architecture.md)
- [Governance, privacy, recovery and operations](docs/research/central-bank/operational-control-baseline.md)
- [Current BSV integration findings](docs/research/bsv-integration.md)
- [Token enforcement: BTMS, regulated Mandala, co-signing and covenants](docs/research/token-enforcement/candidate-comparison.md)
- [Architecture decisions](docs/architecture/decisions.md)
- [Treasury and denomination specification](docs/architecture/treasury-and-denominations.md)
- [Threat model](docs/architecture/threat-model.md)
- [Implementation stages and acceptance gates](docs/implementation-plan.md)
- [Tests and recorded results](docs/testing/verification.md)
- [Performance acceptance protocol](docs/testing/performance-plan.md)

The 100,000 TPS operating floor is a project requirement. Official reports of Teranode's million-plus-TPS test-network work support blockchain capacity research; they are not a measured result for this application. No throughput target has been demonstrated by this reference ledger.

The focused source review identifies regulated `tm_mandala` as a closer existing-code candidate than plain BTMS. Its supply and recovery rules are overlay-enforced above ordinary Bitcoin locks. It still needs independent treasury approvals, issuer-only retirement and adversarial bypass/recovery tests before it could satisfy this project's contract. The comparison records these boundaries rather than treating a token library as a completed CBDC.

## Repository and rights

This repository was public and empty at intake on 7 October 2026. Public visibility has been preserved. Research here uses public sources and bounded original summaries; private source manuscripts and personal data are excluded. No licence has yet been selected for project-authored code. Referenced third-party software and documents retain their own terms; citation is not a licence grant, patent clearance or government authorization.
