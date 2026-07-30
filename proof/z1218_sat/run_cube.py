#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from generate_cnf import build, write, x

ap=argparse.ArgumentParser()
ap.add_argument('--branch',choices=['no8','row8'],required=True)
ap.add_argument('--cube',type=int,required=True)
ap.add_argument('--bits',type=int,default=6)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
assert 0 <= a.cube < (1<<a.bits)
cnf=build(a.branch)
# Exhaustive cube on row 1, columns 0..bits-1. All these columns are
# incident with the fixed marked row in both branches for bits<=6.
for c in range(a.bits):
    bit=(a.cube >> c)&1
    cnf.unit(x(1,c) if bit else -x(1,c))
write(cnf,a.out,f'{a.branch}-cube-{a.cube:0{a.bits}b}')
print(a.branch,a.cube,a.bits,cnf.nvars,len(cnf.clauses))
