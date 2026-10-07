import random
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from cbdc_lab import Actor, Currency, Ledger, LedgerError, Output
from cbdc_lab.demo import actors, demonstration


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ledger.db"
        self.registry = actors() + [Actor("frozen", frozen=True), Actor("inactive", active=False), Actor("limited", holding_limit=50)]
        self.currency = Currency()
        self.ledger = Ledger(self.path, self.currency, self.registry)

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def mint(self, amount=10_000, to="alice", key="mint"):
        self.ledger.propose_mint("mint-operator", key, [Output(to, amount)], "test issuance")
        return self.ledger.approve("mint-approver", key, self.ledger.proposal(key)["hash"])

    def test_exact_100_to_2000_five_cents_and_back(self):
        original = self.mint()
        split = self.ledger.transfer("alice", "split", original["outputs"], [Output("alice", 5)] * 2_000)
        self.assertEqual(len(split["outputs"]), 2_000)
        self.assertEqual(self.ledger.supply(), 10_000)
        merged = self.ledger.transfer("alice", "merge", split["outputs"], [Output("alice", 10_000)])
        self.assertEqual(len(merged["outputs"]), 1)
        self.assertEqual(self.ledger.verify()["supply"], 10_000)

    def test_mixed_denominations(self):
        minted = self.mint()
        self.ledger.transfer("alice", "mixed", minted["outputs"], [Output("bob", 3_335), Output("alice", 6_665)])
        self.assertEqual(self.ledger.balance("bob"), 3_335)
        self.assertEqual(self.ledger.balance("alice"), 6_665)
        self.ledger.verify()

    def test_proposal_has_no_economic_effect(self):
        self.ledger.propose_mint("mint-operator", "mint", [Output("alice", 100)], "test")
        self.assertEqual(self.ledger.supply(), 0)
        self.assertEqual(self.ledger.proposal("mint")["state"], "proposed")
        self.ledger.verify()

    def test_issuer_cannot_approve_own_proposal(self):
        self.ledger.propose_mint("mint-operator", "mint", [Output("alice", 100)], "test")
        with self.assertRaises(LedgerError):
            self.ledger.approve("mint-operator", "mint", self.ledger.proposal("mint")["hash"])

    def test_holder_cannot_mint(self):
        with self.assertRaises(LedgerError):
            self.ledger.propose_mint("alice", "mint", [Output("alice", 100)], "test")

    def test_wrong_approval_hash_rejected(self):
        self.ledger.propose_mint("mint-operator", "mint", [Output("alice", 100)], "test")
        with self.assertRaises(LedgerError):
            self.ledger.approve("mint-approver", "mint", "0" * 64)
        self.assertEqual(self.ledger.supply(), 0)

    def test_mint_and_approval_replay_do_not_inflate(self):
        first = self.mint()
        second = self.mint()
        self.assertEqual(first, second)
        self.assertEqual(self.ledger.supply(), 10_000)

    def test_transfer_replay_is_idempotent(self):
        minted = self.mint()
        first = self.ledger.transfer("alice", "pay", minted["outputs"], [Output("bob", 10_000)])
        second = self.ledger.transfer("alice", "pay", minted["outputs"], [Output("bob", 10_000)])
        self.assertEqual(first, second)
        self.assertEqual(self.ledger.balance("bob"), 10_000)

    def test_changed_replay_rejected(self):
        self.mint()
        with self.assertRaises(LedgerError):
            self.mint(amount=20_000)

    def test_no_supply_creation_or_destruction_in_transfer(self):
        minted = self.mint()
        for amount in (9_995, 10_005):
            with self.assertRaises(LedgerError):
                self.ledger.transfer("alice", "bad", minted["outputs"], [Output("bob", amount)])
        self.assertEqual(self.ledger.balance("alice"), 10_000)
        self.assertEqual(self.ledger.verify()["audit_events"], 3)

    def test_duplicate_input_rejected(self):
        minted = self.mint()
        with self.assertRaises(LedgerError):
            self.ledger.transfer("alice", "duplicate", minted["outputs"] * 2, [Output("bob", 20_000)])

    def test_double_spend_rejected(self):
        minted = self.mint()
        self.ledger.transfer("alice", "first", minted["outputs"], [Output("bob", 10_000)])
        with self.assertRaises(LedgerError):
            self.ledger.transfer("alice", "second", minted["outputs"], [Output("alice", 10_000)])

    def test_wrong_owner_rejected(self):
        minted = self.mint()
        with self.assertRaises(LedgerError):
            self.ledger.transfer("bob", "theft", minted["outputs"], [Output("bob", 10_000)])

    def test_inactive_frozen_unknown_and_privileged_owners_rejected(self):
        for owner in ("frozen", "inactive", "missing", "mint-operator", "mint-approver"):
            with self.subTest(owner=owner), self.assertRaises(LedgerError):
                self.mint(to=owner)

    def test_malformed_amounts_rejected(self):
        for amount in (True, False, 0, -5, 1, 1.0, "5", 2**63, None):
            with self.subTest(amount=amount), self.assertRaises(LedgerError):
                self.mint(amount=amount)

    def test_holding_limit_enforced_after_consuming_own_notes(self):
        minted = self.mint(amount=50, to="limited")
        self.ledger.transfer("limited", "reshape", minted["outputs"], [Output("limited", 25), Output("limited", 25)])
        with self.assertRaises(LedgerError):
            self.mint(amount=5, to="limited", key="too-much")
        self.assertEqual(self.ledger.balance("limited"), 50)

    def test_limit_checked_at_approval(self):
        self.ledger.propose_mint("mint-operator", "p1", [Output("limited", 50)], "test")
        self.mint(amount=50, to="limited", key="p2")
        with self.assertRaises(LedgerError):
            self.ledger.approve("mint-approver", "p1", self.ledger.proposal("p1")["hash"])
        self.assertEqual(self.ledger.proposal("p1")["state"], "proposed")

    def test_retirement_requires_treasury_custody_and_dual_control(self):
        minted = self.mint()
        with self.assertRaises(LedgerError):
            self.ledger.propose_retire("mint-operator", "burn", minted["outputs"], "test")
        redeemed = self.ledger.transfer("alice", "redeem", minted["outputs"], [Output("treasury", 10_000)])
        self.ledger.propose_retire("mint-operator", "burn", redeemed["outputs"], "test")
        self.assertEqual(self.ledger.supply(), 10_000)
        self.ledger.approve("mint-approver", "burn", self.ledger.proposal("burn")["hash"])
        result = self.ledger.verify()
        self.assertEqual(result["supply"], 0)
        self.assertEqual(result["journal_debits"], 20_000)
        self.assertEqual(result["journal_credits"], 20_000)

    def test_retirement_revalidates_spent_inputs(self):
        minted = self.mint(to="treasury")
        self.ledger.propose_retire("mint-operator", "burn", minted["outputs"], "test")
        self.ledger.transfer("treasury", "spend", minted["outputs"], [Output("bob", 10_000)])
        with self.assertRaises(LedgerError):
            self.ledger.approve("mint-approver", "burn", self.ledger.proposal("burn")["hash"])

    def test_fanout_over_bound_is_rejected_atomically(self):
        minted = self.mint(amount=10_005)
        with self.assertRaises(LedgerError):
            self.ledger.transfer("alice", "too-many", minted["outputs"], [Output("alice", 5)] * 2_001)
        self.assertEqual(self.ledger.balance("alice"), 10_005)

    def test_empty_inputs_and_outputs_rejected(self):
        minted = self.mint()
        for ins, outs in (([], [Output("alice", 5)]), (minted["outputs"], [])):
            with self.assertRaises(LedgerError):
                self.ledger.transfer("alice", "bad", ins, outs)

    def test_supply_cap(self):
        other = Ledger(Path(self.tmp.name) / "small.db", Currency(supply_cap=10), self.registry)
        try:
            other.propose_mint("mint-operator", "mint", [Output("alice", 15)], "test")
            with self.assertRaises(LedgerError):
                other.approve("mint-approver", "mint", other.proposal("mint")["hash"])
            self.assertEqual(other.supply(), 0)
        finally:
            other.close()

    def test_mainnet_and_currency_change_fail_closed(self):
        with self.assertRaises(LedgerError):
            Ledger(Path(self.tmp.name) / "main.db", Currency(network="mainnet"), self.registry)
        with self.assertRaises(LedgerError):
            Ledger(self.path, Currency(code="TEUR"), self.registry)

    def test_policy_registry_change_fails_closed(self):
        with self.assertRaises(LedgerError):
            Ledger(self.path, self.currency, actors())

    def test_process_restart_preserves_state_and_replay(self):
        minted = self.mint()
        self.ledger.close()
        self.ledger = Ledger(self.path, self.currency, self.registry)
        self.assertEqual(self.mint(), minted)
        self.assertEqual(self.ledger.verify()["supply"], 10_000)

    def test_consistent_backup_restore(self):
        self.mint()
        destination = Path(self.tmp.name) / "backup.db"
        self.ledger.backup(destination)
        restored = Ledger(destination, self.currency, self.registry)
        try:
            self.assertEqual(self.ledger.verify(), restored.verify())
        finally:
            restored.close()
        with self.assertRaises(FileExistsError):
            self.ledger.backup(destination)

    def test_audit_corruption_detected(self):
        self.mint()
        self.ledger.db.execute("UPDATE audit SET previous_hash='bad' WHERE seq=2")
        with self.assertRaises(LedgerError):
            self.ledger.verify()

    def test_balanced_note_tampering_detected(self):
        self.mint()
        self.ledger.db.execute("UPDATE notes SET owner='bob' WHERE id='mint:0'")
        with self.assertRaises(LedgerError):
            self.ledger.verify()

    def test_journal_tampering_detected(self):
        self.mint()
        self.ledger.db.execute("UPDATE journal SET account='wrong' WHERE account='asset:test_issuance_suspense'")
        with self.assertRaises(LedgerError):
            self.ledger.verify()

    def test_operation_tampering_detected(self):
        self.mint()
        self.ledger.db.execute("UPDATE operations SET digest='bad'")
        with self.assertRaises(LedgerError):
            self.ledger.verify()

    def test_concurrent_double_spend_has_one_winner(self):
        minted = self.mint()
        barrier = threading.Barrier(2)
        outcomes = []
        def spend(index):
            ledger = Ledger(self.path, self.currency, self.registry)
            try:
                barrier.wait()
                ledger.transfer("alice", f"concurrent-{index}", minted["outputs"], [Output("bob", 10_000)])
                outcomes.append("success")
            except LedgerError:
                outcomes.append("rejected")
            finally:
                ledger.close()
        threads = [threading.Thread(target=spend, args=(i,)) for i in range(2)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=15)
        self.assertCountEqual(outcomes, ["success", "rejected"])
        self.assertEqual(self.ledger.verify()["supply"], 10_000)

    def test_seeded_random_partition_conservation(self):
        rng = random.Random(20261007)
        notes = self.mint()["outputs"]
        for step in range(100):
            boundaries = sorted(rng.sample(range(1, 2000), rng.randint(1, 30)))
            points = [0] + boundaries + [2000]
            amounts = [(b-a)*5 for a, b in zip(points, points[1:])]
            notes = self.ledger.transfer("alice", f"partition-{step}", notes, [Output("alice", a) for a in amounts])["outputs"]
            self.assertEqual(self.ledger.supply(), 10_000)
        self.ledger.verify()

    def test_reason_and_request_id_validation(self):
        for key, reason in (("bad id", "test"), ("a"*65, "test"), ("valid", "  "), ("valid", "x"*501)):
            with self.assertRaises(LedgerError):
                self.ledger.propose_mint("mint-operator", key, [Output("alice", 5)], reason)

    def test_demo(self):
        result = demonstration(Path(self.tmp.name) / "demo.db")
        self.assertEqual(result["remaining_minor_units"], 6_665)
        self.assertFalse(result["bsv_anchor_request"]["broadcast_enabled"])


if __name__ == "__main__":
    unittest.main()
