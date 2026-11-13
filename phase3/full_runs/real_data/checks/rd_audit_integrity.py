# -*- coding: utf-8 -*-
"""rd-audit (R10, 2026-11-12): integrity checks that execute nothing downloaded and unpickle nothing.

(a) Is every public energy inside the window that the figures-based map assumed for the digitized energy? If it is, a
    predicted CERTIFIED or NOT CERTIFIED status carries over to the real energy by monotonicity alone.
(b) Every archive member named in converted/*.json: SHA-256 and size of the raw bytes against the recorded ones.
(c) Second route for gate G1 (NOT the declared gate): the byte stream of every label and DMRG member is TOKENIZED with
    pickletools.genops (a parser: no object is built, no global is resolved, nothing is imported or executed) and the
    float payloads that follow each field name are compared bit for bit with the converted JSON.
usage: python -B -I rd_audit_integrity.py
"""
import hashlib
import json
import os
import pickletools
import struct
import sys
import tarfile

ROOT = 'C:/Users/Nicolas/Downloads/Proyecto_SQD_ML/P5_energy_certified_labels/work'
RUNS = ROOT + '/phase3/full_runs'
RD = RUNS + '/real_data'
MAP = RUNS + '/map/laptop_analysis'
ARCH = RD + '/source/archive/quantum-groundstate-learning-6b8866b66d62aaf3ee815cd14fa58e9bf4629d66.tar.gz'
ARCH_SHA = '13aa8e69c9bc614c72c5a415ecd889f113eabe95eec81e221174b3f14dedbb91'
OUTJ = RD + '/checks/rd_audit_integrity.json'
RES = {}


def say(*a):
    print(*a)
    sys.stdout.flush()


D = {n: json.load(open(RD + '/converted/real_n%d.json' % n)) for n in (57, 115)}
SM = json.load(open(MAP + '/summary_map.json'))

# ------------------------------------------------------------------------------------------------ (a) windows
say('== (a) public energy against the window assumed by the figures-based map (per stored coupling) ==')
A = {}
for n in (57, 115):
    rows = [r for r in SM['rows'] if r['n'] == n]
    keys = sorted({'%.1f' % r['Jz'] for r in rows}, key=float)
    inside, ratio, ood = {}, {}, {}
    for k in keys:
        thr = json.load(open(MAP + '/out/thr/thr_n%d_J%s.json' % (n, k)))
        eps = D[n]['skqd_random_flip'][k]['final_global_energy'] - thr['E0']
        inside[k] = bool(thr['eps_lo'] <= eps <= thr['eps_up'])
        ratio[k] = eps / thr['eps_dig']
        ood[k] = bool(thr.get('ood'))
    dec = [r for r in rows if r['status'] in ('CERTIFIED', 'NOT_CERTIFIED')]
    implied = [r for r in dec if inside['%.1f' % r['Jz']]]
    A[n] = dict(couplings=len(keys), inside=sum(inside.values()), outside=[k for k in keys if not inside[k]],
                ratio_min=min(ratio.values()), ratio_max=max(ratio.values()),
                ratio_train=[min(v for k, v in ratio.items() if not ood[k]), max(v for k, v in ratio.items() if not ood[k])],
                ood=[k for k in keys if ood[k]], ratio_ood={k: ratio[k] for k in keys if ood[k]},
                rows=len(rows), decisive_predicted=len(dec), decisive_implied_by_window=len(implied),
                decisive_not_implied=[[r['Jz'], r['label'], r['status']] for r in dec if not inside['%.1f' % r['Jz']]])
    say(' n=%d: %d stored couplings, public energy inside [eps_lo, eps_up] at %d (outside at %s); eps_real/eps_dig %.3f-%.3f '
        '(training couplings %.3f-%.3f); test couplings %s with ratios %s'
        % (n, len(keys), A[n]['inside'], A[n]['outside'], A[n]['ratio_min'], A[n]['ratio_max'], A[n]['ratio_train'][0],
           A[n]['ratio_train'][1], A[n]['ood'], {k: round(v, 3) for k, v in A[n]['ratio_ood'].items()}))
    say('   rows %d; predicted decisive %d; of these, status at the public energy implied by the window alone: %d; not implied: %d'
        % (len(rows), len(dec), len(implied), len(dec) - len(implied)))
RES['a_windows'] = A

# ------------------------------------------------------------------------------------------------ (b), (c) archive
say('\n== (b) archive members against the hashes recorded in converted/*.json; (c) static token comparison ==')
h = hashlib.sha256()
with open(ARCH, 'rb') as f:
    for blk in iter(lambda: f.read(1 << 20), b''):
        h.update(blk)
