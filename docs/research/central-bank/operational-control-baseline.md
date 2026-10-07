# Operational control baseline

Research snapshot: 2026-10-07. This is a proposed assurance checklist, not evidence that any control has been implemented.

## 1. Governance comes before privileged functions

PFMI provides an important assessment lens for legal basis, governance, risk, finality and operational arrangements. Its formal applicability depends on the infrastructure and the competent authorities. Referencing it is not certification. [CB-006](https://www.bis.org/publications/principles-financial-market-infrastructures.pdf)

### Proposed authority register

For each consequential function, document:

- The institution with legal authority and the instrument granting it
- The accountable policy owner and operating entity
- The individuals/roles permitted to request, approve, execute and review
- The permitted scope, monetary exposure, expiry and escalation route
- The technical credential or signing policy implementing that permission
- The evidence retained and the independent party reviewing its use

Apply this to issuance, redemption, participant admission, policy changes, freezes, key recovery, software upgrades, emergency suspension and restoration. Keep monetary approval, operational execution and audit separable. A threshold signature proves that a technical threshold was met; it does not prove those signers had the requisite public authority.

For the requested government-controlled treasury area, maintain a dedicated mint/retire permission set and approval chain. Record the central-bank legal issuer separately. Holders receive authority to split or merge their own available denominations, conserving exact value, rather than access to supply-changing treasury functions. Include cross-role escalation, unauthorised retirement and denomination-based limit evasion in the negative tests.

Produce a versioned scheme rulebook, operator handbook, participant agreement model, change procedure and incident responsibility matrix. These are research templates until the relevant institutions review and adopt them. Do not invent an issuer or regulator to fill an empty role.

## 2. Define the privacy promise as a threat model

The 2024 joint design report treats privacy as a combination of technology, operating arrangements and policy, with compliance and fraud trade-offs. The ECB's intended online design illustrates separation between intermediary identity data and Eurosystem transaction visibility. Neither statement proves privacy for this repository. [CB-004, section 3a](https://www.bis.org/publications/central-bank-digital-currencies-system-design.pdf), [CB-011](https://www.ecb.europa.eu/euro/digital_euro/features/privacy/html/index.en.html)

### Proposed data map

For identity documents, aliases, account identifiers, device IDs, balances, transaction amounts, counterparties, timestamps, location-derived data, logs and backups, record:

1. Which party collects the data and for what purpose
2. Whether the core actually needs it
3. Which parties can read, correlate, export or decrypt it
4. Retention and deletion obligations
5. Disclosure authority and review procedure
6. Recovery and breach implications
7. What users are told in understandable language

Minimise and segregate information before selecting sophisticated cryptography. Pseudonymous addresses can remain linkable. Encryption at rest does not prevent an authorised operator from reading decrypted data. A zero-knowledge proof may hide its witness while leaving transaction timing, amount, counterparties or network metadata exposed.

For every privacy claim, name the adversary: another user, merchant, intermediary, core operator, infrastructure provider, colluding parties, investigator or network observer. State what remains visible. Test the claim using realistic repeated payments, wallet migration, log correlation and recovery procedures.

Use synthetic identities and transactions in public tests. Do not place identity documents or easily reversible hashes of personal identifiers on a shared immutable ledger. Aggregate analytics should have a documented leakage model and minimum useful output, rather than an undefined “anonymous” label.

Legal compliance design must specify the actual covered entities, applicable duties and permitted disclosures. Do not hard-code one country's retention period or identity rule as a global requirement. Also assess accessibility for people without smartphones, reliable connectivity, conventional documentation or an existing bank account.

## 3. Key management is a lifecycle

NIST's final Revision 5 covers protected key handling, inventory and compromise-recovery planning. It also describes split-knowledge procedures. The checked project page lists a Revision 6 draft, so algorithm and revision status must be reviewed again before implementation. [CB-015](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final), [revision context](https://csrc.nist.gov/projects/key-management/key-management-guidelines)

### Proposed key classes

| Class | Main risk | Proposed treatment to evaluate |
|---|---|---|
| Issuance authorisation | Unauthorised supply | Separate approval from execution; protected signing; independently controlled quorum |
| Settlement/service identity | False instructions or state | Scoped credentials, authenticated peers and prompt revocation |
| Software/policy release | Malicious upgrade | Reproducible artifacts, independent review and separate release approval |
| User authorisation | Theft or loss of access | Explicit custody model, secure enrolment and tested recovery |
| Data encryption | Disclosure or unrecoverable records | Purpose-specific keys, access restrictions and justified recovery arrangements |
| Audit attestation | Forged evidence | Independent custody and validation |
| Trust anchors | Ecosystem-wide impersonation | Documented ceremonies, guarded replacement and emergency distribution |

For each key, specify owner, purpose, algorithm profile, generation method, custody, storage protection, activation, cryptoperiod, rotation, revocation, backup/recovery policy, destruction and evidence. Do not assume signing keys and encryption keys have identical backup needs.

Test loss and compromise separately. A lost user credential should not automatically extinguish an underlying legal claim. A compromised credential may require containment and adjudication. Neither warrants silently minting replacement money while old spending authority remains live.

Key rotation must address pending instructions, offline devices, old signatures and trust-store updates. Recovery procedures themselves need fraud controls, independent approval, notice where appropriate and a dispute path. Never store production secrets, seed phrases or usable test-environment administrative credentials in the public repository.

## 4. Finality needs legal and technical definitions

PFMI expects a clearly defined final settlement point and clarity about when instructions cease to be revocable. The law and the system's rules must agree with the technical event being represented to users. [CB-006, principle 8](https://www.bis.org/publications/principles-financial-market-infrastructures.pdf)

### Proposed state vocabulary

- Received: the service has the instruction; no settlement promise
- Validated: required syntactic and policy checks have passed at a defined version
- Reserved: spending availability is constrained; settlement has not necessarily occurred
- Committed: the selected authoritative system has accepted the state transition
- Final: the applicable legal and scheme conditions for final settlement are satisfied
- Rejected, expired or cancelled: a defined non-settlement outcome
- Indeterminate: the observer cannot yet establish the authoritative outcome

This is a vocabulary proposal; a chosen implementation may combine states only after proving their equivalence. A transaction hash, block confirmation, client acknowledgement, API timeout or smart-contract event is not inherently a legal finality determination.

Record which event triggers finality, the evidence available to each participant, and what happens during network partitions, validator faults, operator failure or conflicting records. User interfaces must not display “paid” merely because submission succeeded.

After finality, an authorised refund or corrective payment should normally be a separate linked event rather than an undocumented edit to historical settlement. The governing law may provide remedies; technical append-only history does not remove them. Document any exceptional intervention and the legal effect separately.

## 5. Recovery must restore the financial state

Polaris emphasises recovery of transaction status and participant positions, as well as ecosystem responsibilities and cryptographic adaptation. Restoring a running server is only one part of that task. [CB-013, Appendix A](https://www.bis.org/publications/project-polaris-security-and-resilience-framework-cbdc-systems-part-2.pdf)

### Proposed recovery evidence

- Identified critical services and dependencies
- Service-specific recovery-time and recovery-point targets
- Authenticated, isolated backups and a tested restoration chain
- A known consistent checkpoint and replay/reconciliation method
- The status of every in-flight issuance, payment and redemption
- Detection of duplicates, omitted events and conflicting entitlements
- A process for compromised rather than merely unavailable infrastructure
- Participant communications and decision authority for restart
- Post-restart independent reconciliation before normal limits resume

The Bank of England's illustrative work links recovery metrics, trusted backups and data reconciliation. Treat that as a useful design example, not as proof that a backup strategy is sufficient. [CB-008, pages 36–38](https://www.bankofengland.co.uk/-/media/boe/files/paper/2023/the-digital-pound-technology-working-paper.pdf)

Test regional outage, corrupted replica, malicious insider, compromised signing key, failed intermediary, interrupted upgrade and loss of normal identity/communications services. Separate financial-state recovery from discretionary remediation of customer losses.

The FMI cyber guidance discusses safe two-hour resumption capability and completion of settlement by day-end, while requiring judgment and contingency planning. Do not import “two hours” as an unexamined universal CBDC promise or restart an unsafe system to hit a clock. [CB-007, section 6](https://www.bis.org/publications/guidance-cyber-resilience-financial-market-infrastructures.pdf)

## 6. Offline value requires a separate risk profile

The Polaris handbook includes device lifecycle and offline-value recovery considerations. Losing an offline purse raises different questions from restoring an online account. [CB-012, sections 4.4.3–4.5](https://www.bis.org/publications/project-polaris-handbook-offline-payments-cbdc.pdf)

### Proposed offline gate

Keep offline transfers disabled in the first executable profile unless there is a separately reviewed design covering:

- Whether payment settles locally or remains pending until reconnection
- Whether recipients can spend received value onward while still offline
- Counterfeit, cloning, rollback and double-spend threats
- Device limits, value limits, duration limits and update requirements
- Tamper-resistance assumptions and device supply-chain risks
- Online/offline funding and defunding reconciliation
- Lost/stolen-device treatment and how duplicate recovery is prevented
- Loss allocation when later reconciliation discovers conflicting claims
- Privacy effects of funding, defunding, risk controls and recovery
- Accessibility and acceptance when a device cannot be trusted or refreshed

These limits are not a claim that unrestricted offline settlement is impossible. They are a requirement to state what has and has not been demonstrated. A secure-element claim or vendor demonstration is not sufficient evidence of a complete operational model.

## 7. Observability without accidental surveillance

The Bank of England's consultation response distinguishes operational metadata from aggregated analytical data in its proposed infrastructure. This suggests making those purposes explicit in a research design. [CB-009](https://www.bankofengland.co.uk/paper/2024/response-to-the-digital-pound-technology-working-paper)

Proposed operational metrics include service health, queue age, failed authentications, reconciliation exceptions and the age of unresolved instructions. Do not log full payment payloads or user identities just because it is convenient for debugging.

Keep forensic retention, supervisory reporting, user statements and public statistical outputs separate. Each needs its own access policy and test fixtures. Audit evidence should be tamper-evident and verifiable without exposing production secrets or unnecessary personal data.

## 8. Assurance gates and falsifiable tests

| Gate | Evidence required before the claim can advance |
|---|---|
| Concept approved | Explicit objectives, users, alternatives and unresolved decisions |
| Legal profile complete | Qualified jurisdiction-specific review and named competent authorities |
| Monetary model specified | Journal mappings, supply/availability invariants and reconciliation ownership |
| Prototype credible | Reproducible synthetic tests with negative and concurrency cases |
| Privacy claim bounded | Data-flow map, adversary model, leakage tests and disclosure procedure |
| Security model credible | Independent design review, key lifecycle and remediation of findings |
| Recovery demonstrated | Exercised failures with financial-state reconciliation |
| Pilot considered | Issuer approval, participant duties, loss allocation, consumer support and bounded exposure |
| Production considered | Independent assurance and explicit institutional acceptance of residual risk |

Useful falsification tests include repeated issuance IDs, concurrent spends, stale eligibility, policy changes during a reservation, incorrect precision, compromised release keys, failed redemption acknowledgements, intermediary exit, lost wallets and restore-from-backup races.

No benchmark, source citation, formal verification of a narrow function, or successful smart-contract audit alone establishes legal compliance, whole-system privacy, economic suitability or production readiness.
