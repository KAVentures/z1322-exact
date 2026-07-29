#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'z1218_sat'))
from generate_cnf import build, write, x, C

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--branch', choices=['no8','row8'], required=True)
    ap.add_argument('--a', type=int, required=True)
    ap.add_argument('--b', type=int, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args=ap.parse_args()
    marked=10 if args.branch=='no8' else 8
    assert 0 <= args.a <= marked
    assert 0 <= args.b <= C-marked
    if args.branch=='no8': assert args.a + args.b == 9
    else: assert args.a + args.b >= 8
    cnf=build(args.branch)
    # Base CNF lex-sorts columns inside each marked-row incidence class.
    # Thus row 1 is a prefix of ones then zeros in each class.
    for c in range(marked): cnf.unit(x(1,c) if c < args.a else -x(1,c))
    for c in range(marked,C): cnf.unit(x(1,c) if c-marked < args.b else -x(1,c))
    write(cnf,args.out,f'{args.branch}-a{args.a}-b{args.b}')
    print(f'{args.branch} a={args.a} b={args.b}: vars={cnf.nvars} clauses={len(cnf.clauses)}')
if __name__=='__main__': main()
