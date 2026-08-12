#!/usr/bin/env python3
"""Exact CP-SAT search for TT(56), a direct construction route to H(668)."""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from ortools.sat.python import cp_model

LENS=[56,56,56,55]
COEFF=[1,1,2,2]
PATTERNS=[
(4,2,6,11),(6,0,10,7),(8,6,6,9),(10,0,6,9),
(10,4,10,3),(10,8,2,9),(10,8,6,7),(12,10,6,3),
(14,4,6,5),(14,8,6,1),(16,2,6,1),(18,0,2,1),
]

def add_lex_geq_reverse(m,x,name):
    # x >= reverse(x), exact lex implication chain.
    pref=None
    n=len(x)
    for i in range(n):
        a=x[i]; b=x[n-1-i]
        if pref is None: m.AddBoolOr([a,b.Not()])
        else: m.AddBoolOr([pref.Not(),a,b.Not()])
        if i==n-1: break
        eq=m.NewBoolVar(f'{name}_eq_{i}')
        m.Add(a==b).OnlyEnforceIf(eq); m.Add(a!=b).OnlyEnforceIf(eq.Not())
        if pref is None: pref=eq
        else:
            q=m.NewBoolVar(f'{name}_pre_{i}')
            m.AddBoolAnd([pref,eq]).OnlyEnforceIf(q)
            m.AddBoolOr([pref.Not(),eq.Not(),q])
            pref=q

def verify(seq,S):
    if [sum(a) for a in seq] != list(S): return False
    for j in range(1,56):
        total=0
        for q,a in enumerate(seq):
            for i in range(len(a)-j): total += COEFF[q] * (a[i]!=a[i+j])
        if total != 167-3*j: return False
    return True

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--pattern',type=int,required=True); args=ap.parse_args(); p=args.pattern; assert 0<=p<len(PATTERNS); S=PATTERNS[p]
    m=cp_model.CpModel(); z=[]
    for q,n in enumerate(LENS):
        a=[m.NewBoolVar(f'z{q}_{i}') for i in range(n)]; z.append(a)
        neg=(n-S[q])//2; assert 2*neg==n-S[q]
        m.Add(sum(a)==neg)
        add_lex_geq_reverse(m,a,f'rev{q}')
    # For equal-length/equal-role X,Y, sequence swap is safe if row sums equal.
    # Current pattern list has no Sx==Sy except none; no extra constraint needed.
    for j in range(1,56):
        terms=[]; coeff=[]
        for q,a in enumerate(z):
            for i in range(len(a)-j):
                d=m.NewBoolVar(f'd_{j}_{q}_{i}')
                m.AddBoolXOr([a[i],a[i+j],d.Not()])
                terms.append(d); coeff.append(COEFF[q])
        m.Add(sum(c*t for c,t in zip(coeff,terms))==167-3*j)
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=535; solver.parameters.num_search_workers=4; solver.parameters.random_seed=7000+p; solver.parameters.log_search_progress=True
    print(json.dumps({'pattern_index':p,'row_sums':S,'start':time.time()}),flush=True)
    t=time.time(); st=solver.Solve(m); dt=time.time()-t; name=solver.StatusName(st)
    out={'pattern_index':p,'row_sums':S,'status':name,'seconds':dt,'conflicts':solver.NumConflicts(),'branches':solver.NumBranches(),'wall_time':solver.WallTime()}
    if st in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        pm=[]
        for a in z: pm.append([1-2*solver.Value(v) for v in a])
        out['sequences']=pm; out['verified']=verify(pm,S)
        if not out['verified']: raise SystemExit('TT model failed independent verification')
    Path(f'tt_result_{p}.json').write_text(json.dumps(out,indent=2)); print(json.dumps({k:v for k,v in out.items() if k!='sequences'}),flush=True)

if __name__=='__main__': main()
