"""Run the $100-equivalent denomination example using synthetic TUSD only."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from .anchor import anchor_request, observe_testnet
from .ledger import Actor, Currency, Ledger, Output


def actors() -> list[Actor]:
    return [Actor("mint-operator", "issuer"), Actor("mint-approver", "approver"),
            Actor("treasury", "treasury"), Actor("alice"), Actor("bob")]


def demonstration(path: Path) -> dict:
    ledger = Ledger(path, Currency(), actors())
    try:
        ledger.propose_mint("mint-operator", "mint-100", [Output("alice", 10_000)], "Synthetic issuance for denomination test")
        proposal = ledger.proposal("mint-100")
        minted = ledger.approve("mint-approver", "mint-100", proposal["hash"])
        split = ledger.transfer("alice", "split-2000", minted["outputs"], [Output("alice", 5) for _ in range(2_000)])
        split_count = len(split["outputs"])
        merged = ledger.transfer("alice", "merge-100", split["outputs"], [Output("alice", 10_000)])
        mixed = ledger.transfer("alice", "mixed-payment", merged["outputs"], [Output("bob", 3_335), Output("alice", 6_665)])
        redemption = ledger.transfer("bob", "redeem-to-treasury", [mixed["outputs"][0]], [Output("treasury", 3_335)])
        ledger.propose_retire("mint-operator", "retire-3335", redemption["outputs"], "Synthetic redemption; no external cash payout")
        ledger.approve("mint-approver", "retire-3335", ledger.proposal("retire-3335")["hash"])
        report = ledger.verify()
        return {"mode": "simulation", "currency": "TUSD", "real_money": False,
                "issued_minor_units": 10_000, "five_cent_outputs_created": split_count,
                "merged_minor_units": merged["amount"], "retired_minor_units": 3_335,
                "remaining_minor_units": report["supply"], "verification": report,
                "bsv_anchor_request": anchor_request(report)}
    finally:
        ledger.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observe-testnet", action="store_true", help="read public BSV testnet status; sends no transaction")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="cbdc-synthetic-") as tmp:
        result = demonstration(Path(tmp) / "test.db")
        if args.observe_testnet:
            result["testnet_observation"] = observe_testnet()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
