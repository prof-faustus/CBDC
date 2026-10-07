# Initial threat model

Scope: the local reference implementation and the design boundary for a future BSV test pilot. This is a research risk register, not a completed security assessment.

| Threat | Current control or test | Residual risk / next gate |
|---|---|---|
| Unauthorized mint | Separate issuer/approver roles, exact proposal hash, supply cap | IDs are trusted test inputs; build real authentication, mandates, HSM quorum and officer independence |
| Unauthorized retirement | Treasury ownership required before dual approval | No legal evidence, payout or exceptional recovery flow; never infer those from custody |
| Double spending | Serialized transaction and conditional consume; two-connection race test | Not distributed consensus; chain/overlay conflicts remain untested |
| Replay inflation | Unique operation ID and canonical payload digest | Cross-service correlation IDs and expiry need authenticated envelope design |
| Float/rounding creation | Integers only, minimum-unit divisibility, supply cap | Cross-language encoders and external accounting systems must preserve exact semantics |
| Wallet-limit evasion | Per-actor holding checks including consumed change | Per-person aggregation across multiple actors is not implemented |
| Malicious or stale approval | Exact hash and revalidation at application | Expiry, revocation, compromise recovery and mutable policy epochs absent |
| Audit modification | Hash chain, operation-to-audit and state projection reconciliation | A database administrator can rewrite all local records; anchor/external witness and access controls required |
| Audit truncation | Internal consistency checks | A consistently truncated state cannot be detected without independently retained checkpoints |
| Database loss | SQLite backup/restore and restart tests | Disk/power fault injection, replication, recovery objectives and geographically separate backups untested |
| Provider lies | Fixed testnet endpoint, schema and chain-label validation | Provider report is not independently validated headers, chainwork or SPV inclusion |
| Endpoint confusion | No configurable broadcaster; mainnet rejected in ledger | Future signed raw transactions carry no simple network tag; verify endpoints, chain identity and funded inputs |
| Fee theft or fee exhaustion | No wallet or broadcast path exists | Future fee sponsor needs strict satoshi budgets, UTXO control, destination validation and reconciliation |
| Reorganisation | Distinct future state model documented | No live reorg handling; dependent payments and compensations need testing |
| Output amplification/DoS | Input/output and amount bounds, no generator inputs | Large admitted workloads can still monopolize the single writer; rate limiting/backpressure absent |
| Identity disclosure | Synthetic aliases only; anchor contains domain plus audit digest | Hashes may be linkable; privacy review must precede real data or public anchoring |
| Supply-chain compromise | No third-party runtime dependencies in first slice; CI actions pinned | Python/runner trust remains; SDK package integrity/licensing and SBOM review still required |
| Insider control-plane abuse | No mutable role/policy admin API | Immutable setup is a lab simplification, not a production governance solution |
| Deceptive success reporting | Results say simulation/not_submitted; separate read-only receipt | Consumers must retain status semantics and must not rename local success “settled” |

## Security boundaries

- The entire Python process, caller and local OS are trusted by this version. Possession of an actor name is not authentication.
- The database stores synthetic values and test reasons; do not supply real personal information or confidential government decisions.
- A future public API must not expose the current method signatures without authentication and authorization middleware.
- No mainnet, real-value, public launch, credential storage or remote deployment is included.
- A production proposal needs independent threat review, cryptographic and token-protocol review, legal analysis, abuse testing and operational exercises.

## Required adversarial scenarios for the next stage

Combine retry-after-timeout with provider failure; reorder approval and policy changes; conflict a parent transaction and its descendants; replay signed requests across currencies/networks; replace a fee input; tamper with a Merkle proof/header; restore a stale database while the network advances; compromise one approval role; exhaust fee UTXOs; split holdings across wallet aliases; and attempt partial batch completion. For each, record expected state, actual evidence, liability/supply reconciliation and recovery authority.
