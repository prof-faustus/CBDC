# BSV integration: verified sources and execution boundary

Research date: 7 October 2026. Source identifiers refer to [bsv-evidence.json](bsv-evidence.json).

## Maintained code and version selection

The official standalone `bsv-blockchain/ts-sdk` repository is archived. Current development is in [ts-stack](https://github.com/bsv-blockchain/ts-stack), which brings together SDK, wallet, network and overlay packages. The inspected source commit is `edf6e03dad39bd7bc4fc6e73e64de3a2b6f805c9` (7 October 2026). Its SDK manifest reports 3.2.0 with Node.js >=22. This is a source-manifest observation, not verification of an npm release. [BSV-001, BSV-007]

The inspected SDK licence is Open BSV License Version 6, including BSV-specific use and notice conditions. No legal compatibility or patent conclusion follows from inspecting it. The first reference model does not import or redistribute SDK code. Dependency adoption remains a separate implementation decision. [BSV-002]

A reproducible integration must pin the exact package version and integrity digest, record its source mapping, review scoped third-party notices, generate a dependency inventory and run the SDK's applicable conformance tests. Never install “latest” implicitly during a release build.

## Network options and availability

- **BSV testnet:** official documentation describes a public unmanaged test network and lists faucet options. Listing a faucet does not verify that it currently serves coins. [BSV-008]
- **Local regtest:** the official Teranode quickstart offers an isolated testing profile. Its documented setup involves multiple services and generates service credentials; it was not run here. [BSV-009]
- **Teratestnet/scaling profiles:** these are distinct configurations, not interchangeable names for the public testnet. Profile selection and provider support must be verified before use. [BSV-009]

A live credential-free HTTPS request to [WhatsOnChain testnet chain information](https://api.whatsonchain.com/v1/bsv/test/chain/info) succeeded. The recorded run at 08:20:33 UTC reported `chain=test`, height 1,761,928. This establishes point-in-time read access to that provider. It does not prove node independence, spendable test funds, transaction inclusion, a broadcast contract or service-level capacity. [BSV-010; saved observation](../testing/demo-and-testnet-observation.json)

## Avoid mainnet defaults

The inspected SDK `defaultBroadcaster()` selects mainnet unless its testnet argument is enabled; the testnet branch points to `https://testnet.arc.gorillapool.io`. The WhatsOnChain broadcaster likewise defaults to `main` and accepts explicit `test`/`stn` selectors. These defaults must be overridden and guarded in a future adapter. Endpoint strings in code are not endpoint uptime evidence. [BSV-003, BSV-004]

The inspected funding helper accepts an explicit chain and protects key entry from command-line arguments. It is a wallet-dependent tool, not a faucet or permission-free funding path. No helper, wallet, key or funding operation was created in this work. [BSV-006]

## What the executable adapter boundary actually does

`cbdc_lab.anchor` implements only:

1. A fixed, HTTPS, read-only testnet observer with redirect refusal, response-size limits and schema checks.
2. A minimal `OP_FALSE OP_RETURN` script carrying a test-domain string and a 32-byte audit digest.
3. A deterministic unsigned request envelope that says `broadcast_enabled=false` and `status=unsigned_request_only`.

There is no transaction object, signing key, fee input, broadcaster, chain UTXO, token validator, header store or Merkle proof in that code. Unit-test HTTP responses use explicitly named stubs. The saved live observation is the only external network execution in the recorded demo.

## Representation decision still required

The project's money amounts cannot be equated to native BSV output satoshis. Candidate designs must be compared on enforceable supply conservation, holder authorization, issuer authority, freeze/recovery semantics, data availability, privacy and fee sponsorship:

| Candidate | What must be established | Main unresolved issue |
|---|---|---|
| Authoritative issuer ledger with BSV audit anchors | Independent commitments, availability and audit/reconciliation | Anchors do not make local note transfers consensus-enforced |
| Issuer-co-signed note outputs | Complete issuance lineage, exact output values and mandatory issuer authorization | Central service dependence and override/recovery powers |
| Script/covenant or token protocol | Machine-checkable conservation and authorization proof, upgrade and recovery rules | Script constraints, lineage verification, metadata trust and economic cost |

The initial local model is deliberately not labelled a completed implementation of any of these on-chain token designs. The local tests form a reusable behavior specification for evaluating them.

## Submission, inclusion and finality

Teranode describes distinct transaction validation, propagation, assembly and blockchain integration stages. Its conflict documentation includes reorganisations and effects on descendants. Applications therefore need transaction identity, block identity and reversible observation state rather than a single “sent” flag. [BSV-011, BSV-012]

The inspected ARC code accepts several status classes while rejecting explicit invalid/conflicting/stale-block responses and checks returned transaction IDs. A library-level success or provider status label is still not the scheme's finality determination. [BSV-005]

Proposed network state machine: `prepared → signed → submitted/unknown → observed → included → confirmation_policy_satisfied`, with branches to `rejected`, `conflicted`, `orphaned` and `manual_review`. Legal settlement is a separate determination under the chosen rulebook. A timed-out broadcast keeps the same raw transaction and txid; it must not automatically mint a replacement payment.

## Capacity evidence

[AWS's 31 March 2026 report](https://aws.amazon.com/blogs/web3/how-the-bsv-association-built-a-million-tps-blockchain-node-using-aws/) describes six distributed competing Teranode nodes achieving sustained one-million-TPS processing for two weeks with zero transaction loss. It expressly describes a test implementation rather than a full production system. The reported blockchain achievement is important evidence; it does not contain this CBDC application's identity, policy, treasury, privacy, reconciliation or legal-finality workload. [BSV-013]

The required operating floor for this project is **100,000 TPS**. It is neither a universal CBDC standard nor a result of running this repository. The [performance plan](../testing/performance-plan.md) defines how to test the complete service without disguising output fan-out as extra customer payments.
