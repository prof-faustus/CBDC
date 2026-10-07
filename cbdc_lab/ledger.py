"""Local reference ledger. Caller identity is trusted; this is not an auth server.

All money is integer minor units. Database transactions serialize spending and
treasury approval. No method signs, broadcasts or settles a blockchain transaction.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


MAX_INTEGER = 2**63 - 1


class LedgerError(ValueError):
    """A rejected request has no economic effect."""


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def integer(value: int, name: str, *, minimum: int = 1) -> int:
    if type(value) is not int or not minimum <= value <= MAX_INTEGER:
        raise LedgerError(f"{name} must be an integer in [{minimum}, {MAX_INTEGER}]")
    return value


def identifier(value: str, name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", value):
        raise LedgerError(f"invalid {name}")
    return value


@dataclass(frozen=True)
class Currency:
    code: str = "TUSD"
    decimals: int = 2
    minimum_unit: int = 5
    supply_cap: int = 100_000_000
    max_inputs: int = 2_000
    max_outputs: int = 2_000
    max_operation_amount: int = 10_000_000
    network: str = "simulation"

    def validate(self) -> None:
        if not re.fullmatch(r"T[A-Z]{2,7}", self.code):
            raise LedgerError("synthetic currency code must start with T")
        integer(self.decimals, "decimals", minimum=0)
        if self.decimals > 8:
            raise LedgerError("at most eight decimal places")
        for name in ("minimum_unit", "supply_cap", "max_inputs", "max_outputs", "max_operation_amount"):
            integer(getattr(self, name), name)
        if self.max_inputs > 10_000 or self.max_outputs > 10_000:
            raise LedgerError("fan-in and fan-out must not exceed 10,000")
        if self.minimum_unit > self.max_operation_amount:
            raise LedgerError("minimum unit exceeds operation limit")
        if self.network != "simulation":
            raise LedgerError("reference ledger supports simulation only")


@dataclass(frozen=True)
class Actor:
    id: str
    role: str = "holder"
    active: bool = True
    frozen: bool = False
    holding_limit: int = 100_000_000

    def validate(self) -> None:
        identifier(self.id, "actor ID")
        if self.role not in {"holder", "treasury", "issuer", "approver"}:
            raise LedgerError("unknown role")
        if type(self.active) is not bool or type(self.frozen) is not bool:
            raise LedgerError("active/frozen must be booleans")
        integer(self.holding_limit, "holding_limit", minimum=0)


@dataclass(frozen=True)
class Output:
    owner: str
    amount: int


SCHEMA = """
CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY CHECK (id=1), body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS operations (
 id TEXT PRIMARY KEY, digest TEXT NOT NULL, body TEXT NOT NULL,
 state TEXT NOT NULL CHECK (state IN ('proposed','applied')), result TEXT);
CREATE TABLE IF NOT EXISTS notes (
 id TEXT PRIMARY KEY, owner TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>0),
 created_by TEXT NOT NULL REFERENCES operations(id), spent_by TEXT REFERENCES operations(id));
CREATE TABLE IF NOT EXISTS journal (
 id INTEGER PRIMARY KEY, operation_id TEXT NOT NULL REFERENCES operations(id),
 account TEXT NOT NULL, debit INTEGER NOT NULL CHECK(debit>=0),
 credit INTEGER NOT NULL CHECK(credit>=0), CHECK((debit=0) != (credit=0)));
