# CBDC architecture and monetary model

Research snapshot: 2026-10-07. Status: research proposals for evaluation, not an approved monetary system.

## 1. Begin with the claim on the issuer

A CBDC is a direct claim on a central bank, expressed in its currency's existing unit of account. A privately issued balance does not become that claim merely because it is fully backed by central-bank reserves. This is an issuer-and-law distinction, not a choice of database, blockchain or token standard. [BIS foundational report, CB-001](https://www.bis.org/publications/central-bank-digital-currencies-foundational-principles-and-core-features), [IMF legal analysis, CB-005](https://www.imf.org/-/media/files/publications/wp/2020/english/wpiea2020254-print-pdf.pdf)

The 2020 joint principles favour preserving monetary and financial stability, coexistence with other money, and useful innovation. Conversion at par supports the currency's singleness. They do not require replacing cash or introducing a new floating currency. [CB-001](https://www.bis.org/publications/central-bank-digital-currencies-foundational-principles-and-core-features)

### Proposed repository boundary

- Describe the project as CBDC research/reference software, with synthetic test balances.
- Use one fictional currency and one explicitly simulated issuer in the first executable profile. Do not use a real currency symbol in a way that suggests an enforceable claim.
- Model issuer identity and liability class separately from a wallet address or contract address.
- Do not advertise a mint function, central administrator, collateral account or permissioned validator set as sovereign authority.
- Do not assert legal tender, deposit protection, redemption rights, guaranteed anonymity or central-bank endorsement.
- Keep the same nominal unit across online balances, offline value and payment reservations. A representation change is not an FX trade.
- If a separate network-fee asset is later introduced, expose it separately. It must not silently redefine the CBDC denomination or require users to speculate in another token.

### Jurisdiction decisions before real value

Specify the issuing institution and currency area; statutory issuance power; instrument classification; eligible holders; redemption entitlement; legal-tender and acceptance rules if any; insolvency treatment; data-controller and compliance responsibilities; dispute jurisdiction; and the applicable finality framework. A repository licence, scheme membership agreement or deployment transaction cannot supply missing public-law authority.

The IMF working paper distinguishes central-bank-law powers from monetary-law treatment. Its historical cross-country findings should not be treated as today's law for an unselected country. [CB-005](https://www.imf.org/en/publications/wp/issues/2020/11/20/legal-aspects-of-central-bank-digital-currency-central-bank-and-monetary-law-considerations-49827)

## 2. Choose an intermediated research model explicitly

