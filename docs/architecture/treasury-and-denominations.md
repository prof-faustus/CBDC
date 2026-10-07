# Treasury, issuance, retirement and denominations

## Requirement interpretation

The platform includes a treasury workspace through which authorized government functions can propose issuance and retirement. The institution legally entitled to issue the currency must be separately identified. A government treasury is not assumed to possess a central bank's statutory powers in every jurisdiction.

The user's example is exact: 100.00 units = 10,000 minor units = 2,000 outputs of five minor units. A holder may split, recombine or use mixed amounts, subject to the instrument's minimum unit and safety limits. This is changing the representation of existing value, not exercising mint authority.

## Operation contracts

| Operation | Authority | Inputs | Outputs | Change in supply |
|---|---|---|---|---|
| Mint proposal | Issuer operator | Approved issuance rationale, destinations, amounts | Immutable proposed instruction | 0 |
| Mint approval | Independent approver | Exact proposal hash, current policy | New notes and balanced issuance journal | Sum of outputs |
| Transfer/split/merge | Owner of every consumed note | Unique unspent notes | Positive valid amounts to eligible recipients | 0 |
| Retirement proposal | Issuer operator | Treasury-owned unspent notes, rationale | Immutable proposed instruction | 0 |
| Retirement approval | Independent approver | Exact proposal hash and still-unspent treasury notes | Balanced retirement journal; no spendable replacement | Minus sum of inputs |

The public method arguments are a test-harness interface. They are not evidence of real consent or independent officer identity. An authenticated service and separate signing boundary must replace that assumption before a shared pilot.

## Invariants

1. All values are positive integers within the profile's explicit domain. Booleans, floats, strings, zero, negatives and overflows are rejected.
2. Each amount is divisible by the configured minimum unit.
3. A note is consumed at most once. Duplicate input references are rejected before totals are computed.
4. A transfer has `sum(inputs) == sum(outputs)` exactly. No implicit fee is deducted from currency principal.
5. Outstanding value equals the sum of unspent notes and the simulated issuer's circulating liability.
6. Every supply change has one applied instruction, one independent approval record and a balanced journal.
7. An idempotency key identifies one canonical payload. Repeating it returns the original result; changing its contents is rejected.
8. Destination holding limits are checked against the post-transaction amount, accounting for the owner's notes consumed by the same transaction.
9. All effects, journal postings, output records and audit entries commit together locally or roll back together.
10. A rejected operation neither consumes notes nor adds an audit entry claiming economic success.

## Example mixed transfer

Consume Alice's 100.00 note. Create 33.35 for Bob and 66.65 for Alice. Both are multiples of 0.05 and sum to 100.00. Bob can combine the 33.35 with other notes he owns, split it, or transfer it to treasury for the separate retirement workflow. Any merge crossing ownership boundaries requires explicit multi-party authorization, which is not implemented in the first slice.

## Fan-out and batching

The demonstration permits up to 2,000 inputs and 2,000 outputs so the requested example runs in one local transaction. This is a prototype bound, not a BSV consensus maximum. Changing denominations can multiply storage, signature work, propagation, indexing and recovery cost without creating extra economic payments.

Above the bound, reject the instruction with no effects. Do not silently claim atomicity across batches. Future large fan-out support must choose one of: a single chain transaction within verified limits; an explicitly non-atomic sequence with disclosed partial-completion states; or a separately proven reservation/commit protocol. Cancellation and retry semantics must be defined for partially completed sequences.

A 2,000-output split counts as one reshape operation and 2,000 outputs, not 2,000 customer payments. The performance corpus must include both logical payments and ledger transactions, and record bytes, inputs, outputs and signatures.

## Accounting boundary

The executable journal uses debit `asset:test_issuance_suspense`, credit `liability:circulating` for minting and the reverse for retirement. It is intentionally a test placeholder and proves no actual asset backing. A real central-bank scheme may instead convert reserve liabilities, acquire assets or follow other legally authorized postings. The accounting authority must select and reconcile that model before real value.

No function in this repository settles a bank transfer, accepts a deposit, redeems real currency, signs a BSV transaction or changes monetary law.
