import itertools,json,math,sys,os
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix,csc_matrix
from fractions import Fraction
sols=json.load(open('/mnt/data/system6_orbit_solutions.json'))[2]
profiles={
 'P0':{6:8,7:3},
 'PA':{5:1,6:6,7:4},
 'PB':{5:2,6:4,7:5},
 'PC':{5:3,6:2,7:6},
}
OUT='/mnt/data/completion_local_certs';os.makedirs(OUT,exist_ok=True)
PTS=range(13);r=12
def M(xs):return sum(1<<x for x in xs)
Tmask=[M(t) for t in itertools.combinations(PTS,3)];Pmask=[M(p) for p in itertools.combinations(PTS,2)]
for si,s5 in enumerate(sols['solutions5']):
 fixed=[M(B+[r]) for B in sols['size6']]+[M(B+[r]) for B in s5]
 assert sum(x.bit_count()==7 for x in fixed)==3 and sum(x.bit_count()==6 for x in fixed)==8
 for pname,counts in profiles.items():
  active=sorted(counts);cands=[];cdeg=[]
  for d in active:
   for B in itertools.combinations(range(12),d):cands.append(M(B));cdeg.append(d)
  rhs=[]
  for t in Tmask:rhs.append(2-sum((f&t)==t for f in fixed))
  for x in PTS:rhs.append(132-sum(math.comb(f.bit_count()-1,2) for f in fixed if f>>x&1))
  for p in Pmask:rhs.append(22-sum((f.bit_count()-2) for f in fixed if (f&p)==p))
  assert min(rhs)>=0
  na=len(rhs);nb=len(active);nbase=na+nb;zidx=nbase
  A=lil_matrix((len(cands)+2,nbase+1),dtype=float);b=np.zeros(len(cands)+2)
  for j,(B,d) in enumerate(zip(cands,cdeg)):
   for i,t in enumerate(Tmask):
    if B&t==t:A[j,i]=-1
   for x in PTS:
    if B>>x&1:A[j,286+x]=-math.comb(d-1,2)
   for i,p in enumerate(Pmask):
    if B&p==p:A[j,299+i]=-(d-2)
   A[j,na+active.index(d)]=-1;A[j,zidx]=1
  for i in range(na):A[len(cands),i]=1
  b[len(cands)]=1
  EPS=.01
  for i,x in enumerate(rhs):A[len(cands)+1,i]=x
  for i,d in enumerate(active):A[len(cands)+1,na+i]=counts[d]
  b[len(cands)+1]=-EPS
  obj=np.zeros(nbase+1);obj[zidx]=-1
  res=linprog(obj,A_ub=csc_matrix(A),b_ub=b,bounds=[(0,None)]*na+[(None,None)]*nb+[(None,None)],method='highs-ds',options={'presolve':False})
  print(si,pname,'status',res.status,'z',None if res.x is None else res.x[zidx],flush=True);assert res.status==0
  for lim in [100,300,1000,3000,10000,100000,1000000]:
   vals=[Fraction(float(x)).limit_denominator(lim) for x in res.x[:nbase]];al=vals[:na];be=vals[na:]
   value=sum(x*y for x,y in zip(al,rhs))+sum(be[i]*counts[d] for i,d in enumerate(active));least=None
   for B,d in zip(cands,cdeg):
    v=be[active.index(d)]
    v+=sum(al[i] for i,t in enumerate(Tmask) if B&t==t)
    v+=math.comb(d-1,2)*sum(al[286+x] for x in PTS if B>>x&1)
    v+=(d-2)*sum(al[299+i] for i,p in enumerate(Pmask) if B&p==p)
    least=v if least is None or v<least else least
    if v<0:break
   if value<0 and least>=0:
    out={'profile':pname,'solution_index':si,'active_degrees':active,'remaining_counts':counts,
      'fixed_blocks':[[x for x in PTS if f>>x&1] for f in fixed],
      'alpha':[[x.numerator,x.denominator] for x in al],'beta':[[x.numerator,x.denominator] for x in be],
      'rhs':[value.numerator,value.denominator],'min_coefficient':[least.numerator,least.denominator],'den_limit':lim}
    fn=f'{OUT}/{pname}_s{si}.json';json.dump(out,open(fn,'w'),separators=(',',':'));print(' wrote',fn,lim,flush=True);break
  else:raise RuntimeError('no cert')
