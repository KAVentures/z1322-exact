#!/usr/bin/env python3
"""Generate a double-lex shard fixing two selected-column degrees and intersection.

Both columns 0 and 1 contain the marked row. The selected-pair capacity clauses
in the base formula imply that they share at most two further rows, hence their
total intersection is exactly one of 1,2,3. For a fixed first-column degree,
the 8*3 choices for (degree(column 1), intersection) are disjoint and exhaustive.
"""
import argparse
from pathlib import Path
from generate_cnf import build, write, exactly, lex_ge, and2, x, R, C

ap=argparse.ArgumentParser()
ap.add_argument('--branch',choices=['no8','row8'],required=True)
ap.add_argument('--degree0',type=int,choices=range(5,13),required=True)
ap.add_argument('--degree1',type=int,choices=range(5,13),required=True)
ap.add_argument('--intersection',type=int,choices=[1,2,3],required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args()
cnf=build(a.branch)
exactly(cnf,[x(r,0) for r in range(1,R)],a.degree0-1)
exactly(cnf,[x(r,1) for r in range(1,R)],a.degree1-1)
ys=[]
for r in range(1,R):
    y=cnf.new_var()
    and2(cnf,y,x(r,0),x(r,1))
    ys.append(y)
exactly(cnf,ys,a.intersection-1)
for r in range(1,R-1):
    lex_ge(cnf,[x(r,c) for c in range(C)],[x(r+1,c) for c in range(C)])
write(cnf,a.out,f'{a.branch}-doublelex-d0{a.degree0}-d1{a.degree1}-q{a.intersection}')
print(a.branch,a.degree0,a.degree1,a.intersection,cnf.nvars,len(cnf.clauses))
