# Project working rules

- This is research and synthetic test software. Never describe it as sovereign money, government-approved, production-ready or certified.
- Preserve existing files and concurrent changes. Use an isolated branch for substantive changes. Create a pull request only when explicitly authorized; do not merge or deploy without authorization.
- Use public primary sources. Record dates, exact URLs, versions, claims, limitations and access status. Do not add private manuscripts, identity records, keys, secrets or unpublished patent material.
- Keep one instrument, issuer definition and integer unit scale per ledger. Splits, merges and ordinary payments must conserve supply.
- Separate treasury administration from legal issuance authority. Supply changes require independently authorized instructions and matching accounting entries.
- Keep fees denominated in BSV separate from currency principal. Do not describe API acceptance, local commit, block inclusion and legal finality as interchangeable.
- Mainnet and real-value operations are out of scope. Do not silently enable broadcasters, wallets, credentials or services.
- Test doubles and local simulations must say so. Never label a mock response or unsigned request an executed on-chain transaction.
- Run `python -m unittest discover -v`, `python -m compileall -q cbdc_lab tests` and `python scripts/check_research.py` before publishing changes. Network observation is an optional distinct check.
- Preserve user-specified minimum operating requirement of 100,000 TPS while distinguishing it from observed results.
