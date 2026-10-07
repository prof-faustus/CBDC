# Stage 1: BSV token-enforcement candidate comparison

Research date: 7 October 2026. Decision status: **shortlist only; source review only; no testnet lifecycle executed**.

## Result

The closest current official code candidate is **the regulated `tm_mandala` profile in `@bsv/overlay-topics`**, not plain BTMS. It implements exact holder-transfer conservation and issuer-controlled supply changes, plus freeze and recovery policy. Its monetary and administrative controls are **overlay-enforced above P2PKH**, however. Plain BRC-162/Mandala and the regulated profile must not be described as interchangeable. [TEN-010](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0162.md), [TEN-012](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/MandalaTopicManager.ts), [TEN-014](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts)

Keep two on-chain candidates for a focused next experiment: (1) a precisely specified issuer-and-holder co-signed UTXO design, and (2) the pinned regulated Mandala profile with additional treasury governance. Keep the authoritative issuer ledger plus audit anchors as the comparison baseline. A miner-enforced fungible covenant remains a separate proof-development option; the named covenant specifications inspected here are not a drop-in CBDC implementation.

This is a technical shortlist, not a claim of security audit, legal suitability, interoperability, production readiness, or 100,000 TPS performance.

## Evidence boundary and versions

- Inspected `bsv-blockchain/ts-stack` commit: `edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9`.
- Source manifests: `@bsv/btms` 1.2.4 and `@bsv/overlay-topics` 2.0.1; the project had separately inspected SDK 3.2.0 at that head. These are source-manifest observations, not published-artifact/integrity checks. [TEN-007](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/wallet/btms/package.json), [TEN-026](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/package.json)
- Inspected `bsv-blockchain/BRCs` head: `ed1b015bac53106ff34e5d1831acda378cbe5c04`. All external links below are commit-pinned.
- Read the project's `docs/research/bsv-integration.md` and `docs/architecture/treasury-and-denominations.md`. No project-worktree files were changed.
- Public documentation and source reads only. No SDK install, external-code execution, wallet creation, secret retrieval, key generation, signatures, funding, broadcast, or user-computer access occurred.
- The companion [evidence registry](token-enforcement-evidence.json) contains source/blob identifiers, supported claims and limits. [Review hotspots](review-hotspots.md) supplies exact source locations and test priorities.

## Non-negotiable distinction

For the proposed instrument, value is an integer number of currency minor units. It is not native BSV satoshis. Native consensus checks the transaction's Bitcoin validity, locking scripts and the spend graph. It does not automatically understand the currency amount, issuer's legal power, policy approvals, holding limit, identity, liability journal, or retirement rule.

Dropped token fields remain committed in transaction bytes but are not evaluated as token economics by a plain P2PK/P2PKH spend. A holder signature authorizes the Bitcoin spend; it does not imply that a token validator will accept the successor. A transaction can be Bitcoin-valid and destroy its token eligibility. A Merkle inclusion proof does not establish current unspentness or a complete token supply. [TEN-001](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/scripts/0048.md), [TEN-002](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/sdk/src/script/templates/PushDrop.ts), [TEN-010](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0162.md), [TEN-011](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0176.md)

### Enforcement map

| Candidate | Currency conservation and mint/retire policy | Holder spend condition | Freeze/recovery authority | Lineage authority |
|---|---|---|---|---|
| Authoritative issuer ledger + anchors | Issuer service, transactional ledger and independent approval/journal checks | Ledger authentication/authorization | Ledger policy and recovery workflow | Ledger history; anchors commit selected records |
| Proposed issuer-co-signed UTXOs | Co-signer's validation service unless also encoded in a covenant | Script requires holder **and** issuer signatures | Refuse co-signing; recovery needs an explicit alternate branch or external invalidation | Authenticated issuance roots plus admitted spend DAG |
| Plain BTMS / BRC-48 | BTMS topic admission; output allowance is ≤ inputs; ISSUE creates a new asset | Generated PushDrop P2PK owner signature | No standard issuer freeze/recovery in inspected manager | Topic's admitted predecessors and retained ancestry |
| Base BRC-161/162 | Token validator/indexer; authority permits minting; implicit burn permitted | Whatever locking script follows token carrier | Only what additional scripts/profile specify | Token DAG and authority lineage; BRC-176 can package it |
| Regulated `tm_mandala` | Overlay authority/controls modules and state store; exact holder delta zero | Exact P2PKH in this profile, plus overlay owner linkage | Overlay control journal, freeze, evict/reissue; old coin remains on chain | Admitted predecessors, owner journal, authority/admin history and policy configuration |
| Purpose-built covenant | Only predicates actually encoded and proven in Script | Chosen script authorization on every branch | Must be explicitly encoded or delegated | Authenticated genesis plus required predecessor evidence; copying script bytes is insufficient |