assert h.hexdigest() == ARCH_SHA, 'archive hash'
want = {}
for n in (57, 115):
    for name, rec in D[n]['inputs_sha256'].items():
        want[name] = (rec['sha256'], rec['bytes'], n)
entry = {}
for n in (57, 115):
    for grp in ('skqd_random_flip', 'skqd_post_select', 'dmrg'):
        for key, e in D[n][grp].items():
            entry[e['_source_member']] = (n, grp, key, e)

FLOAT_OPS = {'BINFLOAT', 'FLOAT'}
BYTES_OPS = {'BINBYTES', 'SHORT_BINBYTES', 'BINBYTES8', 'BYTEARRAY8'}
STR_OPS = {'SHORT_BINUNICODE', 'BINUNICODE', 'BINUNICODE8', 'UNICODE'}


INT_OPS = {'BININT', 'BININT1', 'BININT2', 'LONG1', 'INT', 'LONG'}
INTS = {}


def tokens(raw, fields):
    """float payloads that follow each field name in the byte stream (parser only; nothing is constructed)."""
    out = {}
    cur = None
    INTS.clear()
    for op, arg, pos in pickletools.genops(raw):
        if op.name in STR_OPS and arg in fields:
            cur = arg
            out.setdefault(cur, [])
            INTS.setdefault(cur, [])
            continue
        if cur is None:
            continue
        if op.name in INT_OPS and not isinstance(arg, bool):
            INTS[cur].append(int(arg))
        if op.name in FLOAT_OPS:
            out[cur].append(struct.pack('<d', arg))
        elif op.name in BYTES_OPS and len(arg) % 8 == 0 and len(arg) > 0:
            b = bytes(arg)
            out[cur].extend(b[i:i + 8] for i in range(0, len(b), 8))
    return out


def flat(v):
    if isinstance(v, float):
        return [v]
    if isinstance(v, list) and v and all(isinstance(x, float) for x in v):
        return v
    return None


def flat_int(v):
    if isinstance(v, list) and v and all(isinstance(x, list) and x and all(isinstance(y, int) and not isinstance(y, bool) for y in x) for x in v):
        return [y for x in v for y in x]
    return None


seen_members = 0
hash_ok = 0
tok = {}
bad = []
with tarfile.open(ARCH, 'r:gz') as tf:
    for m in tf:
        if not m.isfile():
            continue
        short = m.name.split('/', 1)[1] if '/' in m.name else m.name
        if short not in want:
            continue
        raw = tf.extractfile(m).read()
        seen_members += 1
        ok = hashlib.sha256(raw).hexdigest() == want[short][0] and len(raw) == want[short][1]
        hash_ok += ok
        if not ok:
            bad.append(('hash', short))
        if short in entry:
            n, grp, key, e = entry[short]
            fields = {k for k in e if not k.startswith('_')}
            try:
                T = tokens(raw, fields)
            except Exception as ex:                                  # report, do not hide
                bad.append(('tokenize', short, repr(ex)[:120]))
                continue
            for fld in sorted(fields):
                ri = flat_int(e[fld])
                if ri is not None:
                    c = tok.setdefault((grp, fld + ' (integers)'), [0, 0, 0])
                    c[1] += 1
                    gi = INTS.get(fld)
                    if gi is None:
                        c[2] += 1
                    elif gi == ri:
                        c[0] += 1
                    else:
                        bad.append(('ints', short, fld, len(gi), len(ri)))
                    continue
                ref = flat(e[fld])
                if ref is None:
                    continue
                got = T.get(fld)
                c = tok.setdefault((grp, fld), [0, 0, 0])
                c[1] += 1
                if got is None:
                    c[2] += 1
                    continue
                want_b = [struct.pack('<d', x) for x in ref]
                # the payload after a field name may carry extra 8-byte words (array headers do not; dtype tuples are ints)
                if got == want_b or (len(got) > len(want_b) and got[-len(want_b):] == want_b) or got[:len(want_b)] == want_b:
                    c[0] += 1
                else:
                    bad.append(('value', short, fld, len(got), len(want_b)))
say(' members named in converted/*.json: %d; found in the pinned archive: %d; SHA-256 and size equal: %d'
    % (len(want), seen_members, hash_ok))
for (grp, fld), c in sorted(tok.items()):
    say('   %-17s %-32s bit-for-bit equal in %d of %d members%s' % (grp, fld, c[0], c[1], (' (field name not found in %d)' % c[2]) if c[2] else ''))
say(' problems: %d %s' % (len(bad), bad[:8]))
RES['b_archive'] = dict(named=len(want), found=seen_members, hash_equal=hash_ok)
RES['c_tokens'] = {'%s/%s' % k: v for k, v in tok.items()}
RES['c_problems'] = bad[:50]
json.dump(RES, open(OUTJ, 'w'), indent=1)
say('written', OUTJ)
