# Central-bank architecture research

Research snapshot: 2026-10-07. This package is a jurisdiction-neutral foundation for a public CBDC research repository. It contains no private information, credentials, copied full reports, or production deployment instructions.

## Read in this order

1. [Architecture and monetary model](central-bank-architecture.md): what the system represents, its institutional boundary, and a proposed research architecture.
2. [Operational control baseline](operational-control-baseline.md): governance, privacy, keys, recovery, finality and assurance work that a token implementation cannot replace.
3. [Primary-source register](sources.md): 15 selected primary references, publication dates and status caveats.
4. [Machine-readable evidence](evidence.json): supported claims, source locations, retrieval notes and limitations.

## Status vocabulary

- Source finding: a bounded claim supported by the cited publication.
- Research proposal: a recommended design or test for this repository, not a claim that a central bank has adopted it.
- Jurisdiction decision: a matter left open until an issuer, legal framework and accountable authorities are selected.
- Prototype: synthetic money and test identities only. A working token or ledger creates neither central-bank issuance authority nor legal-tender status.

The international material concentrates on retail/general-purpose CBDC. Wholesale settlement has different participants, access rules and risk profiles; it should receive a separate design profile rather than inherit retail assumptions silently. Country examples illustrate alternatives. They are not a country selection.

The requested research profile also includes a government-controlled treasury mint/retire area, separately governed from the central-bank legal issuer; synthetic suspense-versus-liability accounting; and holder-authorised denomination splits/merges that conserve value. Those are project requirements, not findings that every central bank uses that design.

## Important source-status cautions

- The IMF legal paper is historical staff research. Its 2020 survey conclusions are not a current country-by-country legal assessment.
- The ECB FAQ was updated on 2026-08-17 and remains prospective about issuance. Its design intentions and hypothetical holding-limit analysis are not proof of deployment or enacted legislation.
- PFMI and the associated cyber guidance are international FMI standards/guidance. Applicability to a particular CBDC and its operator must be assessed.
- NIST SP 800-57 Part 1 Revision 5 is a final lifecycle reference; the checked project page also lists a Revision 6 draft. Algorithm choices require a fresh implementation-time review.
- The foundational BIS report's landing page and indexed PDF excerpts were inspected, but direct retrieval of its full PDF failed. That limitation is recorded rather than concealed.

## Out of scope

No selected sovereign issuer, national legal opinion, official accounting policy, certified privacy claim, production security assurance, or permission to handle real funds is implied. Nothing here establishes central-bank endorsement of this repository.