The first two rows are architectural constructions for this project, not existing implemented protocol claims. Source-specific rows are supported by the sections below.

## Candidate A: authoritative issuer ledger with audit anchors

The existing local model is a useful behavior specification, but not an implemented distributed monetary system. The issuer ledger would be authoritative for outstanding notes, exact sums, holding limits, approvals and journal balances. Transactional storage must make consumption, output creation, supply changes, accounting and idempotency indivisible.

BSV anchors would bind a domain-separated checkpoint or event commitment to a transaction and, after verification, to a block. They neither execute local transfers nor prove that the issuer supplied complete, truthful records. Independent audit needs the committed records, canonical serialization, append-only sequencing, consistency proofs, reconciliation and a policy for omitted or delayed anchors.

- **Mint/retire:** the ledger must bind independent approval to the precise operation; anchor publication is not that approval.
- **Split/merge:** exact ledger sums and ownership checks; chain carries the audit commitment, not necessarily one UTXO per note.
- **Fees:** separate BSV-funded anchoring transactions; no currency-principal deduction.
- **Freeze/recovery:** ledger policy, with evidence and reversible states; disclose administrative power.
- **No-go:** describing this as consensus-enforced note ownership or token transfer.

## Candidate B: issuer-and-holder co-signed note UTXOs

A proposed two-party lock can require a valid holder signature and issuer co-signature before a note UTXO is spent. With a deliberately selected signature scope binding all required inputs and outputs, miners enforce the signatures. **The issuer service still enforces the currency equations unless a covenant separately proves them.** An issuer that signs a malformed successor can authorize a consensus-valid inflationary token representation.

The co-signer must authenticate every input's currency, amount, owner, issuer-policy version and lineage; check every output and all change; distinguish mint, transfer and retirement; and never sign an unchecked alternate transaction. A root registry or equivalent authenticated issuance authority is necessary: a matching script and issuer-name metadata do not establish a genuine note.

- **Mint:** authenticated issuer creation procedure; co-signing a spend does not itself limit new issuance.
- **Retire:** spend only treasury-controlled notes under a bound independent retirement approval, creating no spendable currency replacements.
- **Holder authorization:** require each owner, including every party to a cross-owner merge; bind the exact funded transaction.
- **Split/merge:** co-signer verifies same currency and policy compatibility and exact conservation, then signs the complete fan-out.
- **Fees:** sponsor inputs/change in BSV, separate from principal; signature scope must resist fee sponsor mutation.
- **Freeze:** refusing future co-signatures prevents this normal spend path. It cannot revoke a transaction already validly signed; signing queues and freeze races need a defined cutoff.
- **Recovery:** pure holder+issuer co-signing cannot recover a permanently lost holder key. A threshold/time-delayed recovery branch changes the authorization promise and must be specified up front. External invalidation plus reissue instead introduces overlay/ledger authority.
- **Availability:** every ordinary transfer depends on issuer signing capacity and policy availability; a global signing bottleneck is not removed merely by using many UTXOs.

This option can make mandatory issuer participation consensus-visible. It does not, by that fact alone, make supply policy consensus-enforced.

## Candidate C: BTMS built on BRC-48

BRC-48 specifies spendable metadata with a simple public-key lock and expressly leaves higher-order token rules unspecified. The current SDK can place the P2PK lock before or after the dropped data; BTMS uses its generated default. Do not test only the old prose's script order. [TEN-001](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/scripts/0048.md), [TEN-002](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/sdk/src/script/templates/PushDrop.ts), [TEN-005](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/wallet/btms/src/BTMSToken.ts)

At the pinned code:

