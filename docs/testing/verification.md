# Verification record

Date: 7 October 2026. Scope: the exact source tree proposed by this foundation change.

## Executed checks

- `python -m unittest discover -v`: 52 tests pass after independent review and regression fixes.
- `python -m compileall -q cbdc_lab tests`: passed.
- `python scripts/check_research.py`: validates evidence schema/required fields, unique source IDs and local Markdown links. It does not certify source truth or legal compliance.
- `python -m cbdc_lab.demo`: completed the complete synthetic treasury/denomination lifecycle.
- `python -m cbdc_lab.demo --observe-testnet`: completed and retrieved live BSV testnet chain status. The [first observation](demo-and-testnet-observation.json) was recorded at 08:20:33 UTC. The [final-code observation](final-demo-and-testnet-observation.json) succeeded at 08:46:07 UTC after one earlier connection timeout; it reported height 1,761,932. These are provider reads, not a broadcast or availability guarantee.

Final command output and environment versions are stored beside this file. GitHub CI for the exact proposed commit is a separate check and must be inspected after the push; a local pass is not a hosted CI result.

The first foundation commit, `2e4ffea0a99978ee751466b6a252ba951fe352e4`, passed GitHub CI on Python 3.12 and 3.13. All 31 files at that commit matched the prepared UTF-8 contents exactly. [Machine-readable receipt](github-foundation-verification.json). Subsequent documentation commits require their own remote/CI checks; this receipt intentionally remains pinned to the commit it proves.

## Coverage

The tests cover exact 100.00 → 2,000 × 0.05 → 100.00 conservation; mixed values; issuer/approver separation; exact approval hashes; no economic effect before approval; replay and payload mismatch; wrong ownership; duplicate/missing/spent inputs; malformed values; frozen/inactive/unknown actors; supply, holding, amount and fan-out bounds; policy/currency mismatch on reopen; treasury-custody retirement; changed state between proposal and approval; concurrency; restart; backup restore; tampered audit, journal, ownership and instruction records; bounded testnet responses; fixed endpoint selection; and disabled broadcast status.

Seeded randomized tests repartition the same value through 100 transformations. Concurrent two-connection tests establish one local double-spend winner and single-effect approval/replay behavior. Fault injection verifies rollback when an audit write fails after economic changes in mint, transfer and retirement.

The reviewer also repeated four concurrency cases 20 times (80 executions), all passing. This is race regression evidence, not a performance benchmark.

## Review fixes included

1. Lifetime journal debit/credit totals can exceed a database signed-64-bit accumulator while the outstanding supply remains valid. Reconciliation now accumulates those historical totals in exact Python integers; regression test covers a maximum-sized mint/retire cycle.
2. Approval now recomputes the canonical proposal body digest before economic application. A changed body cannot rely solely on a stale stored digest; a regression test verifies rejection.

## What was not tested or implemented

- A signed BSV transaction, funded test UTXO, actual broadcast, mining inclusion or cryptographic inclusion proof
- On-chain enforcement of issuance, split/merge conservation, custody or retirement
- SDK installation/runtime conformance, hardware signing, real identity/authentication or policy administration
- Distributed availability, multi-region recovery, OS/power/storage fault tolerance or chain reorganisation handling
- External reserve/cash reconciliation, redemption payout or a legally effective monetary claim
- Load performance at the 100,000 TPS project operating floor
- A security certification, legal opinion, licence/patent clearance, accessibility assessment or production acceptance

SQLite tests demonstrate local transactional behavior within the test harness. They do not validate a national payment system. The audit chain is internally checked and can detect inconsistent retained data; without an independent checkpoint, a fully rewritten or consistently truncated database may look internally valid.
