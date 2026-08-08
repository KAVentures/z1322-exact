#!/usr/bin/env python3
from generate_cnf import row_profiles,DELETION_UPPER,R,C
ps=row_profiles()
assert len(ps)==18,len(ps)
assert len(set(ps))==18
for p in ps:
 assert len(p)==R and tuple(sorted(p))==p and sum(p)==133
 for k,u in DELETION_UPPER.items():assert sum(p[:k])>=133-u
# Independent brute recursion over nondecreasing compositions, then filter.
allp=[]
def rec(i,last,left,cur):
 if i==R:
  if left==0 and all(sum(cur[:k])>=133-u for k,u in DELETION_UPPER.items()):allp.append(tuple(cur))
  return
 for d in range(last,C+1):
  if d>left:break
  rem=R-i-1
  if left-d<rem*d or left-d>rem*C:continue
  rec(i+1,d,left-d,cur+[d])
rec(0,0,133,[])
assert allp==ps,(len(allp),len(ps))
print('PASS: 18 row-degree profiles exhaust every hypothetical 133-edge matrix')