- `ISSUE` is always admitted as a new asset whose identity is its issuance outpoint. No trusted central-bank issuer check appears in the inspected topic manager. Repeated ISSUE transactions create distinct assets; a display name does not merge them into one currency. [TEN-003](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/btms/BTMSTopicManager.ts)
- Per-asset transfer outputs may total **less than** admitted inputs, intentionally burning the difference. Any holder able to spend the Bitcoin lock can burn, including by making no replacement token output. This conflicts with the project's issuer-only retirement contract. [TEN-003](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/btms/BTMSTopicManager.ts), [TEN-004](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/btms/__tests/BTMSTopicManager.test.ts)
- The manager admits outputs sequentially up to their allowance. Its test explicitly accepts the first outputs of an over-output split. This differs from both all-or-nothing regulated transfers and base BRC-162's per-token all-or-nothing rule. An overlay acknowledgment must be checked for the complete intended output set. [TEN-004](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/btms/__tests/BTMSTopicManager.test.ts), [TEN-010](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0162.md)
- Split/merge and unchanged metadata are overlay checks. The normal owner signature is miner-checked; the miner does not total BTMS currency fields. [TEN-002](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/sdk/src/script/templates/PushDrop.ts), [TEN-003](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/btms/BTMSTopicManager.ts)
- Default carrier value is one satoshi; token values are canonical positive safe integers up to 9,007,199,254,740,991. Currency precision and minimum denomination remain scheme rules. [TEN-005](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/wallet/btms/src/BTMSToken.ts), [TEN-006](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/wallet/btms/src/constants.ts)
- Wallet prompts and digest binding help protect holder intent, but that module's qualifying issuance auto-approval is not CBDC issuer authorization. [TEN-008](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/wallet/btms-permission-module/README.md)

**Stage 1 verdict:** useful reference for wallet/overlay transport and small token tests, not an unchanged match for this project's treasury semantics.

## Candidate D: base BRC-161/162 and the regulated Mandala implementation

### Base standard

BRC-161 is legacy JSON BSV-21. BRC-162 specifies the binary Mandala representation, with a stable deploy-outpoint identity, value outputs and zero-amount authority outputs. Authority may be split, transferred, combined or ended. Spending valid authority permits minting without existing value coverage; ordinary value admission uses input ≥ output and allows implicit burns. Base amounts extend to 2^64−1. A compromised authority can mint unrestricted supply under that base model. [TEN-009](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0161.md), [TEN-010](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0162.md)

The base standard places identity/amount in a dropped prefix and permits different remainder scripts. It explicitly assigns token rules to validators/indexers, not consensus. Thus arbitrary covenants are *possible compositional locks*, not an automatic property of a Mandala token. The base payload/display fields do not impose monetary governance. [TEN-010](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0162.md)

BRC-176 is relevant to independent verification: a split/merge proof needs recursively sufficient token-parent bodies to the deploy/authority, including the same-id inputs and sibling output amounts needed for each conservation check. Ordinary SPV-minimal BEEF may omit exactly those bodies. BRC-176 proves scoped local token lineage, not global supply, no-other-mints, or unspent status. It also does not automatically prove the stricter regulated profile's administrative history. [TEN-011](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0176.md)

### Actual `tm_mandala` profile at the pinned source

This is materially more relevant than the base token rules:

