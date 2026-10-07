# Performance acceptance protocol

Status: proposed experiment design. No load result is reported by this file.

## Requirement

The project specifies a minimum operating floor of **100,000 transactions per second**. For a meaningful acceptance result, define the numerator as distinct valid economic payments reaching a named completion boundary. Report administrative operations, note reshapes, ledger transactions and output counts separately. A split into 2,000 outputs is not 2,000 new payments.

Official Teranode test reports show important blockchain capacity. This project must additionally measure issuer authorization, policy checks, identity attestations, privacy mechanisms, signing, fee sponsorship, chain integration, durable records and reconciliation. The complete path is constrained by its slowest stage.

## Predeclared experiment specification

Record exact code revisions; dependency digests; currency/policy profile; hardware and instance counts; regions and independent operators; CPU/RAM/storage/network; database and queue topology; node/ARC/wallet versions; chain parameters; retention; replication; consensus participants; fee model and budget. Publish a deterministic workload generator and seeds.

Workloads must include:

- One-input/two-output ordinary payments, payment chains and hot holders
- Treasury mint/retire approvals and reconciliation
- The requested 2,000-output split and 2,000-input merge, with measured byte/signature costs
- Mixed output values, malformed requests, duplicate/retried requests and conflicting spends
- Realistic holding/transaction policy checks and privacy/identity overhead
- Fee UTXO replenishment, exhausted sponsorship and provider limits
- Backups, retention compaction, checkpointing and replay under load

State offered, admitted, rejected, completed and unresolved counts separately. Report currency principal, BSV fees, transaction bytes, note creation/consumption and storage growth. No retries, duplicate acknowledgements or administrative housekeeping count as extra payments.

## Timing and finality boundaries

Capture timestamps for initial client intent, durable admission, validation/approval, signature completion, provider acceptance, network observation, block inclusion, confirmation-policy completion and any legally defined settlement event. Record clock synchronization and uncertainty. Publish p50/p95/p99 latency, timeout distributions, backlog and fixed-window completion counts.

Do not infer one-second finality from a 100,000-per-second throughput average. Do not call an API success legal settlement. If the scheme uses provisional credit before chain confirmation, report the credit exposure, guarantor and loss allocation separately.

## Run protocol

Proposed baseline: warm-up, at least 24 hours of sustained measurement over several block/confirmation cycles, a separately reported drain, then complete reconciliation. This duration is a project experiment proposal rather than an external standard. Fix latency, error, backlog and recovery thresholds before running; their numeric values remain a project decision.

Use open-loop offered load to avoid hiding queue growth. Retain incomplete requests in the result. Repeat the payment mix, highest permitted fanout and contention scenarios. Do not fill the system with unlimited independent prefunded inputs and omit replenishment cost.

## Fault campaigns

During sustained traffic: terminate an application worker; stop an approval service; partition a region; degrade or exhaust storage; pause a broker; lose an observation feed; reject transactions; submit conflicts; orphan a block; restore a stale snapshot; rotate a compromised test credential. Record detection, containment, economic effect, recovery, backlog clearance and every unresolved outcome.

Acceptance requires supply/issuer-liability equality, exact transfer conservation, no duplicate issue/retire effects and no unexplained loss of acknowledged work. An error-rate target cannot excuse monetary creation or disappearance.

## Evidence package and stopping rule

Produce machine-readable observations, signed or independently witnessed checkpoints, raw configuration, hardware/cost inventory, fault timeline, reconciliation report and known gaps. Identify the completion boundary the result actually proves. Stop a test immediately on unexplained monetary inconsistency, unsafe exposure, runaway resource use or budget overrun; preserve evidence and diagnose before resuming.

No outcome from the local Python unit suite establishes performance at the operating floor. Its purpose is to freeze correctness semantics for later implementations.
