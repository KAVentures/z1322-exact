#!/usr/bin/env python3
"""Exact CP-SAT search for cyclic D-optimal SDS (167;73,76;66).

Any SAT pair, combined with two Paley-Todd length-167 blocks in the
Goethals-Seidel array, yields a Hadamard matrix of order 668.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from ortools.sat.python import cp_model
N=167; KA=73; KB=76
HINTA=tuple(map(int,"11110011011011101110010010000111100100100111010101011010101110000000010110000100000001010010011000000001110010101000111100001011100100101110101100011000001101000001100"))
HINTB=tuple(map(int,"00000111001100100011101100000001101100101110001000001011010110110110011001010011110011101100100000111000000010000010010101111110010110101100011000010101011110110101000"))
assert len(HINTA)==len(HINTB)==N and sum(HINTA)==KA and sum(HINTB)==KB

def eqvar(m,a,b,name):
 e=m.NewBoolVar(name); m.Add(a==b).OnlyEnforceIf(e); m.Add(a!=b).OnlyEnforceIf(e.Not()); return e

def lex_geq(m,left,right,name):
 pref=None
 for i,(a,b) in enumerate(zip(left,right)):
  m.AddBoolOr([a,b.Not()] if pref is None else [pref.Not(),a,b.Not()])
  if i==len(left)-1: break
  e=eqvar(m,a,b,f'{name}_e{i}')
  if pref is None: pref=e
  else:
   q=m.NewBoolVar(f'{name}_p{i}'); m.AddBoolAnd([pref,e]).OnlyEnforceIf(q); m.AddBoolOr([pref.Not(),e.Not(),q]); pref=q

def verify(A,B):
 if sum(A)!=KA or sum(B)!=KB:return False
 for s in range(1,84):
  da=sum(A[i]!=A[(i+s)%N] for i in range(N)); db=sum(B[i]!=B[(i+s)%N] for i in range(N))
  if da+db!=166:return False
 return True

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--cube',type=int,required=True); args=ap.parse_args(); assert 0<=args.cube<16
 m=cp_model.CpModel(); A=[m.NewBoolVar(f'a{i}') for i in range(N)]; B=[m.NewBoolVar(f'b{i}') for i in range(N)]
 m.Add(sum(A)==KA); m.Add(sum(B)==KB); m.Add(A[0]==1)
 for s in range(1,84):
  ds=[]
  for X,nm in ((A,'a'),(B,'b')):
   for i in range(N):
    d=m.NewBoolVar(f'd_{nm}_{s}_{i}'); m.AddBoolXOr([X[i],X[(i+s)%N],d.Not()]); ds.append(d)
  m.Add(sum(ds)==166)
 # Common dihedral action allows A to be chosen as its bracelet maximum, without restricting existence.
 for sh in range(1,N): lex_geq(m,A,[A[(i+sh)%N] for i in range(N)],f'r{sh}')
 for sh in range(N): lex_geq(m,A,[A[(sh-i)%N] for i in range(N)],f'f{sh}')
 split=[1,166,2,165]
 for bit,pos in enumerate(split):m.Add(A[pos]==((args.cube>>bit)&1))
 for i,v in enumerate(HINTA):m.AddHint(A[i],v)
 for i,v in enumerate(HINTB):m.AddHint(B[i],v)
 sol=cp_model.CpSolver(); sol.parameters.max_time_in_seconds=535; sol.parameters.num_search_workers=4; sol.parameters.random_seed=9000+args.cube; sol.parameters.log_search_progress=True
 print(json.dumps({'cube':args.cube,'start':time.time(),'split':split}),flush=True)
 t=time.time(); st=sol.Solve(m); dt=time.time()-t; name=sol.StatusName(st)
 out={'cube':args.cube,'status':name,'seconds':dt,'conflicts':sol.NumConflicts(),'branches':sol.NumBranches(),'wall_time':sol.WallTime()}
 if st in (cp_model.FEASIBLE,cp_model.OPTIMAL):
  av=[sol.Value(x) for x in A];bv=[sol.Value(x) for x in B];out.update(A=av,B=bv,verified=verify(av,bv));
  if not out['verified']:raise SystemExit('D-optimal SAT model failed independent verification')
 Path(f'do334_result_{args.cube}.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ('A','B')}),flush=True)
if __name__=='__main__':main()
