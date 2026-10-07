import io
import json
import unittest
from urllib.error import URLError

from cbdc_lab import LedgerError
from cbdc_lab.anchor import DOMAIN, TESTNET_INFO_URL, anchor_request, commitment_script, observe_testnet


class StubOpener:
    def __init__(self, response):
        self.response = response
        self.requests = []
    def open(self, request, timeout):
        self.requests.append((request.full_url, timeout))
        return io.BytesIO(self.response)


class AnchorTests(unittest.TestCase):
    def test_script_contains_only_domain_and_digest(self):
        raw = bytes.fromhex(commitment_script("12" * 32))
        self.assertEqual(raw, b"\x00\x6a" + bytes([len(DOMAIN)]) + DOMAIN + b"\x20" + b"\x12" * 32)

    def test_invalid_heads(self):
        for value in ("", "z"*64, "A"*64, "0"*63, None, " "*64):
            with self.subTest(value=value), self.assertRaises(LedgerError):
                commitment_script(value)

    def test_request_never_enables_broadcast(self):
        report = {"ok": True, "mode": "simulation", "audit_head": "12"*32}
        request = anchor_request(report)
        self.assertFalse(request["broadcast_enabled"])
        self.assertEqual(request["network"], "bsv-testnet")
        self.assertEqual(request["output_satoshis"], 0)
        self.assertEqual(request, anchor_request(report))

    def test_invalid_verification_rejected(self):
        for report in ({}, {"ok": False, "mode": "simulation"}, {"ok": True, "mode": "mainnet"}):
            with self.assertRaises(LedgerError): anchor_request(report)

    def test_observer_fixed_testnet_endpoint(self):
        opener = StubOpener(json.dumps({"chain": "test", "blocks": 123, "bestblockhash": "ab"*32}).encode())
        result = observe_testnet(opener=opener)
        self.assertEqual(opener.requests, [(TESTNET_INFO_URL, 15)])
        self.assertEqual(result["height"], 123)
        self.assertFalse(result["transaction_submitted"])
        self.assertEqual(result["verification"], "provider_report_only")

    def test_observer_rejects_wrong_network_and_malformed_responses(self):
        bodies = [b"no json", b"[]", b"null", b"x"*64_001,
                  json.dumps({"chain": "main", "blocks": 1, "bestblockhash": "ab"*32}).encode(),
                  json.dumps({"chain": "test", "blocks": True, "bestblockhash": "ab"*32}).encode(),
                  json.dumps({"chain": "test", "blocks": 1, "bestblockhash": "zz"*32}).encode()]
        for body in bodies:
            with self.subTest(body=body[:50]), self.assertRaises(LedgerError):
                observe_testnet(opener=StubOpener(body))


if __name__ == "__main__": unittest.main()
