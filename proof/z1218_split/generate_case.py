#!/usr/bin/env python3
from __future__ import annotations
import argparse, math
from itertools import combinations
from collections import Counter
from pathlib import Path
R,C=12,18

def x(r,c): return 1+r*C+c
class CNF:
    def __init__(self): self.nvars=R*C; self.clauses=[]
    def new(self): self.nvars+=1; return self.nvars
    def add(self,*ls):
        s=set(ls)
        if any(-z in s for z in s): return
        self.clauses.append(tuple(sorted(s,key=lambda z:(abs(z),z<0))))
    def unit(self,l): self.add(l)

def at_most(cnf,lits,k):
    n=len(lits)
    if k<0: cnf.add(); return
    if k>=n: return
    if k==0:
        for l in lits: cnf.add(-l)
        return
    if n==1: cnf.add(-lits[0]); return
    s=[[cnf.new() for _ in range(k)] for _ in range(n-1)]
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
def and3(cnf,z,a,b,c): cnf.add(-z,a); cnf.add(-z,b); cnf.add(-z,c); cnf.add(z,-a,-b,-c)
def lex_ge(cnf,A,B):
    assert len(A)==len(B) and A
    prefix=None
    for i,(a,b) in enumerate(zip(A,B)):
        if prefix is None: cnf.add(a,-b)
        else: cnf.add(-prefix,a,-b)
        if i==len(A)-1: break
        q=cnf.new(); equiv(cnf,q,a,b)
        if prefix is None: prefix=q
        else:
            z=cnf.new(); and2(cnf,z,prefix,q); prefix=z

def add_row_lex(cnf):
    for r in range(1,11): lex_ge(cnf,[x(r,c) for c in range(C)],[x(r+1,c) for c in range(C)])
def add_k33_counters(cnf):
    for a,b,c in combinations(range(R),3):
        ys=[]
        for j in range(C):
            z=cnf.new(); and3(cnf,z,x(a,j),x(b,j),x(c,j)); ys.append(z)
        at_most(cnf,ys,2)

def profiles101():
    out=[]
    def rec(pos,last,rem,v):
        if pos==18:
            if rem==0:
                s=sum(math.comb(d,3) for d in v)
                if s<=330: out.append((tuple(v),330-s))
            return
        left=18-pos
        for d in range(last,12):
            rr=rem-d
            if rr<d*(left-1): break
            if rr>11*(left-1): continue
            v.append(d); rec(pos+1,d,rr,v); v.pop()
    rec(0,5,101,[])
    return list(reversed(out))

def row8_cases():
    out=[]
    for pi,(p,slack) in enumerate(profiles101()):
        cnt=Counter(p); vals=sorted(cnt); sels=set()
        def rec(i,left,cur):
            if i==len(vals):
                if left==0:
                    s=[]
                    for d,k in cur.items(): s += [d]*k
                    if sum(math.comb(d,2) for d in s)<=110: sels.add(tuple(sorted(s,reverse=True)))
                return
            d=vals[i]
            for k in range(min(cnt[d],left)+1): cur[d]=k; rec(i+1,left-k,cur)
            cur.pop(d,None)
        rec(0,8,{})
        for s in sorted(sels,reverse=True):
            rem=list(p)
            for d in s: rem.remove(d)
            out.append((pi,slack,s,tuple(sorted(rem,reverse=True))))
    return out

def build_no8():
    cnf=CNF()
    for c in range(C): cnf.unit(x(0,c) if c<10 else -x(0,c))
    for r in range(1,R): exactly(cnf,[x(r,c) for c in range(C)],9)
    for c in range(10): at_least(cnf,[x(r,c) for r in range(1,R)],4)
    for c in range(10,C): at_least(cnf,[x(r,c) for r in range(1,R)],5)
    for lo,hi in [(0,10),(10,18)]:
        for c in range(lo,hi-1): lex_ge(cnf,[x(r,c) for r in range(1,R)],[x(r,c+1) for r in range(1,R)])
    add_row_lex(cnf); add_k33_counters(cnf)
    return cnf,{'branch':'no8'}

def build_row8(caseid):
    cases=row8_cases(); pi,slack,sel,unsel=cases[caseid]
    cnf=CNF()
    for c in range(C): cnf.unit(x(0,c) if c<8 else -x(0,c))
    deg=list(sel)+list(unsel)
    for c,d in enumerate(deg): exactly(cnf,[x(r,c) for r in range(1,R)],d)
    for r in range(1,R): at_least(cnf,[x(r,c) for c in range(C)],8)
    for lo,hi in [(0,8),(8,18)]:
        for c in range(lo,hi-1):
            if deg[c]==deg[c+1]: lex_ge(cnf,[x(r,c) for r in range(1,R)],[x(r,c+1) for r in range(1,R)])
    add_row_lex(cnf); add_k33_counters(cnf)
    return cnf,{'branch':'row8','case':caseid,'profile':pi,'slack':slack,'selected':sel,'unselected':unsel}

def write(cnf,path,meta):
    path=Path(path)
    with path.open('w') as f:
        f.write('c '+repr(meta)+'\n'); f.write(f'p cnf {cnf.nvars} {len(cnf.clauses)}\n')
        for cl in cnf.clauses: f.write(' '.join(map(str,cl))+' 0\n')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--branch',choices=['no8','row8']); ap.add_argument('--case',type=int,default=0); ap.add_argument('--out'); ap.add_argument('--list',action='store_true'); a=ap.parse_args()
    if a.list:
        for i,z in enumerate(row8_cases()): print(i,z)
        return
    if not a.out: raise SystemExit('--out required unless --list')
    cnf,meta=build_no8() if a.branch=='no8' else build_row8(a.case)
    write(cnf,a.out,meta); print(meta); print('vars',cnf.nvars,'clauses',len(cnf.clauses))
if __name__=='__main__': main()
