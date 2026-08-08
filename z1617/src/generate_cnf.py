#!/usr/bin/env python3
"""Proof-oriented SAT encoding for a hypothetical 133-edge 16x17 K_3,3-free matrix."""
from __future__ import annotations
import argparse,json
from itertools import combinations
from pathlib import Path
R,C=16,17
# Exact/proved upper bounds after deleting the k least-degree rows.
DELETION_UPPER={1:126,2:118,3:110,4:103,5:96,6:90,7:81,8:74}

class CNF:
 def __init__(self): self.nvars=R*C; self.clauses=[]
 def new(self): self.nvars+=1; return self.nvars
 def add(self,*lits):
  s=set(lits)
  if any(-z in s for z in s): return
  self.clauses.append(sorted(s,key=lambda z:(abs(z),z<0)))

def x(r,c): return 1+r*C+c

def at_most(cnf,lits,k):
 n=len(lits)
 if k<0: cnf.add(); return
 if k>=n:return
 if k==0:
  for z in lits:cnf.add(-z)
  return
 if n==1:cnf.add(-lits[0]);return
 s=[[cnf.new() for _ in range(k)] for _ in range(n-1)]
 cnf.add(-lits[0],s[0][0])
 for j in range(1,k):cnf.add(-s[0][j])
 for i in range(1,n-1):
  cnf.add(-lits[i],s[i][0]);cnf.add(-s[i-1][0],s[i][0])
  for j in range(1,k):
   cnf.add(-lits[i],-s[i-1][j-1],s[i][j]);cnf.add(-s[i-1][j],s[i][j])
  cnf.add(-lits[i],-s[i-1][k-1])
 cnf.add(-lits[-1],-s[n-2][k-1])
def at_least(cnf,lits,k):at_most(cnf,[-z for z in lits],len(lits)-k)
def exactly(cnf,lits,k):at_most(cnf,lits,k);at_least(cnf,lits,k)

def equiv(cnf,q,a,b):
 cnf.add(-q,-a,b);cnf.add(-q,a,-b);cnf.add(q,-a,-b);cnf.add(q,a,b)
def and2(cnf,z,a,b):cnf.add(-z,a);cnf.add(-z,b);cnf.add(z,-a,-b)
def and3(cnf,z,a,b,c):cnf.add(-z,a);cnf.add(-z,b);cnf.add(-z,c);cnf.add(z,-a,-b,-c)
def lex_ge(cnf,A,B):
 assert len(A)==len(B) and A
 prefix=None
 for i,(a,b) in enumerate(zip(A,B)):
  cnf.add(a,-b) if prefix is None else cnf.add(-prefix,a,-b)
  if i==len(A)-1:break
  q=cnf.new();equiv(cnf,q,a,b)
  if prefix is None:prefix=q
  else:
   z=cnf.new();and2(cnf,z,prefix,q);prefix=z

def row_profiles():
 out=[]
 def rec(i,last,left,cur):
  if i==R:
   if left==0:out.append(tuple(cur))
   return
  remain=R-i
  lo=max(last,0);hi=min(C,left)
  for d in range(lo,hi+1):
   nl=left-d
   if nl<(remain-1)*d or nl>(remain-1)*C:continue
   q=cur+[d]
   ok=True
   for k,u in DELETION_UPPER.items():
    if len(q)>=k and sum(q[:k])<133-u:ok=False;break
   if ok:rec(i+1,d,nl,q)
 rec(0,0,133,[])
 return out

def build(profile):
 cnf=CNF()
 # Row degrees fix the edge count exactly at 133. Sorting degrees is WLOG.
 for r,d in enumerate(profile):exactly(cnf,[x(r,c) for c in range(C)],d)
 # Any column of degree <=4 could be deleted, leaving >=129 edges in 16x16,
 # contradicting Z(16,16,3,3)=128.
 for c in range(C):at_least(cnf,[x(r,c) for r in range(R)],5)
 # Column permutation symmetry only: every orbit has lexicographically sorted columns.
 for c in range(C-1):lex_ge(cnf,[x(r,c) for r in range(R)],[x(r,c+1) for r in range(R)])
 # For each row triple, at most two columns may contain all three rows.
 for a,b,c in combinations(range(R),3):
  ys=[]
  for j in range(C):
   y=cnf.new();ys.append(y);and3(cnf,y,x(a,j),x(b,j),x(c,j))
  at_most(cnf,ys,2)
 return cnf

def write(cnf,path,profile_id,profile):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w') as f:
  f.write('c exact Z(16,17,3,3) 133-edge decision shard\n')
  f.write(f'c row_profile_id {profile_id} row_degrees {list(profile)}\n')
  f.write('c primary x(r,c)=1+17*r+c, 0<=r<16,0<=c<17\n')
  f.write(f'p cnf {cnf.nvars} {len(cnf.clauses)}\n')
  for z in cnf.clauses:f.write(' '.join(map(str,z))+' 0\n')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--profile-id',type=int);ap.add_argument('--out',type=Path);ap.add_argument('--manifest',type=Path);ap.add_argument('--list',action='store_true');a=ap.parse_args()
 ps=row_profiles()
 if a.list:print(json.dumps([{'id':i,'row_degrees':p} for i,p in enumerate(ps)],indent=2));return
 if a.profile_id is None or a.out is None:ap.error('--profile-id and --out required')
 if not 0<=a.profile_id<len(ps):ap.error(f'profile id 0..{len(ps)-1}')
 p=ps[a.profile_id];cnf=build(p);write(cnf,a.out,a.profile_id,p)
 obj={'profile_id':a.profile_id,'row_degrees':p,'vars':cnf.nvars,'clauses':len(cnf.clauses)}
 if a.manifest:a.manifest.write_text(json.dumps(obj,indent=2)+'\n')
 print(json.dumps(obj))
if __name__=='__main__':main()
