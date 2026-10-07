# Architecture decision record

Status: accepted for the first **research prototype only**, 7 October 2026. Production decisions remain subject to issuer, legal, security and operational review.

## ADR-001: One instrument per deployment profile

Choose one immutable synthetic currency code, decimal scale, minimum unit, supply cap and issuer-policy registry per database. The CLI's TUSD profile has two decimal places and a five-cent minimum unit. A different jurisdiction can create a different profile; different sovereign liabilities must never be pooled merely because the same platform runs them.

Alternative: a multi-asset ledger from day one. Rejected for the first slice because it creates FX, issuer, collateral and precision ambiguities before the single-liability invariants are tested. “One type of money” means common units and fungibility within one issuer's currency; it does not create one global sovereign liability.

## ADR-002: Model notes with exact integer values

Use local unspent notes, each with one owner and positive bounded integer minor-unit value. A transfer consumes complete notes and creates a new set whose sum is identical. Multiple denominations are representational choices within the same money, not separate assets. Fixed denominations are unnecessary; any permitted multiple of the minimum unit can be used.

Alternative: balances only. This remains a viable production design and may be more efficient for many payment paths. Local notes make the requested splitting/merging semantics and future BSV UTXO mapping explicit. Local note IDs are deliberately documented as non-chain identifiers.

## ADR-003: Separate proposal from exact approval

The issuer-role actor proposes mint/retire instructions; a different approver-role actor approves the canonical request hash. Approval performs all current state checks again inside the write transaction. A proposal alone neither reserves outputs nor changes supply. A spent retirement input causes approval to fail; it is never silently replaced.

This is a workflow model, not a cryptographic quorum. Production must bind authenticated independent officers or service principals to scoped mandates, HSM signing, expiry, revocation and an auditable legal basis. A single caller able to impersonate both IDs defeats the demonstration's role boundary.

## ADR-004: Require owner-authorized transfer into treasury before retirement

Treasury retirement consumes notes already owned by a treasury-role account. Ordinary holders cannot reduce their balance without an authorized transfer. A separate exceptional lawful recovery path, if a jurisdiction needs one, must have its own evidence and due-process design; it is absent here.

Redemption of software units and payout through another system are separate events. The demo labels retirement synthetic and promises no external cash payment. Production must define when each liability is extinguished and who carries failure risk.

## ADR-005: Use a dependency-free transactional reference model

Python's SQLite interface supplies durable local transactions, uniqueness and constraint checks. `BEGIN IMMEDIATE` serializes economic mutations; full synchronous mode and foreign keys are enabled. Request digests provide exact replay semantics. A consistent backup is obtained through SQLite's backup API.

This is a correctness baseline, not the intended national high-throughput deployment. It has one writer, linear reconciliations, a static identity registry, no service authentication and no distribution. Do not extrapolate its unit-test duration to payments per second. The future scaling architecture must retain these invariants while distributing intake, policy decisions, note partitions and reconciliation safely.

## ADR-006: Separate CBDC amount from BSV carrier and fees

Currency value is never silently converted into satoshis. Future adapters need three separately typed amounts: currency principal in minor units, carrier-output satoshis and fee-budget satoshis. A fee sponsor can pay BSV costs without shrinking the user's currency payment. Fee exhaustion must fail or queue visibly; it cannot authorize minting currency.

## ADR-007: Start with a non-broadcast anchoring boundary

The first BSV integration reads an explicitly testnet-only endpoint and builds a small audit-head commitment script. It neither imports the SDK nor creates keys. The script is suitable input to later transaction construction, not proof that a network accepts it. No signed transaction, token covenant, UTXO validation or Merkle-path verification is performed.

This preserves testability while current SDK, licence, node and wallet choices are investigated. The active official source is now ts-stack, not the archived standalone ts-sdk repository. Source evidence is in the BSV register. Installing or operating a selected dependency later requires its actual terms and exact package integrity to be reviewed.

## ADR-008: Do not mistake anchoring for a token system

An audit digest on BSV can witness a commitment under stated assumptions. It cannot enforce the off-chain ledger's amount conservation or holder authorization. The next design comparison must evaluate issuer-co-signed UTXOs, a formally specified covenant/token protocol, and an authoritative issuer ledger with independent anchors. Each must specify who can create supply, who can override ownership, how validators establish issuer lineage, and what survives an operator outage.

No token standard is selected merely because it exposes a `mint` method. Consensus script validation, overlay indexing, issuer rules and legal entitlement are different enforcement layers. A proof obligation and adversarial test corpus precede implementation selection.

The completed [source-level comparison](../research/token-enforcement/candidate-comparison.md) now identifies regulated Mandala and an issuer/holder co-signature design as the focused shortlist. Regulated Mandala's monetary controls are overlay predicates above P2PKH, not native consensus rules. Its existing code still requires qualification against the treasury contract. No package has been installed or adopted by this decision.

## ADR-009: Explicit completion states

Local application state, node/provider acknowledgement, broadcast observation, block inclusion, confirmation-policy completion and legal finality require separate records. Future adapters must store block hashes and detect orphaning; a status string such as `IMMUTABLE` from a provider is not an independent legal guarantee. Unknown broadcast outcomes retain the same transaction identity while being reconciled.

The current model reports `mode=simulation` and `chain_status=not_submitted`. It cannot claim instant chain finality. “Instant minting” initially means low-latency authorization/application processing, whose actual latency remains to be measured separately.

## ADR-010: Static policy and synthetic privacy boundary

Profiles demonstrate active/frozen identities, holding limits, amount limits, denomination bounds and distinct roles. They use invented identifiers. No customer PII belongs on-chain. Mutable policy versions, aggregate person-level limits across wallets, identity attestations, expiry, appeals, audit access control and privacy attacks remain explicit work items.

Source-grounded legal and institutional context is in the [central-bank research](../research/central-bank/central-bank-architecture.md). These implementation choices are project decisions rather than standards attributed to those sources.