- **Conservation:** a transfer without authority must have exact zero supply delta. Authority operations require a committed action: issue > 0, redeem < 0, reissue equal to the recorded frozen amount, otherwise zero. [TEN-014](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts)
- **Issuer:** deploy and authority owners/provers must be trusted; deploy is signed; authority predecessors must be admitted and trusted; consumed authority must be recreated. Removing a key from the trusted set affects authority use, so rotation order matters. [TEN-012](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/MandalaTopicManager.ts), [TEN-014](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts)
- **Holder:** outputs must be exactly canonical P2PKH with one satoshi, with owner linkage verified by the overlay; input ownership comes from maintained owner records/journal. Consensus checks the P2PKH signature, not that linkage or the owner's legal status. [TEN-013](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/MandalaTopicDocs.md.ts), [TEN-019](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/ownership.ts)
- **Amounts/split/merge:** the regulated profile imposes safe-integer caps on amounts, sums and indexed circulating supply, stricter than base BRC-162. Bigint internal sums do not remove this public profile cap. Minimum unit 0.05 and 2,000-output handling still need a project profile and tests. [TEN-014](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts), [TEN-020](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/brc162/ledger.ts)
- **Controls:** frozen/evicted inputs are rejected; pause, allow/deny access, screening and optional membership are applied. Authority transactions bypass some pause/access conditions, not frozen-input checks or sanctions. [TEN-015](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/controls.ts)
- **Recovery:** reissue targets a frozen amount, requires the stated recipient and forbids value inputs. State then marks the old outpoint evicted; supply calculation excludes it although it remains on chain. This is administrative invalidation, not a Bitcoin spend or consensus destruction of the old note. [TEN-014](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts), [TEN-016](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/AssetStateReducer.ts), [TEN-017](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/MandalaStorageManager.ts)
- **Fees:** native BSV funding is separate. A fee-rate field and setFeeRate action exist; the inspected authority/control modules do not establish a complete fee-collection/sponsorship path. Do not claim a stored fee rate proves payment. [TEN-013](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/MandalaTopicDocs.md.ts), [TEN-016](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/AssetStateReducer.ts)
- **Lineage/state:** admitted source outputs, the owner journal, off-chain linkage/admin details, trusted configuration and ordered admin state are necessary. Commitments protect details from substitution but do not make withheld details available. Recovery primitives exist; their correct integration is still a proof obligation. [TEN-018](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/MandalaLookupService.ts), [TEN-020](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/brc162/ledger.ts), [TEN-021](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/overlay/src/Engine.ts)

**Missing CBDC governance:** no independent treasury-officer approval or treasury-owned-input restriction was identified in the inspected issue/redeem checks and action schema. Trusted authority key control is not the project's two-person approval. Those requirements need an additional reviewed signing/service layer or changed script/profile. [TEN-014](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/authority.ts), [TEN-027](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/src/mandala/details.ts)

**Source/spec mismatch:** BRC-162's Implementations section says none yet, while current ts-stack contains the regulated implementation above. Use the pinned implementation and explicit profile, not that stale status sentence or the shared “Mandala” label, as the comparison object. [TEN-010](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0162.md), [TEN-028](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/topics/README.md)

**Stage 1 verdict:** best concrete official-code candidate for a controlled overlay research pilot, conditional on accepting overlay-authoritative monetary validity and closing governance, recovery and concurrency gaps. Not a consensus-enforced CBDC.

## Candidate E: actual covenant mechanisms and why they are not substitutes yet

BRC-21 describes binding a pushed transaction preimage through CHECKSIG, allowing Script to constrain transaction fields and successor outputs. It is not a new native opcode or a complete currency design. [TEN-023](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/scripts/0021.md)

BRC-197 is a useful concrete comparison: its revenue-listing family specifies exact program/ABI, authenticated full-output constraints, split/merge and retirement rules, external fee funding and separate authenticated-genesis/lineage checks. It explicitly distinguishes Script-valid copied/funded branches from valid domain lineage. But it accounts for satoshi revenues, uses tightly bounded routes (at most eight inputs and eleven outputs), and is not the project's freely denominated fiat instrument. Its included executable corpus was not run here. [TEN-024](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0197.md)

BRC-226 is a named royalty-covenant proposal describing transfer, permissionless purchase/replication, and holder burn. The spec's deployment and genesis-only verification claims were not independently verified here. Replication and holder burn are not the desired restricted CBDC supply policy. A matching genesis commitment must not be assumed to establish scarce authorized issuance; require an adversarial copied-script/genesis test before adopting any constant-lineage claim. [TEN-025](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0226.md)

**Stage 1 verdict:** covenant feasibility is credible at the mechanism level; no inspected named covenant supplies a proven, ready-to-adopt 2,000-output CBDC lifecycle. A new/adapted family needs exact byte-level semantics, independent Script execution and authenticated lineage proofs.

## Go/no-go proof obligations before any funded testnet lifecycle

All items below are **pending qualification**, not failed tests and not completed implementation claims.

