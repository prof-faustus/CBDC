"""BSV data-commitment boundary, without wallets, signing or broadcasting.

An OP_RETURN commitment is evidence anchoring, not a CBDC token covenant.
The local ledger remains authoritative in this experiment. Never equate an
anchor's inclusion with per-note on-chain spend validation or legal settlement.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone

from .ledger import LedgerError, canonical


TESTNET_INFO_URL = "https://api.whatsonchain.com/v1/bsv/test/chain/info"
DOMAIN = b"CBDC-LAB:TEST:V1"


def commitment_script(audit_head: str) -> str:
    """Return a small OP_FALSE OP_RETURN script with a domain and SHA256 head.

    No identities, balances, reasons, currency documents or public keys are put
    into the script. This function creates no transaction and spends no satoshis.
    """
    if not isinstance(audit_head, str) or len(audit_head) != 64:
        raise LedgerError("audit head must be 32 bytes in lowercase hex")
    try:
        head = bytes.fromhex(audit_head)
    except ValueError as exc:
        raise LedgerError("audit head must be hex") from exc
    if audit_head != head.hex() or len(head) != 32:
        raise LedgerError("audit head must be 32 bytes in lowercase hex")
    return (b"\x00\x6a" + bytes([len(DOMAIN)]) + DOMAIN + b"\x20" + head).hex()


def anchor_request(report: dict) -> dict:
    """Prepare a non-broadcast request for a separately reviewed testnet adapter."""
    if report.get("ok") is not True or report.get("mode") != "simulation":
        raise LedgerError("a successful synthetic ledger verification is required")
    script = commitment_script(report["audit_head"])
    body = {"schema": 1, "network": "bsv-testnet", "purpose": "synthetic-audit-commitment",
            "audit_head": report["audit_head"], "locking_script_hex": script,
            "output_satoshis": 0, "currency_principal_in_satoshis": False,
            "status": "unsigned_request_only", "broadcast_enabled": False}
    return {**body, "request_hash": hashlib.sha256(canonical(body).encode()).hexdigest()}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LedgerError("testnet observer refuses redirects")


def observe_testnet(*, opener=None) -> dict:
    """Read a fixed public provider endpoint. Provider assertion, not SPV proof.

    Fixed destination prevents accidental mainnet or arbitrary-URL calls.
    Redirects, oversized payloads and unexpected chain labels fail closed.
    """
    opener = opener or urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(TESTNET_INFO_URL, headers={"User-Agent": "CBDC-Lab-Testnet-Observer/0.1"})
    with opener.open(request, timeout=15) as response:
        raw = response.read(64_001)
        if len(raw) > 64_000:
            raise LedgerError("oversized provider response")
    try:
        body = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise LedgerError("invalid provider JSON") from exc
    if not isinstance(body, dict) or body.get("chain") != "test":
        raise LedgerError("provider did not report BSV testnet")
    height, block = body.get("blocks"), body.get("bestblockhash")
    if type(height) is not int or height < 0 or not isinstance(block, str) or len(block) != 64:
        raise LedgerError("invalid chain tip")
    try:
        if bytes.fromhex(block).hex() != block:
            raise ValueError()
    except ValueError as exc:
        raise LedgerError("invalid block hash") from exc
    return {"observed_at": datetime.now(timezone.utc).isoformat(), "source_url": TESTNET_INFO_URL,
            "source_response_sha256": hashlib.sha256(raw).hexdigest(), "chain": "test",
            "height": height, "best_block_hash": block,
            "verification": "provider_report_only", "transaction_submitted": False}
