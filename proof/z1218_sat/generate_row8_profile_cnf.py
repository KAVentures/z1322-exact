#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
R,C=12,18
class CNF:
 def __init__(self):self.nvars=R*C;self.clauses=[]
 def new_var(self):self.nvars+=1;return self.nvars
 def add(self,*lits):
  s=set(lits)
  if any(-z in s for z in s):return
  self.clauses.append(sorted(s,key=lambda z:(abs(z),z<0)))
def x(r,c):return 1+r*C+c
def add(cnf,lits,guard=None):cnf.add(*(([-guard] if guard else [])+list(lits)))
def at_most(cnf,lits,k,guard=None):
 n=len(lits)
 if k<0:add(cnf,[],guard);return
 if k>=n:return
 if k==0:
  for z in lits:add(cnf,[-z],guard)
  return
 if n==1:add(cnf,[-lits[0]],guard);return
 s=[[cnf.new_var() for _ in range(k)] for _ in range(n-1)]
 add(cnf,[-lits[0],s[0][0]],guard)
 for j in range(1,k):add(cnf,[-s[0][j]],guard)
 for i in range(1,n-1):
  add(cnf,[-lits[i],s[i][0]],guard);add(cnf,[-s[i-1][0],s[i][0]],guard)
  for j in range(1,k):
   add(cnf,[-lits[i],-s[i-1][j-1],s[i][j]],guard);add(cnf,[-s[i-1][j],s[i][j]],guard)
  add(cnf,[-lits[i],-s[i-1][k-1]],guard)
 add(cnf,[-lits[-1],-s[n-2][k-1]],guard)
def at_least(cnf,lits,k,guard=None):at_most(cnf,[-z for z in lits],len(lits)-k,guard)
def exactly(cnf,lits,k,guard=None):at_most(cnf,lits,k,guard);at_least(cnf,lits,k,guard)
def enum_profiles():
 out=[]
 def rec(n,mn,total,arr):
  if n==0:
   if total==0 and sum(comb(d,3) for d in arr)<=330:out.append(tuple(arr))
   return
  for d in range(mn,12):
   if d*n>total:break
   if total-d<d*(n-1) or total-d>11*(n-1):continue
   rec(n-1,d,total-d,arr+[d])
 rec(18,5,101,[]);return out
def submultisets(cnt,total=8):
 sizes=sorted(cnt);out=[]
 def rec(i,left,cur):
  if i==len(sizes):
   if left==0:out.append(dict(cur))
   return
  d=sizes[i]
  for k in range(min(cnt[d],left)+1):
   if k:cur[d]=k
   elif d in cur:del cur[d]
   rec(i+1,left-k,cur)
  cur.pop(d,None)
 rec(0,total,{});return out
def cases():
 out=[]
 for p in enum_profiles():
  cnt=Counter(p)
  for sel in submultisets(cnt):
   if sum(k*comb(d,2) for d,k in sel.items())<=110:
    selected=sorted((d for d,k in sel.items() for _ in range(k)),reverse=True)
    rem=cnt.copy()
    for d in selected:rem[d]-=1
    unselected=sorted((d for d,k in rem.items() for _ in range(k)),reverse=True)
    out.append({'profile':list(p),'selected':selected,'unselected':unselected})
 return out
def equiv(cnf,q,a,b):
 cnf.add(-q,-a,b);cnf.add(-q,a,-b);cnf.add(q,-a,-b);cnf.add(q,a,b)
def and2(cnf,z,a,b):
 cnf.add(-z,a);cnf.add(-z,b);cnf.add(z,-a,-b)
def conditional_lex_ge(cnf,A,B,g):
 prefix=None
 for i,(a,b) in enumerate(zip(A,B)):
  cnf.add(-g,a,-b) if prefix is None else cnf.add(-g,-prefix,a,-b)
  if i==len(A)-1:break
  q=cnf.new_var();equiv(cnf,q,a,b)
  if prefix is None:prefix=q
  else:
   z=cnf.new_var();and2(cnf,z,prefix,q);prefix=z
def build():
 cnf=CNF()
 for c in range(C):cnf.add(x(0,c) if c<8 else -x(0,c))
 exactly(cnf,[x(r,c) for r in range(1,R) for c in range(C)],101)
 for r in range(1,R):at_least(cnf,[x(r,c) for c in range(C)],8)
 for r,s in combinations(range(1,R),2):
  ys=[]
  for c in range(8):
   y=cnf.new_var();ys.append(y)
   cnf.add(-y,x(r,c));cnf.add(-y,x(s,c));cnf.add(y,-x(r,c),-x(s,c))
  at_most(cnf,ys,2)
 cs=cases();selectors=[cnf.new_var() for _ in cs];exactly(cnf,selectors,1)
 for case,g in zip(cs,selectors):
  degs=case['selected']+case['unselected']
  for c,d in enumerate(degs):exactly(cnf,[x(r,c) for r in range(1,R)],d,g)
  d=case['selected'][0]
  for r in range(1,R):add(cnf,[x(r,0) if r<=d else -x(r,0)],g)
  for lo,hi in [(0,8),(8,18)]:
   j=lo
   while j<hi:
    k=j+1
    while k<hi and degs[k]==degs[j]:k+=1
    for c in range(j,k-1):conditional_lex_ge(cnf,[x(r,c) for r in range(1,R)],[x(r,c+1) for r in range(1,R)],g)
    j=k
 for rs in combinations(range(R),3):
  for cs3 in combinations(range(C),3):cnf.add(*[-x(r,c) for r in rs for c in cs3])
 return cnf,cs
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--cases',type=Path);a=ap.parse_args()
 cnf,cs=build()
 with a.out.open('w') as f:
  f.write(f'c strengthened profile-selector row8, cases={len(cs)}\n')
  f.write(f'p cnf {cnf.nvars} {len(cnf.clauses)}\n')
  for cl in cnf.clauses:f.write(' '.join(map(str,cl))+' 0\n')
 if a.cases:a.cases.write_text(json.dumps(cs,indent=2)+'\n')
 print('cases',len(cs),'vars',cnf.nvars,'clauses',len(cnf.clauses))
if __name__=='__main__':main()
