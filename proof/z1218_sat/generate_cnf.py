#!/usr/bin/env python3
from __future__ import annotations
import argparse
from itertools import combinations
from pathlib import Path
R,C=12,18
class CNF:
    def __init__(self): self.nvars=R*C; self.clauses=[]
    def new_var(self): self.nvars+=1; return self.nvars
    def add(self,*lits):
        s=set(lits)
        if any(-z in s for z in s): return
        self.clauses.append(sorted(s,key=lambda z:(abs(z),z<0)))
    def unit(self,lit): self.add(lit)
def x(r,c): return 1+r*C+c
def at_most(cnf,lits,k):
    n=len(lits)
    if k<0: cnf.add(); return
    if k>=n: return
    if k==0:
        for lit in lits: cnf.add(-lit)
        return
    if n==1: cnf.add(-lits[0]); return
    s=[[cnf.new_var() for _ in range(k)] for _ in range(n-1)]
    cnf.add(-lits[0],s[0][0])
    for j in range(1,k): cnf.add(-s[0][j])
    for i in range(1,n-1):
        cnf.add(-lits[i],s[i][0]); cnf.add(-s[i-1][0],s[i][0])
        for j in range(1,k):
            cnf.add(-lits[i],-s[i-1][j-1],s[i][j]); cnf.add(-s[i-1][j],s[i][j])
        cnf.add(-lits[i],-s[i-1][k-1])
    cnf.add(-lits[-1],-s[n-2][k-1])
def at_least(cnf,lits,k): at_most(cnf,[-l for l in lits],len(lits)-k)
def exactly(cnf,lits,k): at_most(cnf,lits,k); at_least(cnf,lits,k)
def equiv(cnf,q,a,b):
    cnf.add(-q,-a,b); cnf.add(-q,a,-b); cnf.add(q,-a,-b); cnf.add(q,a,b)
def and2(cnf,z,a,b): cnf.add(-z,a); cnf.add(-z,b); cnf.add(z,-a,-b)
def lex_ge(cnf,A,B):
    assert len(A)==len(B) and A
    prefix=None
    for i,(a,b) in enumerate(zip(A,B)):
        if prefix is None: cnf.add(a,-b)
        else: cnf.add(-prefix,a,-b)
        if i==len(A)-1: break
        q=cnf.new_var(); equiv(cnf,q,a,b)
        if prefix is None: prefix=q
        else:
            z=cnf.new_var(); and2(cnf,z,prefix,q); prefix=z
def add_k33(cnf):
    for rs in combinations(range(R),3):
        for cs in combinations(range(C),3): cnf.add(*[-x(r,c) for r in rs for c in cs])
def fix_marked_row(cnf,d):
    for c in range(C): cnf.unit(x(0,c) if c<d else -x(0,c))
def add_column_lex(cnf,groups):
    for group in groups:
        cols=list(group)
        for c1,c2 in zip(cols,cols[1:]): lex_ge(cnf,[x(r,c1) for r in range(1,R)],[x(r,c2) for r in range(1,R)])
def add_selected_pair_capacity(cnf,d):
    for r,s in combinations(range(1,R),2):
        ys=[]
        for c in range(d):
            y=cnf.new_var(); ys.append(y)
            cnf.add(-y,x(r,c)); cnf.add(-y,x(s,c)); cnf.add(y,-x(r,c),-x(s,c))
        at_most(cnf,ys,2)
def build(branch):
    cnf=CNF()
    if branch=='no8':
        fix_marked_row(cnf,10)
        for r in range(1,R): exactly(cnf,[x(r,c) for c in range(C)],9)
        add_column_lex(cnf,[range(0,10),range(10,C)]); add_selected_pair_capacity(cnf,10)
    elif branch=='row8':
        fix_marked_row(cnf,8)
        exactly(cnf,[x(r,c) for r in range(1,R) for c in range(C)],101)
        for r in range(1,R): at_least(cnf,[x(r,c) for c in range(C)],8)
        add_column_lex(cnf,[range(0,8),range(8,C)]); add_selected_pair_capacity(cnf,8)
    else: raise ValueError(branch)
    marked=10 if branch=='no8' else 8
    for c in range(C):
        need=4 if c<marked else 5
        at_least(cnf,[x(r,c) for r in range(1,R)],need)
    add_k33(cnf); return cnf
def write(cnf,path,branch):
    with path.open('w') as f:
        f.write(f'c Z(12,18,3,3) 109-edge exclusion branch {branch}\n')
        f.write('c primary variables x(r,c)=1+r*18+c for 0<=r<12,0<=c<18\n')
        f.write(f'p cnf {cnf.nvars} {len(cnf.clauses)}\n')
        for clause in cnf.clauses: f.write(' '.join(map(str,clause))+' 0\n')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--branch',choices=['no8','row8'],required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); cnf=build(a.branch); write(cnf,a.out,a.branch); print(f'{a.branch}: vars={cnf.nvars} clauses={len(cnf.clauses)} out={a.out}')
if __name__=='__main__': main()
