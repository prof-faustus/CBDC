# Laboratory runbook

## Safe execution

Use Python 3.12+ and a fresh local workspace. There are no third-party runtime packages. Run the unit suite first, then the demo. The default demo uses a temporary database and removes it when done. All names and amounts are synthetic. Never put customer identity, real credentials, real funds or confidential government instructions into the demonstration.

For a persistent experiment, instantiate `Ledger` with a dedicated new database path and a fixed profile/actor registry. These objects form a trusted test interface, not a remotely callable service. Do not expose them over HTTP or accept an arbitrary caller-supplied actor ID as authentication.

## Before changing a profile

Record the currency code, scale, minimum denomination, supply/operation caps, input/output bounds and actor registry. Reopening an existing database with a changed profile is rejected. A policy migration requires a separately reviewed design rather than bypassing this check.

## Reconciliation

Call `verify()` after scenarios and before creating an anchor request. It reconciles the audit hash chain, stored request digests, applied operation evidence, note history, issuer journal and outstanding supply. Keep an independently protected copy of the resulting checkpoint if authenticity or truncation detection is required. The local check alone does not supply that trust anchor.

If verification fails, stop dependent work. Preserve the original database and test commands. Diagnose the mismatch in a copy; do not invent a balancing mint or manually alter the circulating liability to make the report pass.

## Backup and restore drill

Use `Ledger.backup(new_path)` for a consistent SQLite backup. It refuses an existing destination. Reopen the copy with the same profile and registry; run `verify()` and compare the independently retained audit head and supply. A successful local copy/restore is not evidence of geographic disaster recovery or a proven RPO/RTO.

## Network observation

`--observe-testnet` sends a credential-free GET to a fixed public BSV testnet chain-info endpoint. It does not send a transaction or wallet address. Failures are visible and should not be rewritten as a successful connection. A provider may return stale or false data; independent header/proof verification is future work.

## Signing and broadcasting

No signing/broadcast path is implemented. An unsigned commitment request is not a transaction. Do not pass it to an arbitrary wallet or mainnet endpoint. The next test stage must choose and authorize its signer, fee source, dependency terms and explicit network. Keep secrets outside code, logs, command arguments, test vectors and Git history.

## Publication checks

Run tests, compile checks and research checks on the final tree. Inspect the diff for secrets, private sources, accidental databases and claims stronger than the evidence. Use an isolated branch and draft PR. Verify remote file bytes and the exact-head CI result. Do not merge, deploy or change repository visibility as a side effect.
