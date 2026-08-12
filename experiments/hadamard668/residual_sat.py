#!/usr/bin/env python3
"""Exact SAT search for the published H(668) fourth-vector residual.

A SAT model is a length-167 binary vector of weight 80 whose cyclic
intersection counts equal the published 83 targets.  Together with the three
published blocks this yields a Goethals-Seidel Hadamard matrix of order 668.

The 16 CUBE values fix x[1],x[166],x[2],x[165] after bracelet
canonicalization and therefore partition the complete normalized search.
"""
from __future__ import annotations

import argparse, json, time
from pathlib import Path
from pysat.solvers import Gluecard4

N = 167
W = 80
TARGET = (
    41,37,40,39,41,39,35,38,36,34,42,39,37,37,32,37,
    37,36,36,36,40,39,36,37,39,38,35,33,39,35,37,41,
    42,40,41,38,43,41,34,39,39,36,42,39,38,41,40,40,
    37,38,37,37,35,37,37,37,36,38,37,34,37,40,39,37,
    38,38,42,38,42,37,34,39,39,37,41,36,34,37,38,42,
    45,39,40,
)
GUIDE = (
1,1,1,0,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,1,0,0,0,1,1,0,0,1,1,0,1,0,1,1,1,0,0,1,0,1,1,0,0,0,0,1,1,0,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,1,0,1,0,0,1,1,1,1,0,0,1,0,0,0,0,1,0,0,1,0,0,1,0,0,1,1,1,1,0,1,0,0,1,0,0,0,1,1,1,1,0,0,1,1,0,0,0,1,0,
)
assert len(TARGET) == 83 and len(GUIDE) == N and sum(GUIDE) == W

class Alloc:
    def __init__(self): self.top = N
    def new(self): self.top += 1; return self.top

def x(i: int) -> int: return i + 1

def exactly(s, lits, k):
    s.add_atmost(list(lits), int(k))
    s.add_atmost([-z for z in lits], len(lits) - int(k))

def xor_indicator(s, r, a, b):
    s.add_clause([-r, a, b])
    s.add_clause([-r, -a, -b])
    s.add_clause([r, -a, b])
    s.add_clause([r, a, -b])

def xnor_indicator(s, r, a, b):
    s.add_clause([-r, a, -b])
    s.add_clause([-r, -a, b])
    s.add_clause([r, a, b])
    s.add_clause([r, -a, -b])

def boolean_and(s, r, a, b):
    s.add_clause([-r, a]); s.add_clause([-r, b]); s.add_clause([r, -a, -b])

def lex_geq(s, al, left, right):
    prefix = None
    for idx, (a, b) in enumerate(zip(left, right)):
        s.add_clause([a, -b] if prefix is None else [-prefix, a, -b])
        if idx == len(left)-1: break
        eq = al.new(); xnor_indicator(s, eq, a, b)
        if prefix is None: prefix = eq
        else:
            q = al.new(); boolean_and(s, q, prefix, eq); prefix = q

def bracelet(s, al):
    base = [x(i) for i in range(N)]
    s.add_clause([x(0)])
    for sh in range(1, N):
        lex_geq(s, al, base, [x((i+sh)%N) for i in range(N)])
    for sh in range(N):
        lex_geq(s, al, base, [x((sh-i)%N) for i in range(N)])

def verify(v):
    assert len(v)==N and sum(v)==W
    got=[]
    for sh in range(1,84):
        got.append(sum(v[i]*v[(i+sh)%N] for i in range(N)))
    return tuple(got)==TARGET, got

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--cube',type=int,required=True)
    a=ap.parse_args(); assert 0 <= a.cube < 16
    al=Alloc(); s=Gluecard4(use_timer=True)
    primary=[x(i) for i in range(N)]
    exactly(s, primary, W)
    for sh,t in enumerate(TARGET,1):
        ds=[]
        for i in range(N):
            r=al.new(); xor_indicator(s,r,x(i),x((i+sh)%N)); ds.append(r)
        exactly(s, ds, 2*(W-t))
    bracelet(s,al)
    split=[1,166,2,165]
    for bit,pos in enumerate(split):
        val=(a.cube>>bit)&1
        s.add_clause([x(pos) if val else -x(pos)])
    try:
        s.set_phases([x(i) if GUIDE[i] else -x(i) for i in range(N)])
    except Exception:
        pass
    print(json.dumps({'cube':a.cube,'variables':al.top,'split':split,'start':time.time()}),flush=True)
    t0=time.time(); sat=s.solve(); elapsed=time.time()-t0
    if not sat:
        print(json.dumps({'cube':a.cube,'status':'UNSAT','seconds':elapsed}),flush=True)
        Path(f'result_{a.cube}.json').write_text(json.dumps({'cube':a.cube,'status':'UNSAT','seconds':elapsed},indent=2))
        return
    m={z for z in s.get_model() if z>0}; v=[1 if x(i) in m else 0 for i in range(N)]
    ok,got=verify(v)
    out={'cube':a.cube,'status':'SAT','seconds':elapsed,'verified':ok,'weight':sum(v),'vector':v,'target':list(TARGET),'actual':got}
    Path(f'result_{a.cube}.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'cube':a.cube,'status':'SAT','seconds':elapsed,'verified':ok,'weight':sum(v)}),flush=True)
    if not ok: raise SystemExit('solver model failed independent arithmetic verification')

if __name__=='__main__': main()
