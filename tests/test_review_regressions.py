"""Independent review regressions for the local, trusted-call test harness.

Fault injection and direct database corruption below are deliberately outside
normal application calls. They test rollback and consistency checks, not access
control or resistance to an attacker who controls the whole process/database.
"""

from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from cbdc_lab import Actor, Currency, Ledger, LedgerError, Output
from cbdc_lab.demo import actors
from cbdc_lab.ledger import MAX_INTEGER, canonical


class ReviewRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "review.db"
        self.currency = Currency()
        self.registry = actors()
        self.ledger = Ledger(self.path, self.currency, self.registry)

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def mint(self, key="mint", amount=100, owner="alice"):
        self.ledger.propose_mint("mint-operator", key, [Output(owner, amount)], "test")
        return self.ledger.approve("mint-approver", key, self.ledger.proposal(key)["hash"])

    def snapshot(self):
        return {
            table: [tuple(row) for row in self.ledger.db.execute(f"SELECT * FROM {table} ORDER BY 1")]
            for table in ("config", "operations", "notes", "journal", "audit")
        }

    def concurrent(self, action):
        barrier = threading.Barrier(2)
        outcomes = []

        def run(index):
            ledger = None
            try:
                ledger = Ledger(self.path, self.currency, self.registry)
                barrier.wait(timeout=5)
                outcomes.append(("ok", action(ledger, index)))
            except LedgerError as error:
                outcomes.append(("rejected", str(error)))
            except BaseException as error:
                outcomes.append(("unexpected", repr(error)))
            finally:
                if ledger is not None:
                    ledger.close()

        threads = [threading.Thread(target=run, args=(index,), daemon=True) for index in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=15)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(len(outcomes), 2)
        self.assertNotIn("unexpected", [item[0] for item in outcomes], outcomes)
        return outcomes

    def test_gross_journal_totals_can_exceed_signed_integer_limit(self):
        registry = [Actor(actor.id, actor.role, holding_limit=MAX_INTEGER) for actor in actors()]
        ledger = Ledger(Path(self.tmp.name) / "large.db",
                        Currency(minimum_unit=1, supply_cap=MAX_INTEGER,
                                 max_operation_amount=MAX_INTEGER), registry)
        try:
            for index in range(2):
                mint_key, retire_key = f"mint-{index}", f"retire-{index}"
                ledger.propose_mint("mint-operator", mint_key,
                                    [Output("treasury", MAX_INTEGER)], "boundary")
                issued = ledger.approve("mint-approver", mint_key, ledger.proposal(mint_key)["hash"])
                ledger.propose_retire("mint-operator", retire_key, issued["outputs"], "boundary")
                ledger.approve("mint-approver", retire_key, ledger.proposal(retire_key)["hash"])
            report = ledger.verify()
            self.assertEqual(report["supply"], 0)
            self.assertEqual(report["liability"], 0)
            self.assertEqual(report["journal_debits"], 4 * MAX_INTEGER)
            self.assertEqual(report["journal_credits"], 4 * MAX_INTEGER)
        finally:
            ledger.close()

    def test_corrupted_proposal_body_cannot_apply_under_old_hash(self):
        self.ledger.propose_mint("mint-operator", "mint", [Output("alice", 100)], "test")
        approved_hash = self.ledger.proposal("mint")["hash"]
        changed_body = self.ledger.proposal("mint")["request"]
        changed_body["outputs"][0]["amount"] = 200
        self.ledger.db.execute("UPDATE operations SET body=? WHERE id='mint'", (canonical(changed_body),))
        before = self.snapshot()
        with self.assertRaises(LedgerError):
            self.ledger.approve("mint-approver", "mint", approved_hash)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.ledger.supply(), 0)

    def test_transfer_audit_failure_rolls_back_all_changes(self):
        minted = self.mint()
        before = self.snapshot()
        with patch.object(self.ledger, "_audit", side_effect=RuntimeError("injected failure")):
            with self.assertRaises(RuntimeError):
                self.ledger.transfer("alice", "pay", minted["outputs"], [Output("bob", 100)])
        self.assertEqual(self.snapshot(), before)
        self.ledger.transfer("alice", "pay", minted["outputs"], [Output("bob", 100)])
        self.assertEqual(self.ledger.verify()["supply"], 100)
        self.assertEqual(self.ledger.balance("bob"), 100)

    def test_retirement_audit_failure_rolls_back_spend_and_journal(self):
        minted = self.mint(owner="treasury")
        self.ledger.propose_retire("mint-operator", "retire", minted["outputs"], "test")
        request_hash = self.ledger.proposal("retire")["hash"]
        before = self.snapshot()
        original_audit = self.ledger._audit

        def fail_after_audit_write(event):
            original_audit(event)
            raise RuntimeError("injected failure after audit insert")

        with patch.object(self.ledger, "_audit", side_effect=fail_after_audit_write):
            with self.assertRaises(RuntimeError):
                self.ledger.approve("mint-approver", "retire", request_hash)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.ledger.proposal("retire")["state"], "proposed")
        self.ledger.approve("mint-approver", "retire", request_hash)
        self.assertEqual(self.ledger.verify()["supply"], 0)

    def test_mint_audit_failure_rolls_back_outputs_and_journal(self):
        self.ledger.propose_mint("mint-operator", "mint", [Output("alice", 100)], "test")
        request_hash = self.ledger.proposal("mint")["hash"]
        before = self.snapshot()
        with patch.object(self.ledger, "_audit", side_effect=RuntimeError("injected failure")):
            with self.assertRaises(RuntimeError):
                self.ledger.approve("mint-approver", "mint", request_hash)
        self.assertEqual(self.snapshot(), before)
        self.ledger.approve("mint-approver", "mint", request_hash)
        self.assertEqual(self.ledger.verify()["supply"], 100)

    def test_verify_uses_one_snapshot_during_concurrent_write(self):
        self.mint()
        before = self.ledger.verify()
        reading = threading.Event()
        resume = threading.Event()
        outcomes = []

        def verify():
            ledger = None
            try:
                ledger = Ledger(self.path, self.currency, self.registry)
                original_projection = ledger._verify_projection

                def paused_projection():
                    reading.set()
                    if not resume.wait(timeout=5):
                        raise RuntimeError("snapshot test writer did not finish")
                    original_projection()

                with patch.object(ledger, "_verify_projection", side_effect=paused_projection):
                    outcomes.append(ledger.verify())
            except BaseException as error:
                outcomes.append(error)
            finally:
                if ledger is not None:
                    ledger.close()

        thread = threading.Thread(target=verify, daemon=True)
        thread.start()
        try:
            self.assertTrue(reading.wait(timeout=5))
            self.mint(key="concurrent-mint")
        finally:
            resume.set()
            thread.join(timeout=15)
        self.assertFalse(thread.is_alive())
        self.assertEqual(outcomes, [before])
        self.assertEqual(self.ledger.verify()["supply"], 200)

    def test_concurrent_approval_is_idempotent(self):
        self.ledger.propose_mint("mint-operator", "mint", [Output("alice", 100)], "test")
        request_hash = self.ledger.proposal("mint")["hash"]
        outcomes = self.concurrent(lambda ledger, _: ledger.approve("mint-approver", "mint", request_hash))
        self.assertEqual([item[0] for item in outcomes], ["ok", "ok"])
        self.assertEqual(outcomes[0][1], outcomes[1][1])
        self.assertEqual(self.ledger.verify()["supply"], 100)
        self.assertEqual(self.ledger.db.execute("SELECT COUNT(*) FROM journal").fetchone()[0], 2)

    def test_concurrent_transfer_replay_is_idempotent(self):
        minted = self.mint()
        outcomes = self.concurrent(lambda ledger, _: ledger.transfer(
            "alice", "pay", minted["outputs"], [Output("bob", 100)]))
        self.assertEqual([item[0] for item in outcomes], ["ok", "ok"])
        self.assertEqual(outcomes[0][1], outcomes[1][1])
        self.assertEqual(self.ledger.verify()["supply"], 100)
        self.assertEqual(self.ledger.balance("bob"), 100)

    def test_concurrent_approvals_cannot_exceed_supply_cap(self):
        self.ledger.close()
        self.currency = Currency(supply_cap=100)
        self.path = Path(self.tmp.name) / "limited-supply.db"
        self.ledger = Ledger(self.path, self.currency, self.registry)
        hashes = []
        for index in range(2):
            key = f"mint-{index}"
            self.ledger.propose_mint("mint-operator", key, [Output("alice", 100)], "test")
            hashes.append(self.ledger.proposal(key)["hash"])
        outcomes = self.concurrent(lambda ledger, index: ledger.approve(
            "mint-approver", f"mint-{index}", hashes[index]))
        self.assertCountEqual([item[0] for item in outcomes], ["ok", "rejected"])
        self.assertEqual(self.ledger.verify()["supply"], 100)

    def test_sql_like_reason_stays_literal_and_invalid_ids_have_no_effect(self):
        reason = "'); DROP TABLE notes; --"
        self.ledger.propose_mint("mint-operator", "safe", [Output("alice", 100)], reason)
        self.assertEqual(self.ledger.proposal("safe")["request"]["reason"], reason)
        before = self.snapshot()
        for key in ("bad';--", "bad\x00id", "../bad", "bad\n", 1, None):
            with self.subTest(key=key), self.assertRaises(LedgerError):
                self.ledger.propose_mint("mint-operator", key, [Output("alice", 100)], "test")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.ledger.verify()["supply"], 0)

    def test_generator_inputs_and_outputs_fail_closed(self):
        minted = self.mint()
        before = self.snapshot()
        with self.assertRaises(LedgerError):
            self.ledger.transfer("alice", "bad-inputs", iter(minted["outputs"]), [Output("bob", 100)])
        with self.assertRaises(LedgerError):
            self.ledger.transfer("alice", "bad-outputs", minted["outputs"], iter([Output("bob", 100)]))
        self.assertEqual(self.snapshot(), before)

    def test_retirement_replay_changes_no_state(self):
        minted = self.mint(owner="treasury")
        first = self.ledger.propose_retire("mint-operator", "retire", minted["outputs"], "test")
        self.assertEqual(first["state"], "proposed")
        result = self.ledger.approve("mint-approver", "retire", self.ledger.proposal("retire")["hash"])
        before = self.snapshot()
        self.assertEqual(self.ledger.propose_retire("mint-operator", "retire", minted["outputs"], "test"), result)
        self.assertEqual(self.ledger.approve("mint-approver", "retire", self.ledger.proposal("retire")["hash"]), result)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.ledger.verify()["supply"], 0)


if __name__ == "__main__":
    unittest.main()
