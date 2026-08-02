#!/usr/bin/env python3
"""Generate one exhaustive shard by fixing the canonical first column degree.

In both base branches row 0 belongs to column 0 and every column has degree at
least five. Thus degree(column 0) is exactly one of 5,...,12. The eight shards
are disjoint and their union is the complete branch.
"""
import argparse
from pathlib import Path
from generate_cnf import build, write, exactly, x, R

ap=argparse.ArgumentParser()
ap.add_argument('--branch',choices=['no8','row8'],required=True)
ap.add_argument('--degree',type=int,choices=range(5,13),required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
cnf=build(a.branch)
# row 0 is already fixed to one in column 0, so exactly degree-1 among rows 1..11
exactly(cnf,[x(r,0) for r in range(1,R)],a.degree-1)
write(cnf,a.out,f'{a.branch}-col0deg{a.degree}')
print(f'{a.branch} degree {a.degree}: vars={cnf.nvars} clauses={len(cnf.clauses)}')
