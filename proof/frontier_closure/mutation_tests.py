#!/usr/bin/env python3
from __future__ import annotations
import copy,gzip,importlib.util,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('verifier',ROOT/'verify_all.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
profiles=v.enumerate_column_profiles()

def expect_rejection(label,fn):
    try:fn()
    except (AssertionError,KeyError,ValueError):
        print(label+': REJECTED');return
    raise AssertionError(label+' was accepted')

with tempfile.TemporaryDirectory(prefix='z1318-mutations-') as td:
    td=Path(td)
    # Witness: force three copies of one row triple by replacing columns.
    src=ROOT/'data/z13_18_116_witness.json'
    obj=json.loads(src.read_text())
    triple_mask=(1<<0)|(1<<1)|(1<<2)
    obj['column_masks'][0]=triple_mask
    obj['column_masks'][1]=triple_mask
    obj['column_masks'][2]=triple_mask
    # Keep metadata internally inconsistent too; either defect must be rejected.
    p=td/'bad_witness.json';p.write_text(json.dumps(obj))
    expect_rejection('mutated witness',lambda:v.verify_witness(p,13,18,116))

    # Global certificate: make the certified negative RHS false.
    src=sorted((ROOT/'certificates/global').glob('p*_f*.json'))[0]
    obj=json.loads(src.read_text());obj['cert']['rhs']=0
    p=td/'bad_global.json';p.write_text(json.dumps(obj))
    # Give it a valid profile-index filename so rejection reaches certificate logic.
    q=td/src.name;q.write_text(p.read_text())
    expect_rejection('mutated global RHS',lambda:v.verify_global_certificate(q,profiles))

    # Local certificate: alter one positive dual numerator.
    src=ROOT/'certificates/local/pat01.json.gz'
    with gzip.open(src,'rt',encoding='utf8') as f:o=json.load(f)
    def mutate(node):
        if node[0]=='D' and node[1]:
            node[1][0][1]=0;return True
        if node[0]=='P':return mutate(node[1])
        if node[0]=='I':return mutate(node[3]) or mutate(node[4])
        if node[0]=='B':
            return any(mutate(x) for x in node[2])
        return False
    assert mutate(o['tree'])
    p=td/'bad_local.json.gz'
    with gzip.open(p,'wt',encoding='utf8') as f:json.dump(o,f)
    expect_rejection('mutated local dual',lambda:v.verify_local_certificate(p,{5:3,6:6}))

    # Metadata: alter a profile count.
    src=ROOT/'certificates/local/pat00.json.gz'
    with gzip.open(src,'rt',encoding='utf8') as f:o=json.load(f)
    o['counts']['5']+=1
    p=td/'bad_metadata.json.gz'
    with gzip.open(p,'wt',encoding='utf8') as f:json.dump(o,f)
    expect_rejection('mutated local metadata',lambda:v.verify_local_certificate(p,{5:3,6:5,7:1}))

print('ALL MUTATION TESTS PASSED')
