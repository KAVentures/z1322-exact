#!/usr/bin/env python3
"""Independent OR-Tools CP-SAT model for the exact H(668) residual."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from ortools.sat.python import cp_model

N=167; W=80
TARGET=(41,37,40,39,41,39,35,38,36,34,42,39,37,37,32,37,37,36,36,36,40,39,36,37,39,38,35,33,39,35,37,41,42,40,41,38,43,41,34,39,39,36,42,39,38,41,40,40,37,38,37,37,35,37,37,37,36,38,37,34,37,40,39,37,38,38,42,38,42,37,34,39,39,37,41,36,34,37,38,42,45,39,40)
GUIDE=(1,1,1,0,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,1,0,0,0,1,1,0,0,1,1,0,1,0,1,1,1,0,0,1,0,1,1,0,0,0,0,1,1,0,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,1,1,0,0,0,0,0,0,1,0,1,0,0,1,1,1,1,0,0,1,0,0,0,0,1,0,0,1,0,0,1,0,0,1,1,1,1,0,1,0,0,1,0,0,0,1,1,1,1,0,0,1,1,0,0,0,1,0)
assert len(TARGET)==83 and len(GUIDE)==N and sum(GUIDE)==W

def add_eq(model,a,b,name):
    e=model.NewBoolVar(name)
    model.Add(a==b).OnlyEnforceIf(e)
    model.Add(a!=b).OnlyEnforceIf(e.Not())
    return e

def lex_geq(model,left,right,prefix_name):
    # For every position i, if all previous positions are equal, forbid left_i=0,right_i=1.
    prefix=None
    for i,(a,b) in enumerate(zip(left,right)):
        if prefix is None:
            model.AddBoolOr([a,b.Not()])
        else:
            model.AddBoolOr([prefix.Not(),a,b.Not()])
        if i==len(left)-1: break
        eq=add_eq(model,a,b,f'{prefix_name}_eq_{i}')
        if prefix is None:
            prefix=eq
        else:
            nxt=model.NewBoolVar(f'{prefix_name}_pre_{i}')
            model.AddBoolAnd([prefix,eq]).OnlyEnforceIf(nxt)
            model.AddBoolOr([prefix.Not(),eq.Not(),nxt])
            prefix=nxt

def verify(v):
    if len(v)!=N or sum(v)!=W: return False
    return all(sum(v[i]*v[(i+s)%N] for i in range(N))==TARGET[s-1] for s in range(1,84))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--cube',type=int,required=True); args=ap.parse_args(); assert 0<=args.cube<16
    m=cp_model.CpModel(); x=[m.NewBoolVar(f'x{i}') for i in range(N)]
    m.Add(sum(x)==W)
    # Safe rotation normalization.
    m.Add(x[0]==1)
    for s,t in enumerate(TARGET,1):
        ds=[]
        for i in range(N):
            d=m.NewBoolVar(f'd_{s}_{i}')
            # d = x_i XOR x_{i+s}; odd parity of x_i,x_j,not d.
            m.AddBoolXOr([x[i],x[(i+s)%N],d.Not()])
            ds.append(d)
        m.Add(sum(ds)==2*(W-t))
    # Dihedral bracelet maximum: one representative per rotation/reflection orbit.
    base=x
    for sh in range(1,N):
        lex_geq(m,base,[x[(i+sh)%N] for i in range(N)],f'r{sh}')
    for sh in range(N):
        lex_geq(m,base,[x[(sh-i)%N] for i in range(N)],f'f{sh}')
    split=[1,166,2,165]
    for bit,pos in enumerate(split): m.Add(x[pos]==((args.cube>>bit)&1))
    for i,v in enumerate(GUIDE): m.AddHint(x[i],v)
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=535.0; solver.parameters.num_search_workers=4; solver.parameters.random_seed=1000+args.cube; solver.parameters.log_search_progress=True
    print(json.dumps({'cube':args.cube,'start':time.time(),'split':split}),flush=True)
    t0=time.time(); status=solver.Solve(m); dt=time.time()-t0
    name=solver.StatusName(status)
    out={'cube':args.cube,'status':name,'seconds':dt,'conflicts':solver.NumConflicts(),'branches':solver.NumBranches(),'wall_time':solver.WallTime()}
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        v=[solver.Value(z) for z in x]; out.update(vector=v,weight=sum(v),verified=verify(v));
        if not out['verified']: raise SystemExit('CP-SAT model failed independent verification')
    Path(f'cpsat_result_{args.cube}.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({k:v for k,v in out.items() if k!='vector'}),flush=True)

if __name__=='__main__': main()
