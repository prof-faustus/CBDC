# Static-review hotspots and evidence locations

Research date: 7 October 2026. These are observations and qualification obligations from public source inspection, not reproduced vulnerability reports or passing test claims. No dependencies or external source code were installed or executed.

## H01: BTMS partial-output admission

Source admits ISSUE unconditionally, accumulates per-asset totals, and admits individual acceptable outputs. Qualification must compare admitted indices to all requested outputs; do not infer transaction-level atomic token acceptance.

Source: [TEN-003, lines 158–205](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/btms/BTMSTopicManager.ts#L158-L205).

## H02: BTMS admission regression witness

The repository includes a test deliberately exercising partial-prefix admission. It was read, not executed.

Source: [TEN-004, lines 449–474](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/btms/__tests/BTMSTopicManager.test.ts#L449-L474).

## H03: Regulated monetary deltas

Exact holder transfer delta zero is an overlay predicate. Issue and redeem only constrain sign of delta here; CBDC officer quorum and treasury-owned retirement restriction remain application obligations.

Source: [TEN-014, lines 244–268](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts#L244-L268).

## H04: Concurrent supply cap

The cap reads current supply before admission. Prove deployment serialization/conflict handling for concurrent independent authority spends; this is a review obligation, not a reproduced exploit.

Source: [TEN-014, lines 260–281](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts#L260-L281).

## H05: Recovery authorization

Reissue references frozen state, positive replacement delta, no value inputs and named recipient. Review simultaneous or repeated reissues and stale control state.

Source: [TEN-014, lines 280–313](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts#L280-L313).

## H06: Overlay economic invalidation

The supply filter excludes evicted outputs. The code's own comment identifies reissued frozen coins as remaining on chain. Native unspentness and economic money status must be represented separately.

Source: [TEN-017, lines 203–228](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/MandalaStorageManager.ts#L203-L228).

## H07: Control exceptions

Frozen/evicted-input checks occur before authority-transaction bypass of pause/access. Do not paraphrase the implementation as either no exceptions or unrestricted issuer bypass.

Source: [TEN-015, lines 77–97](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/controls.ts#L77-L97).

## H08: Rollback precondition

Input restoration requires caller confirmation that the engine regards it unspent and admitted again. Test actual reorg/eviction integration; merely finding the helper is not sufficient.

Source: [TEN-018, lines 453–456](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/MandalaLookupService.ts#L453-L456).

## H09: Multiple-topic broadcast

An accepted second topic may enable broadcast when the CBDC topic rejects. Restrict/verify the requested topic set and test actual chain-spend reconciliation; no topical rejection can revoke Bitcoin-valid signatures.

Source: [TEN-021, lines 1766–1777](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/overlay/src/Engine.ts#L1766-L1777).

## H10: SPV bypass mode

Normal submissions call transaction verification; the internal historical-no-SPV mode depends on prior independent inclusion verification. Ensure untrusted callers cannot obtain its trust.

Source: [TEN-021, lines 1719–1727](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/overlay/src/Engine.ts#L1719-L1727).

## H11: Exact script family

Regulated Mandala intentionally narrows base BRC-162 to canonical P2PKH and one-satoshi carriers. A custom co-signature or covenant lock cannot be silently substituted while claiming this unchanged profile.

Source: [TEN-019, lines 107–122](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/ownership.ts#L107-L122).

## H12: Action schema vs treasury approval

Issue optionally carries bankRef; redeem has no action-specific required keys here. No independent officer approval was identified in inspected schema/checks. Additional signed evidence must bind exact instruction and transaction.

Source: [TEN-027, lines 83–92](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/details.ts#L83-L92).

## H13: Decoder consistency

BTMS client recognizes metadata beginning with a JSON-object prefix; topic manager uses a printable/signature heuristic. Differential-test malformed/alternate metadata, field counts and script shape before trusting equal decoding.

Source: [TEN-005, lines 166–179](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/wallet/btms/src/BTMSToken.ts#L166-L179).

## H14: Source/spec status mismatch

Pinned BRC-162 says no implementation while the pinned ts-stack source contains regulated Mandala. Record source/code profile independently; do not claim normative completeness from a shared name.

Source: [TEN-010, lines 308–311](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0162.md#L308-L311).

## H15: Local lineage proof limits

BRC-176 scopes the proof to subject outputs and excludes global mint completeness and current UTXO membership. Regulated admin-control state is an additional obligation.

Source: [TEN-011, lines 42–50](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0176.md#L42-L50).

## H16: Covenant origin authenticity

Concrete covenant specification separates script transition validity from authenticated genesis/lineage. Require counterfeit-copy tests for proposed currency covenants as well.

Source: [TEN-024, lines 39–41](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0197.md#L39-L41).

## Explicit non-findings and limits

- The BRC-226 deployment assertions and constant-lineage claim were not verified against a live chain, implementation source or independent verifier. They are not adoption evidence.
- Upstream tests, published package integrity, node policy, wallet support, performance, storage atomicity and security audits were not validated in this task.
- No fee-charge path was established from Mandala's stored feeRatePerKb field. Native transaction fee accounting and any overlay service fee need separate qualification.
- No unspentness, mined inclusion or supply result was claimed for this project's current unsigned audit-anchor envelope.
- No legal or CBDC suitability conclusion follows from protocol availability or the name “regulated.”

