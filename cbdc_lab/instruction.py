"""Offline instruction preimage candidate; NOT a signature or token protocol.

Explicit domain, issuer, instrument, nonce and expiry are covered by exact bytes.
This module neither creates keys nor signs/broadcasts; runtime authorization,
nonce persistence and actual script/overlay enforcement remain unimplemented.
"""
import hashlib
from .ledger import LedgerError, canonical, identifier, integer

DOMAIN = 'CBDC-LAB:OFFLINE-INSTRUCTION:V1'
FIELDS = {'schema', 'network', 'issuer', 'instrument', 'operation', 'nonce',
          'expires_at', 'inputs', 'outputs', 'amount'}

def preimage(request: dict, *, expected_issuer: str, expected_instrument: str,
             now: int) -> bytes:
    if type(request) is not dict or set(request) != FIELDS:
        raise LedgerError('exact instruction fields required')
    if type(request['schema']) is not int or request['schema'] != 1:
        raise LedgerError('unsupported schema')
    if request['network'] != 'bsv-testnet':
        raise LedgerError('testnet domain required')
    for key in ('issuer', 'instrument', 'nonce'):
        identifier(request[key], key)
    if request['issuer'] != expected_issuer or request['instrument'] != expected_instrument:
        raise LedgerError('wrong issuer or instrument domain')
    integer(now, 'now', minimum=0)
    integer(request['expires_at'], 'expires_at', minimum=0)
    if request['expires_at'] <= now:
        raise LedgerError('expired instruction')
    op = request['operation']
    if op not in ('mint', 'transfer', 'retire'):
        raise LedgerError('unknown operation')
    ins, outs = request['inputs'], request['outputs']
    if type(ins) is not list or len(ins) > 2000 or type(outs) is not list or len(outs) > 2000:
        raise LedgerError('bounded lists required')
    for item in ins:
        identifier(item, 'input')
    if len(set(ins)) != len(ins):
        raise LedgerError('duplicate input')
    for out in outs:
        if type(out) is not dict or set(out) != {'owner', 'amount'}:
            raise LedgerError('exact output fields required')
        identifier(out['owner'], 'owner')
        integer(out['amount'], 'output amount')
    integer(request['amount'], 'amount')
    if op == 'mint' and (ins or not outs):
        raise LedgerError('mint requires no inputs and nonempty outputs')
    if op == 'transfer' and (not ins or not outs):
        raise LedgerError('transfer requires inputs and outputs')
    if op == 'retire' and (not ins or outs):
        raise LedgerError('retire requires inputs and no outputs')
    if outs and sum(o['amount'] for o in outs) != request['amount']:
        raise LedgerError('declared amount differs from output total')
    return (DOMAIN + '\n' + canonical(request)).encode('ascii')

def instruction_hash(request: dict, **context) -> str:
    return hashlib.sha256(preimage(request, **context)).hexdigest()
