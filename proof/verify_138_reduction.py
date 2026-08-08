#!/usr/bin/env python3
from itertools import combinations
from fractions import Fraction
from math import comb
from pathlib import Path
import json,sys,contextlib,io
ROOT=Path(__file__).resolve().parent;PTS=range(13)
TR=list(combinations(PTS,3));PA=list(combinations(PTS,2));TID={t:i for i,t in enumerate(TR)};PID={p:i for i,p in enumerate(PA)}
def F(q):return Fraction(q[0],q[1])
def verify(path):
 d=json.loads(path.read_text());counts={int(k):int(v) for k,v in d['counts'].items()};f=d['fixed_degree'];fixed=set(d['fixed_block']);counts[f]-=1;active=d['active_degrees']
 al=list(map(F,d['alpha']));be=list(map(F,d['beta']));assert len(al)==377 and all(x>=0 for x in al)
 rhs=[2-int(set(t)<=fixed) for t in TR]
 rhs += [132-(comb(f-1,2) if r in fixed else 0) for r in PTS]
 rhs += [22-((f-2) if set(p)<=fixed else 0) for p in PA]
 value=sum(x*y for x,y in zip(al,rhs))+sum(be[i]*counts[deg] for i,deg in enumerate(active));assert value==F(d['rhs'])<0
 least=None;nvars=0
 for i,deg in enumerate(active):
  for B in combinations(PTS,deg):
   val=be[i]
   val+=sum(al[TID[t]] for t in combinations(B,3))
   val+=comb(deg-1,2)*sum(al[286+r] for r in B)
   val+=(deg-2)*sum(al[299+PID[p]] for p in combinations(B,2))
   assert val>=0,(path,B,val)
   if least is None or val<least:least=val
   nvars+=1
 assert least==F(d['min_coefficient'])
 full={deg:c+(1 if deg==f else 0) for deg,c in counts.items() if c+(1 if deg==f else 0)}
 return tuple(full.get(i,0) for i in range(14)),nvars
sys.path.insert(0,str(ROOT))
with contextlib.redirect_stdout(io.StringIO()):import enumerate138
profiles=[tuple(c) for c,inc,s,pen in enumerate138.sol];surv={0,1,3,6,7,11};expected={profiles[i] for i in range(83) if i not in surv}
got=[];nv=0
for k,p in enumerate(sorted((ROOT/'certs138').glob('p*.json')),1):
 q,n=verify(p);got.append(q);nv+=n
 if k%10==0:print('checked',k,flush=True)
assert len(got)==77 and len(set(got))==77 and set(got)==expected
remaining=[{d:n for d,n in enumerate(profiles[i]) if n} for i in sorted(surv)]
# Exact elementary exclusion of profile 6^18 7^3 9^1 (index 11).
slack=2*comb(13,3)-(18*comb(6,3)+3*comb(7,3)+comb(9,3))
assert slack==23 and 3*slack==69
assert (69-(9*4+4*2))//5==5
outside=[(a,b) for a in range(19) for b in range(4) if 2*a+3*b==26]
assert outside==[(10,2),(13,0)]
assert 5*13>12*5 and 5*10>12*5-6*2
inside=[(a,b) for a in range(19) for b in range(4) if 2*a+3*b==20]
assert inside==[(7,2),(10,0)]
assert 5*10>8*3+4*5
assert 9-(5-4)>=8 and 3*2==6<8
excluded_human={6:18,7:3,9:1}
assert remaining[-1]==excluded_human
final_remaining=remaining[:-1]
assert final_remaining==[
 {6:16,7:6},
 {5:1,6:14,7:7},
 {5:2,6:12,7:8},
 {4:1,6:13,7:8},
 {5:3,6:10,7:9},
]
report={'status':'PASS','profiles_138':83,'rationally_excluded':77,
 'human_excluded':[excluded_human], 'checked_block_variables':nv,
 'unresolved_profiles':final_remaining,
 'conclusion':'The 138-edge existence question is reduced exactly to five degree profiles.'}
(ROOT/'reports/verify_138_reduction_report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
