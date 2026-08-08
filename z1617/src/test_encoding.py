#!/usr/bin/env python3
"""Exhaustive small-instance semantic tests for the trusted CNF primitives."""
from itertools import product
from generate_cnf import CNF,at_most,at_least,exactly,lex_ge,and3

def dpll(clauses,assign):
 while True:
  changed=False;reduced=[]
  for clause in clauses:
   undec=[];sat=False
   for lit in clause:
    v=abs(lit)
    if v in assign:
     if assign[v]==(lit>0):sat=True;break
    else:undec.append(lit)
   if sat:continue
   if not undec:return False
   if len(undec)==1:
    lit=undec[0];v=abs(lit);z=lit>0
    if v in assign and assign[v]!=z:return False
    if v not in assign:assign[v]=z;changed=True
   reduced.append(undec)
  clauses=reduced
  if not changed:break
 if not clauses:return True
 v=abs(clauses[0][0])
 for z in (False,True):
  q=dict(assign);q[v]=z
  if dpll(clauses,q):return True
 return False

def sat(cnf,bits):return dpll([list(c) for c in cnf.clauses],{i+1:bool(z) for i,z in enumerate(bits)})
for n in range(1,8):
 for k in range(n+1):
  for name,fn,want in [('at_most',at_most,lambda s,k=k:s<=k),('at_least',at_least,lambda s,k=k:s>=k),('exactly',exactly,lambda s,k=k:s==k)]:
   c=CNF();c.nvars=n;fn(c,list(range(1,n+1)),k)
   for bits in product([0,1],repeat=n):assert sat(c,bits)==want(sum(bits)),(name,n,k,bits)
for n in range(1,7):
 c=CNF();c.nvars=2*n;lex_ge(c,list(range(1,n+1)),list(range(n+1,2*n+1)))
 for A in product([0,1],repeat=n):
  for B in product([0,1],repeat=n):assert sat(c,A+B)==(A>=B),(n,A,B)
for bits in product([0,1],repeat=3):
 c=CNF();c.nvars=4;and3(c,4,1,2,3)
 for y in (0,1):assert sat(c,bits+(y,))==(y==int(all(bits)))
print('PASS: cardinality, lexicographic, and conjunction encodings')
