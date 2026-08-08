#!/usr/bin/env python3
from itertools import combinations
from math import comb
from pathlib import Path
import argparse,json,time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix,hstack,vstack
ROOT=Path(__file__).resolve().parent

def enum_hist(n,e,lo,hi,m):
 out=[];c=[0]*(m+1)
 def rec(d,leftn,lefts,tc):
  if d>hi:
   if leftn==0 and lefts==0 and tc<=2*comb(m,3):out.append(tuple(c))
   return
  for z in range(leftn+1):
   if d*z>lefts:break
   nt=tc+z*comb(d,3)
   if nt>2*comb(m,3):break
   c[d]=z;rec(d+1,leftn-z,lefts-d*z,nt)
  c[d]=0
 rec(lo,n,e,0);return out

def degrees(h):return tuple(d for d,z in enumerate(h) for _ in range(z))

class LP:
 def __init__(self,h,f):
  self.m=13;self.h=h;self.f=f;self.F=(1<<f)-1;rem=list(h);rem[f]-=1;self.rem=rem
  self.active=[d for d,z in enumerate(rem) if z];m=self.m
  self.blocks=[]
  for d,z in enumerate(rem):
   if z:
    for B in combinations(range(m),d):self.blocks.append((d,B,sum(1<<x for x in B)))
  self.tr=list(combinations(range(m),3));self.pa=list(combinations(range(m),2));ri=[];ci=[];da=[];b=[];r=0
  for T in self.tr:
   tm=sum(1<<x for x in T)
   for j,(_,_,bm) in enumerate(self.blocks):
    if bm&tm==tm:ri.append(r);ci.append(j);da.append(1)
   b.append(2-int(self.F&tm==tm));r+=1
  for x in range(m):
   for j,(d,_,bm) in enumerate(self.blocks):
    if bm>>x&1:ri.append(r);ci.append(j);da.append(comb(d-1,2))
   b.append(132-(comb(f-1,2) if self.F>>x&1 else 0));r+=1
  for P in self.pa:
   pm=(1<<P[0])|(1<<P[1])
   for j,(d,_,bm) in enumerate(self.blocks):
    if bm&pm==pm:ri.append(r);ci.append(j);da.append(d-2)
   b.append(22-((f-2) if self.F&pm==pm else 0));r+=1
  self.thresholds=sorted(self.active)
  for t in self.thresholds:
   for P in self.pa:
    pm=(1<<P[0])|(1<<P[1]);cap=22-((f-2) if self.F&pm==pm else 0)
    for j,(d,_,bm) in enumerate(self.blocks):
     if d>=t and bm&pm==pm:ri.append(r);ci.append(j);da.append(1)
    b.append(cap//(t-2));r+=1
  self.A=csc_matrix((np.array(da,float),(np.array(ri),np.array(ci))),shape=(r,len(self.blocks)));self.b=np.array(b,float)
  eri=[];eci=[];eda=[];e=[];labels=[];rr=0
  for d in self.active:
   labels.append(['degree',d])
   for j,(dd,_,_) in enumerate(self.blocks):
    if dd==d:eri.append(rr);eci.append(j);eda.append(1)
   e.append(rem[d]);rr+=1
  for x in range(m):
   labels.append(['row',x])
   for j,(_,_,bm) in enumerate(self.blocks):
    if bm>>x&1:eri.append(rr);eci.append(j);eda.append(1)
   e.append(9-int(self.F>>x&1));rr+=1
  self.labels=labels;self.E=csc_matrix((np.array(eda,float),(np.array(eri),np.array(eci))),shape=(rr,len(self.blocks)));self.e=np.array(e,float)
 def dual(self,tl):
  p=self.A.shape[0];q=self.E.shape[0];coeff=hstack([-self.A.T,-self.E.T,self.E.T],format='csc');Aub=vstack([coeff,csc_matrix(np.ones((1,p+2*q)))],format='csc')
  return linprog(np.r_[self.b,self.e,-self.e],A_ub=Aub,b_ub=np.r_[np.zeros(len(self.blocks)),1.],bounds=(0,None),method='highs',options={'presolve':True,'time_limit':tl})
 def cert(self,res):
  if not res.success or res.fun is None or res.fun>=-1e-10:return None
  p=self.A.shape[0];q=self.E.shape[0];z=res.x;Ai=self.A.astype(np.int64);Ei=self.E.astype(np.int64)
  for Q in (10**3,10**4,10**5,10**6,10**7,10**8,10**9):
   zz=np.rint(z*Q).astype(object);a=np.array(zz[:p],dtype=np.int64);be=np.array(zz[p:p+q],dtype=np.int64)-np.array(zz[p+q:],dtype=np.int64)
   co=np.asarray(Ai.T.dot(a)+Ei.T.dot(be),dtype=np.int64).ravel();rhs=sum(int(self.b[i])*int(a[i]) for i in range(p))+sum(int(self.e[i])*int(be[i]) for i in range(q))
   if min(co,default=0)>=0 and rhs<0:return {'alpha':[int(x) for x in a],'beta':[int(x) for x in be],'rhs':int(rhs),'mincoef':int(min(co,default=0)),'fixed_degree':self.f,'thresholds':self.thresholds,'labels':self.labels,'Q':Q}
  return None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);ap.add_argument('--end',type=int);ap.add_argument('--time',type=float,default=30);a=ap.parse_args();hs=enum_hist(18,117,5,13,13);end=min(len(hs),a.end or len(hs));out=[]
 print('profiles',len(hs),flush=True)
 for i in range(a.start,end):
  h=hs[i];act=[d for d,z in enumerate(h) if z];act.sort(key=lambda d:(h[d],-abs(d-6),d));item={'index':i,'degrees':degrees(h),'trials':[],'excluded':False}
  for f in act:
   t=time.time();lp=LP(h,f);r=lp.dual(a.time);c=lp.cert(r);tr={'f':f,'status':int(r.status),'fun':float(r.fun) if r.fun is not None else None,'exact':c is not None,'seconds':time.time()-t,'variables':len(lp.blocks)};item['trials'].append(tr)
   if c:
    (ROOT/'certificates'/f'p{i:03d}_f{f}.json').write_text(json.dumps({'m':13,'n':18,'e':117,'hist':h,'cert':c},indent=2)+'\n');item['excluded']=True;break
  print(json.dumps(item),flush=True);out.append(item)
 (ROOT/'reports'/f'screen_{a.start}_{end}.json').write_text(json.dumps(out,indent=2)+'\n');print('summary',sum(x['excluded'] for x in out),len(out),flush=True)
if __name__=='__main__':main()
