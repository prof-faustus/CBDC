"""Offline negative corpus only. No claim of real signature/UTXO validation."""
import copy
import unittest
from cbdc_lab.ledger import LedgerError
from cbdc_lab.instruction import preimage, instruction_hash, DOMAIN

class InstructionTests(unittest.TestCase):
    def setUp(self):
        self.r = dict(schema=1, network='bsv-testnet', issuer='test-issuer',
            instrument='TUSD', operation='mint', nonce='request-1', expires_at=200,
            inputs=[], outputs=[dict(owner='alice',amount=10000)], amount=10000)
        self.ctx = dict(expected_issuer='test-issuer',expected_instrument='TUSD',now=100)
    def reject(self, **changes):
        r=copy.deepcopy(self.r); r.update(changes)
        with self.assertRaises(LedgerError):preimage(r,**self.ctx)
    def test_order_independent_exact_bytes(self):
        self.assertEqual(preimage(self.r,**self.ctx),preimage(dict(reversed(list(self.r.items()))),**self.ctx))
        self.assertTrue(preimage(self.r,**self.ctx).startswith((DOMAIN+'\n').encode()))
    def test_cross_network_rejected(self): self.reject(network='bsv-mainnet')
    def test_cross_issuer_rejected(self): self.reject(issuer='other-issuer')
    def test_cross_instrument_rejected(self): self.reject(instrument='TEUR')
    def test_expiry_boundary(self):
        self.reject(expires_at=100); self.reject(expires_at=99)
    def test_unknown_field_and_schema(self):
        self.reject(extra='unsigned'); self.reject(schema=True); self.reject(schema=2)
    def test_amount_types(self):
        for a in [True,10000.0,'10000',0,-1,2**63]: self.reject(amount=a)
    def test_mint_cannot_consume(self): self.reject(inputs=['note-1'])
    def test_transfer_requires_inputs(self): self.reject(operation='transfer')
    def test_retire_cannot_create_outputs(self): self.reject(operation='retire',inputs=['note-1'])
    def test_repeated_input_rejected(self): self.reject(operation='transfer',inputs=['note-1','note-1'])
    def test_output_value_tamper(self): self.reject(outputs=[dict(owner='alice',amount=10005)])
    def test_nonce_and_recipient_covered_by_hash(self):
        old=instruction_hash(self.r,**self.ctx)
        for changes in [dict(nonce='request-2'),dict(outputs=[dict(owner='bob',amount=10000)])]:
            r=copy.deepcopy(self.r);r.update(changes)
            self.assertNotEqual(old,instruction_hash(r,**self.ctx))
    def test_valid_transfer_and_retire_shapes(self):
        for changes in [dict(operation='transfer',inputs=['note-1']),dict(operation='retire',inputs=['note-1'],outputs=[])]:
            r=copy.deepcopy(self.r);r.update(changes);preimage(r,**self.ctx)
    def test_size_and_extra_output_fields(self):
        self.reject(inputs=['n']*2001)
        self.reject(outputs=[dict(owner='alice',amount=10000,hidden=True)])
