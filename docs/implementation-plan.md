# Staged implementation and acceptance gates

The goal is a test-first core/central-bank payment platform with a treasury workspace and one fungible currency per issuer profile. This roadmap preserves the distinction between working laboratory code, BSV test-network execution and any future regulated system.

## Stage 0: Evidence, authority and executable invariants

**Delivered in this foundation:** public source register, institutional/legal research, architecture decisions, treasury/denomination specification, threat model, dependency-free reference ledger, adversarial tests, CLI demo and recorded live testnet read.

Acceptance: source claims have provenance and limits; exact-value conservation and supply/accounting invariants pass; no real data or secrets; no mainnet path; simulation is visible in every execution result. Actual test results are in [verification.md](testing/verification.md).

## Stage 1: BSV representation proof and offline transaction tests

**Source comparison completed; protocol selection and runtime proof remain open.** The [candidate comparison](research/token-enforcement/candidate-comparison.md) inspects 28 pinned primary source files/specifications. It shortlists regulated Mandala and an explicitly designed issuer-and-holder co-signature protocol against the issuer-ledger/anchor baseline. Plain BTMS does not meet the unchanged treasury contract. Select a test protocol only after defining authoritative monetary state and the role of issuer, holder, miners and overlays. Pin the reviewed SDK/package and encode reference vectors shared across languages.

Deliverables: currency descriptor and issuer identity specification; canonical signed instruction envelope; script/protocol specification; exact principal/carrier/fee types; independently reviewed mint/split/merge/retire validity rules; offline serialization and signature tests; negative corpus; size and fee estimates for 2,000 outputs.

Gate: prove no split/merge creates value; unapproved issuer or holder cannot authorize an operation; replay across currency/network domains fails; invalid lineage and tampered output amounts fail. No network submission is needed to finish this reasoning and test-design work.

## Stage 2: Controlled BSV test-network transaction pilot

**Open; not satisfied by the read-only observer.** Requires an explicitly selected test environment/provider, controlled test-only signing arrangement, funded test UTXOs and reviewed dependency/service terms. Do not create credentials, use a user computer or spend real money as an implicit workaround.

Deliverables: testnet-only transaction builder, signer interface, BSV fee sponsor, durable submission outbox, exact-txid receipt validation, chain observer, header/proof validation, transaction-state store and reconciliation. Record raw test transaction bytes, txid, provider response, block/proof evidence, fees and software versions without exposing private keys.

Pilot scenarios: mint → split 100.00 into 2,000 five-cent notes → merge → mixed payment → user-authorized treasury redemption → retire. Repeat with invalid signatures, duplicate submissions, two conflicting spends, insufficient fee balance, provider timeout, rejection, reorganisation and recovery. Treat each unproven enforcement layer honestly; an anchor-only pilot does not pass the token protocol gate.

Completion requires at least one verified test-network lifecycle under the selected representation, not merely a successful POST or txid string. No transaction from this stage has yet been submitted.

## Stage 3: Treasury and intermediary service boundaries

**Open.** Add authenticated roles, separate officer approval sessions, scoped mandates, expiration/revocation, HSM-compatible signer boundaries, policy versions and activation rules, multi-party holder authorization, person-level limits, appeals and participant lifecycle. Keep identity data in an explicitly governed privacy boundary.

Deliverables: private test API and treasury UI, independently reviewed permission matrix, schema and migration policy, integration contracts, error taxonomy, audit exports, observability and operator runbooks. A UI displaying an issuer's name must not be confused with issuer authorization.

Gate: authentication/authorization abuse tests, replay and race tests across service instances, policy-change tests, dependency review, privacy assessment and demonstrated reconciliation to synthetic issuer/intermediary ledgers.

## Stage 4: Durability, failures and recovery

**Open.** Move beyond one-machine correctness to controlled distributed fault testing. Establish application/node backup scope, independent checkpoints, retention, restore authorization, compromised-key rotation, recovery-case handling and safe resumption.

Gate: independently witnessed recovery objectives; no lost acknowledged economic effect; no duplicate issue/redemption; complete unresolved-outcome accounting; tested partition, stale-state, fork, disk exhaustion and region-loss behavior. Define who may pause and resume each function.

## Stage 5: End-to-end capacity validation

**Open.** Implement the [performance protocol](testing/performance-plan.md), including treasury/policy/privacy workloads and bounded output amplification. Reconcile every admitted request across failures and drains.

Gate: minimum 100,000 distinct economic payments per second at the predeclared completion boundary, with separately specified latency, errors, backlog, availability, durability and recovery acceptance criteria. A blockchain-only benchmark or batched API receipt is insufficient evidence for this complete-service gate.

## Stage 6: Jurisdiction-specific feasibility and independent assurance

**Open; not authorized as a launch.** Identify the actual issuer, legal powers, scheme operator, customer rights, intermediaries, jurisdiction, data law, financial integrity duties, supervisory expectations, dispute process, accounting standards and operational risk ownership. Review software licences, patents and procurement requirements without assuming public source access settles those issues.

Gate: institution-led legal/monetary decisions, independent security and operational assessments, documented control ownership, required authorizations and a separately approved deployment plan. This project does not certify those outcomes.

## Decisions needed before dependent work

1. Pilot instrument and responsible issuer model, including whether the first jurisdiction study is retail or wholesale.
2. The on-chain enforcement pattern versus issuer-ledger anchoring, following Stage 1 comparison.
3. Approved test-only signer and test network environment/funding path for Stage 2.
4. Scheme-specific finality, privacy, policy, redemption and recovery choices.
5. Project code licence and third-party dependency review.

Research, specification and local adversarial testing can continue independently while those choices are resolved. Network signing, credential setup, mainnet use, real value, public deployment and legal commitments require their own applicable authority.
