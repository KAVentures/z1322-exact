#!/usr/bin/env python3
"""Adversarial rejection tests for the exact verifier."""
import csv,gzip,json,tempfile
from pathlib import Path
import verify_all_exact as v
ROOT=Path(__file__).resolve().parent

def expect_reject(label,fn):
    try:fn()
    except (AssertionError,KeyError,ValueError,EOFError,OSError):
        print(label+': REJECTED')
        return
    raise AssertionError(label+' was incorrectly accepted')

def test_witness():
    rows=[list(map(int,r)) for r in csv.reader(open(ROOT/'data/z12_18_108_witness_verified.csv'))]
    for i,row in enumerate(rows):
        for j,x in enumerate(row):
            if x==0:rows[i][j]=1;break
        else:continue
        break
    with tempfile.NamedTemporaryFile('w',newline='',suffix='.csv',delete=False) as f:
        csv.writer(f).writerows(rows);p=Path(f.name)
    try:expect_reject('mutated 108 witness',lambda:v.verify_108(p))
    finally:p.unlink(missing_ok=True)

def test_witness_103():
    rows=[list(map(int,r)) for r in csv.reader(open(ROOT/'data/z12_17_103_witness_verified.csv'))]
    for i,row in enumerate(rows):
        for j,x in enumerate(row):
            if x==0:rows[i][j]=1;break
        else:continue
        break
    with tempfile.NamedTemporaryFile('w',newline='',suffix='.csv',delete=False) as f:
        csv.writer(f).writerows(rows);p=Path(f.name)
    try:expect_reject('mutated 103 witness',lambda:v.verify_103(p))
    finally:p.unlink(missing_ok=True)

def test_witness_114():
    rows=[list(map(int,r)) for r in csv.reader(open(ROOT/'data/z12_19_114_witness_verified.csv'))]
    for i,row in enumerate(rows):
        for j,x in enumerate(row):
            if x==0:rows[i][j]=1;break
        else:continue
        break
    with tempfile.NamedTemporaryFile('w',newline='',suffix='.csv',delete=False) as f:
        csv.writer(f).writerows(rows);p=Path(f.name)
    try:expect_reject('mutated 114 witness',lambda:v.verify_114(p))
    finally:p.unlink(missing_ok=True)

def test_witness_n(n,total,verifier):
    path=ROOT/f'data/z12_{n}_{total}_witness_verified.csv'
    rows=[list(map(int,r)) for r in csv.reader(open(path))]
    for i,row in enumerate(rows):
        for j,x in enumerate(row):
            if x==0:rows[i][j]=1;break
        else:continue
        break
    with tempfile.NamedTemporaryFile('w',newline='',suffix='.csv',delete=False) as f:
        csv.writer(f).writerows(rows);p=Path(f.name)
    try:expect_reject(f'mutated {total} witness',lambda:verifier(p))
    finally:p.unlink(missing_ok=True)

def find_dual(node):
    if isinstance(node,list):
        if node and node[0]=='D' and node[1]:return node
        for x in node:
            z=find_dual(x)
            if z:return z
    return None

def test_row8_cert():
    src=ROOT/'certificates/z1218/row8_caseB_cert.json.gz'
    with gzip.open(src,'rt',encoding='utf8') as f:o=json.load(f)
    d=find_dual(o['tree']);assert d and d[1]
    d[1][0][1]=0
    with tempfile.NamedTemporaryFile('wb',suffix='.json.gz',delete=False) as f:p=Path(f.name)
    with gzip.open(p,'wt',encoding='utf8') as f:json.dump(o,f,separators=(',',':'))
    try:expect_reject('mutated rational leaf',lambda:v.verify_row8(p))
    finally:p.unlink(missing_ok=True)

def test_bridge_cert():
    src=ROOT/'certificates/z1217/000.json.gz'
    with gzip.open(src,'rt',encoding='utf8') as f:o=json.load(f)
    o['pattern'][0]-=1
    with tempfile.NamedTemporaryFile('wb',suffix='.json.gz',delete=False) as f:p=Path(f.name)
    with gzip.open(p,'wt',encoding='utf8') as f:json.dump(o,f,separators=(',',':'))
    pats=v.z1217_patterns()
    try:expect_reject('mutated bridge metadata',lambda:v.verify_z1217_part((str(p),0,pats[0])))
    finally:p.unlink(missing_ok=True)

if __name__=='__main__':
    test_witness();test_witness_103();test_witness_114()
    test_witness_n(20,120,v.verify_120);test_witness_n(21,126,v.verify_126);test_witness_n(22,132,v.verify_132)
    test_row8_cert();test_bridge_cert();print('ALL MUTATION TESTS PASSED')
