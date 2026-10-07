# Research index and provenance

Snapshot date: **7 October 2026**. The evidence set contains 56 primary-source entries or direct service observations: 15 central-bank/security/legal references, 13 BSV/source/network references and 28 token-enforcement source files/specifications. Original engineering proposals are labelled separately from source facts.

## Read in this order

1. [Central-bank architecture, monetary model and treasury](central-bank/central-bank-architecture.md)
2. [Operational control baseline](central-bank/operational-control-baseline.md)
3. [Central-bank source summaries](central-bank/sources.md) and [machine-readable evidence](central-bank/evidence.json)
4. [BSV implementation and network findings](bsv-integration.md) and [machine-readable evidence](bsv-evidence.json)
5. [BSV token-enforcement comparison](token-enforcement/candidate-comparison.md), [qualification obligations](token-enforcement/review-hotspots.md) and [pinned evidence](token-enforcement/token-enforcement-evidence.json)
6. [Project decisions](../architecture/decisions.md), [treasury contracts](../architecture/treasury-and-denominations.md) and [threat model](../architecture/threat-model.md)
7. [Implementation roadmap](../implementation-plan.md) and [performance acceptance plan](../testing/performance-plan.md)

## Evidence rules

- Every external claim has a primary-source URL and retrieval date. Publication dates are recorded when available; undated live documentation is marked accordingly.
- Distinguish reports, proposals, current source code, enacted law, reference software and direct measurements. They establish different kinds of facts.
- Source access limits are explicit. A landing page or indexed excerpt is not described as a fully inspected PDF.
- GitHub source references are pinned to a commit where available. Source manifest versions do not establish published package versions or installed dependency integrity.
- Service observations record time, URL, returned chain/height and a response digest. They are not independent consensus proofs.
- Preserve both supporting findings and limits. A blockchain capacity test does not measure the application built here.
- No private manuscript, dissertation, patent dossier, identity document, correspondence or private planning file is included. References do not establish ownership, enforceability, licensing or freedom to operate.
- Recheck legal and software sources before a stage depends on them. Do not silently overwrite historical evidence; add a dated observation and explain any changed conclusion.

## Next research questions

Select a pilot jurisdiction and legally responsible issuer; define rights and redemption; settle retail/wholesale and privacy requirements; compare BSV token enforcement patterns; specify custody and recovery authorities; pin a reviewed SDK/runtime; and design a repeatable end-to-end performance/failure corpus.

The current repository preserves a foundation for continuing that work. It is not an exhaustive survey or completed CBDC specification.