1. **Freeze the scheme profile.** Name chain, issuer root, currency id, minor unit/minimum denomination, amount/aggregate caps, enabled script family, all administrative branches and policy version. Resolve whether monetary validity is ledger-, overlay-, or covenant-authoritative.
2. **Prove issuer governance.** Exact proposal hash plus independent authenticated approval must bind issue/retire/recovery; reject replay, modified amounts, unauthorized issuer, compromised/delegated authority, omitted authority continuation and non-treasury retirement inputs.
3. **Prove conservation.** Use local model vectors and an independent exact-integer oracle. Test 100.00 → 2,000 × 0.05; merge back; 33.35/66.65 transfer; cross-owner input authorization; duplicate inputs; unrelated asset ids; bogus genesis; zero/negative/overflow/noncanonical values; missing/extra output; burns and over-output failures. A 2,000-output reshape counts as one operation.
4. **Bind the complete transaction.** Reject recipient, amount, script, input, fee, change, order, locktime, sequence and signature-scope changes after approval. For co-signing/covenants test missing holder/issuer signatures and every alternate spend path, not just SDK-generated happy paths.
5. **Test bypass explicitly.** After separate authorization, show what a raw consensus-valid but token-invalid spend does when sent outside the overlay. Test rejected Mandala plus another accepted topic in the engine: current engine broadcast eligibility is “any accepted topic.” Never equate a rejected topical transaction with an unspent chain input. [TEN-021](https://github.com/bsv-blockchain/ts-stack/blob/edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9/packages/overlays/overlay/src/Engine.ts)
6. **Prove recovery accounting.** Race transfer/freeze/reissue; attempt the old-coin spend after reissue; repeat reissue; lose/rebuild the overlay; evict/reorg the admin transaction and descendants. At every state, exactly one authorized economic claim survives and the issuer liability reconciles. Decide legal treatment of deliberately destroyed token eligibility.
7. **Prove lineage and availability.** Independently replay from authenticated genesis, with all required merges/authority/admin histories. Missing bodies, details, journal rows or trust configuration must fail closed or report unresolved. Test forged headers/proofs, spent tips, withheld history and two providers disagreeing. Base BRC-176 alone is insufficient for regulated-control validity. [TEN-011](https://github.com/bsv-blockchain/BRCs/blob/ed1b015bac53106ff34e5d1831acda378cbe5c04/tokens/0176.md)
8. **Prove concurrency/atomicity.** Multiple issuer authorities, simultaneous mints near the cap, concurrent spends, late provider acknowledgments, broadcast-success/storage-failure and restart must not inflate balance or silently lose liability. Indexed supply-read checks require serialization or another demonstrated conflict-control mechanism; source inspection has not established it.
9. **Separate funding economics.** With one-satoshi carriers, 2,000 outputs lock 2,000 native satoshis in addition to fees; those satoshis do not equal 100 currency units. Measure actual signed byte size, fee, input/output/signature counts and wallet/provider limits. Verify sponsor change cannot consume currency principal or substitute recipients.
10. **Qualify the actual deployment.** Pin package versions/integrity/source mapping and licenses; run upstream, differential and property tests; inspect compiler output if using covenants; validate against a separate interpreter/node profile; qualify real wallet, overlay, broadcaster and testnet endpoint behavior. Recheck amount/schema differences between all components.
11. **Define finality/recovery states.** Preserve exact raw transaction/txid on ambiguous broadcast; independently distinguish submitted, observed, included, orphaned/conflicted and policy-final. No automatic replacement mint on timeout.
12. **Obtain bounded execution approval.** Select test-only wallet/key custody, testnet funding, fee limit, destination services and allowed signing/broadcast operations. No real value, mainnet fallback or private identity/admin data should enter the public experiment. Current research does not authorize those actions.

**Go:** a no-value, explicitly authorized testnet experiment only after a written profile, deterministic negative corpus, verified signing boundary and recovery design pass review. **No-go:** a production/CBDC readiness claim; adoption based on names or source tests alone; or skipping bypass, lineage, governance and recovery tests.

## Suggested next bounded comparison

Build two adapters against the same behavior corpus without broadcasting: a co-signing-policy model and the regulated Mandala profile. Keep the ledger+anchors baseline and record which invariants each adapter enforces in Script, signer, overlay and ledger. First resolve the issuer-only-retirement and recovery semantics; then qualify byte-level transactions under separately approved test credentials. This yields a defensible representation decision before committing to a funded lifecycle.