The 2021 joint design report separates issuer/core functions from processing and customer services. Its participating banks favour a public-private ecosystem, while acknowledging that circumstances can justify other arrangements. [CB-002, section 2](https://www.bis.org/publications/othp42-system-design.pdf)

### Proposed responsibility split

| Layer | Research responsibility | Boundary to preserve |
|---|---|---|
| Monetary authority | Approve supply changes and monetary parameters | Legal authority is established outside software |
| Government-controlled treasury area | Operate the requested prototype's mint/retire workflow under its configured mandate | Operational control is separately governed from central-bank legal issuer status |
| Scheme governance | Maintain access rules, duties, dispute procedures and change policy | A versioned rulebook is distinct from executable code |
| Core operator | Validate and record authorised issuance, transfers and redemption | Operational delegation does not transfer issuer liability |
| Regulated intermediaries | Onboard users, provide wallets and support, execute applicable compliance duties | User claims must remain distinguishable from intermediary liabilities |
| Identity/compliance services | Supply scoped attestations and legally required decisions | Avoid moving raw identity documents into a shared ledger |
| Independent oversight and audit | Assess controls and reconcile records | Read access is purpose-limited, logged and legally grounded |
| Users and merchants | Authorise payments and review outcomes | A valid signature is evidence under a defined authentication model, not proof of informed consent by itself |

This is an engineering starting point. It does not predetermine who is licensed, which institution controls each service, or whether a public service provider is required for inclusion.

### Requested treasury operational profile

The research profile includes a government-controlled treasury area with mint and retire operations. Its administrator, approver, executor and auditor roles should be distinct from holder roles and recorded separately from the central-bank issuer identity. Each supply change carries a unique instruction, amount, purpose, policy version and approval evidence.

This requirement does not answer whether a government may legally direct central-bank issuance. A jurisdiction profile must establish the treasury's authority, the issuer's responsibilities, and any required delegation, approval or independence constraints. A treasury credential grants only the specified software permission. It cannot create legal authority or transfer the liability from one institution to another.

Retirement should operate on explicitly authorised balances, including returned inventory or a holder-authorised redemption. Do not infer a general power to confiscate user balances from permission to retire treasury inventory. Holder denomination changes must not require the treasury's supply-changing privilege.

### Proposed component boundaries

1. Currency and issuer registry: immutable identity of the simulated instrument and fixed precision for that profile.
2. Issuance/redemption coordinator: policy approvals, unique instruction IDs and reconciliation to a simulated issuer general ledger.
3. Authoritative settlement state: balances or unspent claims, reservations, transaction state and auditable supply changes.
4. Intermediary gateway: authenticated requests, replay protection, authorisation scopes and participant status.
5. Policy decision service: versioned eligibility, limits and legally grounded restrictions; explicit failure behaviour.
6. Identity and privacy boundary: external attestations plus minimal ledger identifiers.
7. Optional payment-workflow service: consented schedules, escrow-like reservations and conditional instructions.
8. Operations and assurance: telemetry, incident handling, reconciliations, recovery evidence and audit exports.

A two-tier architecture need not make every component centralised or every component distributed. The 2024 joint report discusses mixed modular designs and their governance trade-offs. [CB-004, section 2](https://www.bis.org/publications/central-bank-digital-currencies-system-design.pdf)

Do not equate “account-based” with identified and “token-based” with anonymous. The terminology varies between law, economics and computer science. Specify authentication, record ownership and transfer semantics directly. [CB-002, Box 1](https://www.bis.org/publications/othp42-system-design.pdf)

## 3. Single-currency accounting is an invariant, not a price oracle

The following is an original illustrative model for testing. It is not a prescribed central-bank accounting policy.

### A minimal simulated issuer journal

Suppose an authorised conversion of 100 units from an eligible bank's reserve balance to CBDC has been approved.

| Event | Debit on simulated central-bank books | Credit on simulated central-bank books |
|---|---|---|
| Reserve-to-CBDC conversion | Reserve-deposit liability: 100 | CBDC liability: 100 |
| CBDC-to-reserve redemption | CBDC liability: 100 | Reserve-deposit liability: 100 |

The example reclassifies central-bank liabilities; it does not describe every issuance mechanism. It omits the commercial bank's books, customer interfaces, fees and accounting-standard details. Issuance via lending, asset acquisition or fiscal arrangements would require a different approved journal and authority.

### Synthetic suspense model for the prototype

The requested prototype accounting model uses a deliberately unverified issuance-suspense counteraccount rather than pretending to observe real central-bank reserves:

| Synthetic operation | Debit | Credit |
|---|---|---|
| Treasury mint: 100.00 test units | Issuance suspense: 100.00 | Simulated CBDC liability: 100.00 |
| Treasury retire: 100.00 test units | Simulated CBDC liability: 100.00 | Issuance suspense: 100.00 |

These balanced entries demonstrate bookkeeping mechanics only. The suspense debit is not proof of an asset, collateral, reserve funding, sovereign backing or an enforceable liability. Production use would require an approved general-ledger mapping, real settlement evidence and controlled reconciliation/clearance of suspense. The reserve-conversion example above and this synthetic counteraccount model are alternatives at different assurance levels; do not post both for the same event.

A payment between two CBDC holders changes attribution of the outstanding liability, not its total. A reservation changes availability, not supply. A wallet migration changes control, not the holder's entitlement. Destruction of a software representation must not be mistaken for completed economic redemption.

### Proposed invariants

- Outstanding simulated CBDC equals initial authorised outstanding value plus effective issues minus effective redemptions/extinguishments.
- Every authoritative unit is counted once. Available, reserved, offline-issued and quarantined categories must be disjoint or reconciled through an explicitly documented mapping.
- Mirrors, indexers, backups and intermediary records are views or records of claims, not additional supply.
- Every supply-changing event links to one authorised issuer instruction and one corresponding financial journal. Retrying the instruction cannot create a second issue or redemption.
- All arithmetic uses exact bounded integers in a profile-defined smallest unit. Validate overflow, underflow, sign, precision and rounding at every boundary.
- Payment fees, if introduced, identify payer, recipient and journal entry. They never vanish through rounding or silently alter the unit's nominal value.
- No transfer, migration, restoration or policy update manufactures spending power.
- No holder balance becomes negative unless a separately specified and authorised credit product exists. Such credit is outside the initial prototype.

### Proposed reconciliation and exception handling

Reconcile core supply, the simulated issuer general ledger, distributor inventories and intermediary customer records independently. Reconcile offline aggregate commitments without double-counting the corresponding locked online value. A discrepancy must create a bounded exception with an owner and evidence, not an automatic mint to force equality.

External reserve movement and digital issuance cannot be assumed to be one atomic database transaction. Specify pending states, durable correlation IDs, timeout ownership and recovery paths. A timeout means the outcome is unknown until checked. It does not authorise a new financial event.

Proof of a contract's total supply proves only a software state within its trust model. It does not prove statutory issuance authority, accurate external books, recoverable holder claims, or correct accounting treatment.

### Holder-authorised denominations, splits and merges

Denominations are representations of value within one currency, not separate currencies or fresh issuance. A holder may authorise a split or merge of the claims they control, subject to the same availability and entitlement checks as other holder actions.

For the requested example, TUSD denotes synthetic test units only, with no relation to any real currency or token. With two decimal places in this test profile:

- 1 × 100.00 = 2,000 × 0.05 = 10,000 smallest units
- A mixed split can be 1 × 50.00 + 2 × 20.00 + 1 × 5.00 + 100 × 0.05 = 100.00
- Merging either set restores 100.00 without changing outstanding supply

Require the exact sum of input amounts to equal the exact sum of output amounts, all in bounded integers. Consume or encumber each input only once; atomically establish its replacement outputs; reject duplicate inputs, unauthorised holders, unavailable inputs and invalid precision. A failed transformation leaves no partial new spending power. Any explicit fee needs a separately balanced allocation; it cannot be hidden as lost change.

For a balance-ledger implementation, denominations may be wallet presentation only. For individually represented notes or claims, split/merge changes the record set and associated identifiers. In both cases, keep the central-bank aggregate liability and simulated issuer journal unchanged, with a traceable transformation event. Do not send these transformations through unrestricted treasury mint/retire APIs merely because output records are created and input records are consumed.

Test the 2,000-output case, mixed denominations, repeated retries, races with spending, overflow, and partial failure. Set explicit resource bounds or a safe batched-reservation design; denomination support must not become an unbounded transaction-size attack or a way to evade aggregate holding limits.

## 4. Policy controls require public decisions and constrained execution

The joint financial-stability report analyses quantity limits, remuneration and related safeguards. Calibration affects adoption, bank funding and data needs. No numeric limit from another jurisdiction should become a universal constant. [CB-003, section 5](https://www.bis.org/publications/othp42-fin-stab.pdf)

### Proposed configurable policy catalogue

| Control | Minimum decision record | Research test |
|---|---|---|
| Issuance and redemption | Authorised officer roles, amount scope, expiry, journal reference | Duplicate or over-quota instruction cannot change supply |
| Holder eligibility | Jurisdiction, evidence basis and appeal route | Expired/invalid attestations fail with a precise reason |
| Holding limits | Person/entity versus wallet basis; related accounts and offline treatment | Splitting across wallets does not bypass an intended aggregate limit |
| Transaction limits | Single-payment or rolling-window scope, clock source and exemptions | Concurrent requests cannot evade the limit |
| Remuneration | Explicitly enabled policy, effective time, rounding and postings | Recalculation is deterministic and conserves accounting entries |
| Freeze or restraint | Competent authority, legal basis, scope, duration and review | One case cannot expand into an unrestricted administrative power |
| Emergency suspension | Trigger, approving roles, affected services and restart criteria | Narrow containment preserves entitlement and recovery evidence |
| Policy change | Version, approval, activation point and migration behaviour | In-flight payments have unambiguous governing versions |

For the first prototype, use non-remunerated synthetic balances and no product-, merchant- or location-based spending restrictions as explicit research assumptions. They are not statements that every lawful CBDC must have those properties.

## 5. Programmable payments and programmable money are different choices

The ECB distinguishes conditional payment services from money whose use is restricted by purpose, time, place or counterparty. This is the digital euro's stated design direction, not a universal legal definition of CBDC. [CB-010, question 20](https://www.ecb.europa.eu/euro/digital_euro/faqs/html/ecb.faq_digital_euro.en.html)

### Proposed boundary for this research

Allow an optional workflow to submit an ordinary payment when a condition chosen by the payer is met. The money received remains ordinary units of the same instrument. Keep the workflow separate from currency issuance and core transfer rights.

A pay-on-delivery experiment must specify who attests delivery; whether funds are merely reserved or already transferred; when the payer can cancel; the expiry/refund path; disputes; and what happens when an oracle is wrong or unavailable. A smart contract does not establish that physical delivery occurred.

Government benefits, taxation, court orders and compliance duties are distinct policy/legal questions. Do not quietly turn them into a general-purpose power to expire balances or prohibit otherwise lawful purchases.

## 6. Interoperability is a system agreement

The joint 2022 report describes compatibility, interlinking and a common system as different approaches. Each brings access, governance and implementation choices. [CB-014](https://www.bis.org/publications/options-access-and-interoperability-cbdcs-cross-border-payments.pdf)

### Proposed staged scope

1. Domestic same-instrument interoperability: users can move between approved wallet providers without creating a new issuer claim.
2. Domestic conversion: separately model commercial-bank deposits, cash distribution and reserve-settlement interfaces.
3. Optional cross-currency research: separate currencies, issuers and liabilities; define quotes, liquidity, FX risk and settlement coupling.
4. Cross-border access: add only after residence/access rules, compliance obligations, data transfers and dispute jurisdiction are decided.

An API or bridge must document amount precision, participant identity, message version, duplicate handling, rejection reasons, availability expectations, transaction-state mapping and reconciliation ownership. A protocol receipt is not enough if the other system has not reached its required settlement state.

A shared blockchain does not resolve foreign access rights, conflicting laws, supervisory responsibilities or principal risk. Do not advertise universal interoperability from token compatibility alone.

## 7. Decisions intentionally left open

- Issuer, jurisdiction and statutory powers
- Retail versus wholesale profiles and eligible institutions
- Account/claim data model and authoritative record
- Ledger/consensus technology, if any
- Online/offline privacy targets and accepted residual risks
- Custody, loss allocation, recovery and user-redress rules
- Specific limits, remuneration and access policies
- Finality event and governing legal framework
- Performance, resilience and accessibility targets
- Intermediary economics and public-service obligations
- Independent assessment and production acceptance criteria

The next artifact should be a decision log that records alternatives, evidence, accountable decision owners and tests. Implementation should follow those choices rather than let a token standard make them implicitly.