CREATE TABLE IF NOT EXISTS audit (
 seq INTEGER PRIMARY KEY, body TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS unspent_owner ON notes(owner, spent_by);
"""


class Ledger:
    """One currency and immutable synthetic identity/policy registry per database.

    Identities passed as actor IDs are authenticated *by the calling test harness*.
    Do not expose this class directly over a network or accept actor IDs as proof.
    """

    def __init__(self, path: str | Path, currency: Currency, actors: Iterable[Actor]):
        currency.validate()
        actors = list(actors)
        if not actors:
            raise LedgerError("an identity registry is required")
        for actor in actors:
            actor.validate()
        if len({a.id for a in actors}) != len(actors):
            raise LedgerError("duplicate actor")
        self.currency = currency
        self.actors = {a.id: a for a in actors}
        self.db = sqlite3.connect(str(path), timeout=10, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript(SCHEMA)
        config = canonical({"schema": 1, "currency": asdict(currency),
                            "actors": [asdict(a) for a in sorted(actors, key=lambda a: a.id)]})
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT body FROM config WHERE id=1").fetchone()
            if row and row["body"] != config:
                raise LedgerError("configuration mismatch; migrations require a separate reviewed design")
            if not row:
                self.db.execute("INSERT INTO config VALUES (1,?)", (config,))
                self._audit({"event": "GENESIS", "configuration_hash": hashlib.sha256(config.encode()).hexdigest()})
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            self.db.close()
            raise

    def close(self) -> None:
        self.db.close()

    def _actor(self, actor_id: str, role: str | None = None) -> Actor:
        identifier(actor_id, "actor ID")
        actor = self.actors.get(actor_id)
        if actor is None or not actor.active or actor.frozen:
            raise LedgerError("actor is unknown, inactive or frozen")
        if role is not None and actor.role != role:
            raise LedgerError(f"{role} role required")
        return actor

    def _audit(self, event: dict) -> None:
        last = self.db.execute("SELECT seq,event_hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        seq, previous = (last["seq"] + 1, last["event_hash"]) if last else (1, "0" * 64)
        body = {"seq": seq, "at": datetime.now(timezone.utc).isoformat(), **event}
        value = digest({"previous_hash": previous, "body": body})
        self.db.execute("INSERT INTO audit VALUES (?,?,?,?)", (seq, canonical(body), previous, value))

    def _outputs(self, values: Iterable[Output]) -> list[dict]:
        # API accepts materialized bounded sequences, not arbitrary generators.
        if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= self.currency.max_outputs:
            raise LedgerError("output count outside configured bound")
        result = []
        for item in values:
            if not isinstance(item, Output):
                raise LedgerError("outputs must be Output instances")
            owner = self._actor(item.owner)
            if owner.role not in {"holder", "treasury"}:
                raise LedgerError("only holders and treasury may own notes")
            integer(item.amount, "amount")
            if item.amount % self.currency.minimum_unit:
                raise LedgerError("amount violates minimum denomination")
            result.append(asdict(item))
        total = sum(o["amount"] for o in result)
        if total > self.currency.max_operation_amount:
            raise LedgerError("operation amount exceeds configured limit")
        return result

    def _inputs(self, values: list[str] | tuple[str, ...]) -> list[str]:
        if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= self.currency.max_inputs:
            raise LedgerError("input count outside configured bound")
        values = list(values)
        for value in values:
            identifier(value, "input ID")
        if len(values) != len(set(values)):
            raise LedgerError("duplicate input")
        return values

    def _amount_in(self, ids: list[str], owner: str | None = None, *, treasury: bool = False) -> int:
        total = 0
        for note_id in ids:
            row = self.db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
            if not row or row["spent_by"] is not None:
                raise LedgerError("input missing or already spent")
            principal = self._actor(row["owner"])
            if owner is not None and row["owner"] != owner:
                raise LedgerError("input not owned by caller")
            if treasury and principal.role != "treasury":
                raise LedgerError("retirement requires prior owner-authorized transfer to treasury")
            total += row["amount"]
        if total > self.currency.max_operation_amount:
            raise LedgerError("operation amount exceeds configured limit")
        return total

    def _existing(self, request_id: str, body: dict) -> dict | None:
        identifier(request_id, "request ID")
        if len(request_id) > 64:
            raise LedgerError("request ID must be at most 64 characters")
        row = self.db.execute("SELECT * FROM operations WHERE id=?", (request_id,)).fetchone()
        if row:
            if row["digest"] != digest(body):
                raise LedgerError("idempotency key reused for different request")
            return json.loads(row["result"]) if row["result"] else {"id": request_id, "state": "proposed"}
        return None

    def _limits(self, outputs: list[dict], inputs: list[str]) -> None:
        owners = {o["owner"] for o in outputs}
        for owner in owners:
            self._actor(owner)
            existing = self.balance(owner)
            consumed = sum(self.db.execute("SELECT amount FROM notes WHERE id=? AND owner=?", (n, owner)).fetchone()[0]
                           for n in inputs if self.db.execute("SELECT 1 FROM notes WHERE id=? AND owner=?", (n, owner)).fetchone())
            credited = sum(o["amount"] for o in outputs if o["owner"] == owner)
            if existing - consumed + credited > self.actors[owner].holding_limit:
                raise LedgerError("recipient holding limit exceeded")

    def propose_mint(self, actor: str, request_id: str, outputs: list[Output], reason: str) -> dict:
        self._actor(actor, "issuer")
        body = {"type": "MINT", "actor": actor, "outputs": self._outputs(outputs), "inputs": [], "reason": self._reason(reason)}
        return self._propose(request_id, body)

    def propose_retire(self, actor: str, request_id: str, inputs: list[str], reason: str) -> dict:
        self._actor(actor, "issuer")
        body = {"type": "RETIRE", "actor": actor, "outputs": [], "inputs": self._inputs(inputs), "reason": self._reason(reason)}
        return self._propose(request_id, body)

    @staticmethod
    def _reason(reason: str) -> str:
        if not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 500:
            raise LedgerError("a nonempty reason of at most 500 characters is required")
        return reason.strip()

    def _propose(self, request_id: str, body: dict) -> dict:
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self._existing(request_id, body)
            if existing is not None:
                self.db.execute("COMMIT")
                return existing
            if body["type"] == "RETIRE":
                self._amount_in(body["inputs"], treasury=True)
            self.db.execute("INSERT INTO operations VALUES (?,?,?,'proposed',NULL)", (request_id, digest(body), canonical(body)))
            self._audit({"event": "PROPOSED", "operation_id": request_id, "request_hash": digest(body), "actor": body["actor"]})
            self.db.execute("COMMIT")
            return {"id": request_id, "state": "proposed"}
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def approve(self, actor: str, request_id: str, expected_request_hash: str) -> dict:
        self._actor(actor, "approver")
        identifier(request_id, "request ID")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT * FROM operations WHERE id=?", (request_id,)).fetchone()
            if not row or row["digest"] != expected_request_hash:
                raise LedgerError("proposal missing or approved hash does not match")
            body = json.loads(row["body"])
            if digest(body) != expected_request_hash:
                raise LedgerError("proposal body differs from approved hash")
            self._actor(body["actor"], "issuer")
            if body["actor"] == actor or body["type"] not in {"MINT", "RETIRE"}:
                raise LedgerError("independent treasury approval required")
            if row["state"] == "applied":
                self.db.execute("COMMIT")
                return json.loads(row["result"])
            result = self._apply(request_id, body, approver=actor)
            self.db.execute("COMMIT")
            return result
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def proposal(self, request_id: str) -> dict:
        identifier(request_id, "request ID")
        row = self.db.execute("SELECT * FROM operations WHERE id=?", (request_id,)).fetchone()
        if not row:
            raise LedgerError("operation missing")
        return {"id": request_id, "hash": row["digest"], "state": row["state"], "request": json.loads(row["body"])}

    def transfer(self, actor: str, request_id: str, inputs: list[str], outputs: list[Output]) -> dict:
        self._actor(actor)
        body = {"type": "TRANSFER", "actor": actor, "inputs": self._inputs(inputs), "outputs": self._outputs(outputs)}
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self._existing(request_id, body)
            if existing is not None:
                self.db.execute("COMMIT")
                return existing
            self.db.execute("INSERT INTO operations VALUES (?,?,?,'proposed',NULL)", (request_id, digest(body), canonical(body)))
            result = self._apply(request_id, body)
            self.db.execute("COMMIT")
            return result
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _apply(self, request_id: str, body: dict, approver: str | None = None) -> dict:
        inputs, outputs, kind = body["inputs"], body["outputs"], body["type"]
        out_total = sum(o["amount"] for o in outputs)
        amount = out_total
        if kind == "MINT":
            if self.supply() + out_total > self.currency.supply_cap:
                raise LedgerError("supply cap exceeded")
        elif kind == "TRANSFER":
            if self._amount_in(inputs, body["actor"]) != out_total:
                raise LedgerError("input/output amount conservation failed")
        elif kind == "RETIRE":
            amount = self._amount_in(inputs, treasury=True)
        else:
            raise LedgerError("unsupported operation")
        self._limits(outputs, inputs)
        for note_id in inputs:
            count = self.db.execute("UPDATE notes SET spent_by=? WHERE id=? AND spent_by IS NULL", (request_id, note_id)).rowcount
            if count != 1:
                raise LedgerError("concurrent or duplicate spend")
        created = []
        for index, output in enumerate(outputs):
            note_id = f"{request_id}:{index}"
            # IDs are derived only from unique request ID and ordinal; not BSV outpoints.
            self.db.execute("INSERT INTO notes VALUES (?,?,?,?,NULL)", (note_id, output["owner"], output["amount"], request_id))
            created.append(note_id)
        if kind in {"MINT", "RETIRE"}:
            debit_account, credit_account = ("asset:test_issuance_suspense", "liability:circulating") if kind == "MINT" else ("liability:circulating", "asset:test_issuance_suspense")
            self.db.execute("INSERT INTO journal(operation_id,account,debit,credit) VALUES (?,?,?,0)", (request_id, debit_account, amount))
            self.db.execute("INSERT INTO journal(operation_id,account,debit,credit) VALUES (?,?,0,?)", (request_id, credit_account, amount))
        result = {"id": request_id, "state": "applied", "mode": "simulation", "kind": kind,
                  "amount": amount, "currency": self.currency.code, "outputs": created,
                  "supply": self.supply(), "chain_status": "not_submitted"}
        self.db.execute("UPDATE operations SET state='applied',result=? WHERE id=?", (canonical(result), request_id))
        self._audit({"event": "APPLIED", "operation_id": request_id, "request_hash": digest(body), "actor": body["actor"], "approver": approver, "result": result})
        return result

    def balance(self, actor: str) -> int:
        identifier(actor, "actor ID")
        return self.db.execute("SELECT COALESCE(SUM(amount),0) FROM notes WHERE owner=? AND spent_by IS NULL", (actor,)).fetchone()[0]

    def supply(self) -> int:
        return self.db.execute("SELECT COALESCE(SUM(amount),0) FROM notes WHERE spent_by IS NULL").fetchone()[0]

    def unspent(self, owner: str) -> list[dict]:
        identifier(owner, "actor ID")
        return [dict(r) for r in self.db.execute("SELECT id,owner,amount FROM notes WHERE owner=? AND spent_by IS NULL ORDER BY id", (owner,))]

    def verify(self) -> dict:
        """Consistent-snapshot accounting/audit checks; not an external authenticity proof."""
        self.db.execute("BEGIN")
        try:
            previous, count = "0" * 64, 0
            for row in self.db.execute("SELECT * FROM audit ORDER BY seq"):
                count += 1
                body = json.loads(row["body"])
                if row["seq"] != count or body["seq"] != count or row["previous_hash"] != previous or row["event_hash"] != digest({"previous_hash": previous, "body": body}):
                    raise LedgerError("audit hash chain mismatch")
                previous = row["event_hash"]
            if not count:
                raise LedgerError("missing genesis audit record")
            self._verify_projection()
            # Outstanding supply is bounded to SQLite's signed integer range,
            # but valid lifetime turnover can exceed it. Accumulate in Python's
            # exact integers rather than SQLite SUM (overflow) or TOTAL (float).
            debits, credits, liability = 0, 0, 0
            for entry in self.db.execute("SELECT account,debit,credit FROM journal"):
                debits += entry["debit"]
                credits += entry["credit"]
                if entry["account"] == "liability:circulating":
                    liability += entry["credit"] - entry["debit"]
            totals = (debits, credits)
            if totals[0] != totals[1]:
                raise LedgerError("unbalanced general ledger")
            if liability != self.supply():
                raise LedgerError("liability and unspent-note supply differ")
            malformed = self.db.execute("SELECT COUNT(*) FROM notes WHERE amount % ? != 0", (self.currency.minimum_unit,)).fetchone()[0]
            if malformed or self.supply() > self.currency.supply_cap:
                raise LedgerError("currency invariant violation")
            if self.db.execute("PRAGMA foreign_key_check").fetchall():
                raise LedgerError("foreign key violation")
            result = {"ok": True, "mode": "simulation", "supply": self.supply(), "liability": liability,
                      "journal_debits": totals[0], "journal_credits": totals[1], "audit_events": count, "audit_head": previous}
            self.db.execute("COMMIT")
            return result
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _verify_projection(self) -> None:
        """Reconcile stored economic state against retained applied audit events."""
        expected_notes: dict[str, dict] = {}
        expected_journal = []
        applied_ids = set()
        config = self.db.execute("SELECT body FROM config WHERE id=1").fetchone()[0]
        genesis = json.loads(self.db.execute("SELECT body FROM audit WHERE seq=1").fetchone()[0])
        if genesis.get("configuration_hash") != hashlib.sha256(config.encode()).hexdigest():
            raise LedgerError("genesis configuration mismatch")
        for event_row in self.db.execute("SELECT body FROM audit ORDER BY seq"):
            event = json.loads(event_row[0])
            if event.get("event") not in {"PROPOSED", "APPLIED"}:
                continue
            op = self.db.execute("SELECT * FROM operations WHERE id=?", (event["operation_id"],)).fetchone()
            if not op or op["digest"] != digest(json.loads(op["body"])) or op["digest"] != event["request_hash"]:
                raise LedgerError("operation/audit digest mismatch")
            if event["event"] != "APPLIED":
                continue
            op_id, body = op["id"], json.loads(op["body"])
            if op_id in applied_ids or op["state"] != "applied" or json.loads(op["result"]) != event["result"]:
                raise LedgerError("operation applied-state mismatch")
            applied_ids.add(op_id)
            incoming = 0
            for note_id in body["inputs"]:
                note = expected_notes.get(note_id)
                if not note or note["spent_by"] is not None:
                    raise LedgerError("invalid input history")
                incoming += note["amount"]
                note["spent_by"] = op_id
            outgoing = sum(o["amount"] for o in body["outputs"])
            if body["type"] == "TRANSFER" and incoming != outgoing:
                raise LedgerError("historical value conservation failed")
            for index, output in enumerate(body["outputs"]):
                note_id = f"{op_id}:{index}"
                expected_notes[note_id] = {"id": note_id, "owner": output["owner"], "amount": output["amount"], "created_by": op_id, "spent_by": None}
            if body["type"] == "MINT":
                expected_journal.extend([(op_id, "asset:test_issuance_suspense", outgoing, 0), (op_id, "liability:circulating", 0, outgoing)])
            elif body["type"] == "RETIRE":
                expected_journal.extend([(op_id, "liability:circulating", incoming, 0), (op_id, "asset:test_issuance_suspense", 0, incoming)])
        actual_notes = {r["id"]: dict(r) for r in self.db.execute("SELECT * FROM notes")}
        if actual_notes != expected_notes:
            raise LedgerError("note projection differs from audit history")
        actual_journal = [tuple(r) for r in self.db.execute("SELECT operation_id,account,debit,credit FROM journal ORDER BY id")]
        if actual_journal != expected_journal:
            raise LedgerError("journal projection differs from audit history")
        recorded_applied = {r[0] for r in self.db.execute("SELECT id FROM operations WHERE state='applied'")}
        if recorded_applied != applied_ids:
            raise LedgerError("applied operation lacks audit evidence")

    def backup(self, destination: str | Path) -> None:
        """Consistent SQLite backup; refuses replacing an existing file."""
        destination = Path(destination)
        with destination.open("xb"):
            pass
        target = sqlite3.connect(str(destination))
        try:
            self.db.backup(target)
        finally:
            target.close()
