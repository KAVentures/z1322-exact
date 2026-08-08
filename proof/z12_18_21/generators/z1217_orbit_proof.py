#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,math,os,time
from collections import Counter,defaultdict
from functools import lru_cache
from itertools import combinations,product
from math import comb,prod,gcd
import numpy as np
from scipy.optimize import linprog,milp,LinearConstraint,Bounds
from scipy.sparse import csc_matrix
V=12

def C(n,k):return comb(n,k) if 0<=k<=n else 0

def partitions(length,total,maximum,p=()):
    if length==0:
        if total==0:yield p
        return
    lo=max(0,total-maximum*(length-1));hi=min(maximum,total)
    for x in range(hi,lo-1,-1):yield from partitions(length-1,total-x,x,p+(x,))
def patterns():return tuple(p for p in partitions(17,104,12) if sum(C(x,3) for x in p)<=440)

def cells_of(fixed):
    g=defaultdict(list)
    for r in range(V):
        s=sum(((b>>r)&1)<<j for j,b in enumerate(fixed));g[s].append(r)
    return tuple(tuple(g[s]) for s in sorted(g))
@lru_cache(None)
def profiles(sizes,k):
    out=[];suf=[0]*(len(sizes)+1)
    for i in range(len(sizes)-1,-1,-1):suf[i]=suf[i+1]+sizes[i]
    def rec(i,left,cur):
        if i==len(sizes):
            if left==0:out.append(tuple(cur))
            return
        for x in range(max(0,left-suf[i+1]),min(sizes[i],left)+1):cur.append(x);rec(i+1,left-x,cur);cur.pop()
    rec(0,k,[]);return tuple(out)
def rep(cells,p):return sum(1<<r for cell,x in zip(cells,p) for r in cell[:x])
def osize(sizes,p):return prod(C(n,x) for n,x in zip(sizes,p))
def orbit_masks(cells,p):
    qs=[tuple(sum(1<<r for r in z) for z in combinations(cell,x)) for cell,x in zip(cells,p)]
    for z in product(*qs):yield sum(z)

def build(fixed,remaining,forbidden):
    cells=cells_of(fixed);sizes=tuple(map(len,cells));tos=[]
    for u in profiles(sizes,3):
        t=rep(cells,u);fm=sum((b&t)==t for b in fixed)
        if fm>2:return cells,(),(),True
        tos.append((u,fm,osize(sizes,u)))
    fc=Counter(fixed);vars=[]
    for k,need in sorted(remaining.items(),reverse=True):
        if need<=0:continue
        for p in profiles(sizes,k):
            r=rep(cells,p)
            if r in forbidden.get(k,set()):continue
            o=osize(sizes,p);up=min(need,2*o-(fc[r] if o==1 else 0)) if k>=3 else need
            if up<=0:continue
            h=tuple(prod(C(x,y) for x,y in zip(p,u)) for u,_,_ in tos)
            if any(fm==2 and q for q,(_u,fm,_o) in zip(h,tos)):continue
            vars.append((k,p,r,o,up,h))
    return cells,tuple(tos),tuple(vars),False

def model(remaining,tos,vars):
    A=[];b=[]
    for qi,(_u,fm,o) in enumerate(tos):A.append(tuple(v[5][qi] for v in vars));b.append((2-fm)*o)
    for k,n in sorted(remaining.items(),reverse=True):
        if n>0:A.append(tuple(v[0]==k for v in vars));b.append(n)
    return tuple(A),tuple(b)
def bound(A,b,lo,up,ws,Q):
    val=Q*sum(lo);cov=[0]*len(lo)
    for i,w in ws.items():
        val+=w*(b[i]-sum(A[i][j]*lo[j] for j in range(len(lo))))
        for j,a in enumerate(A[i]):cov[j]+=w*a
    for j in range(len(lo)):
        if cov[j]<Q:val+=(up[j]-lo[j])*(Q-cov[j])
    return val
def dual(marg,A,b,lo,up,need):
    ys=[max(0.,-float(x)) for x in marg]
    for Q in [10**q for q in range(3,13)]+[2**24,2**32,2**40,2**48]:
        ws={i:int(y*Q+.5) for i,y in enumerate(ys) if y>1e-13};ws={i:w for i,w in ws.items() if w>0}
        if bound(A,b,lo,up,ws,Q)<need*Q:
            g=Q
            for w in ws.values():g=gcd(g,w)
            if g>1:Q//=g;ws={i:w//g for i,w in ws.items()}
            return ws,Q
    return None
class Gen:
    def __init__(self,limit):self.limit=limit;self.o=self.i=self.d=self.br=0;self.md=0
    def lp(self,A,b,lo,up):return linprog(-np.ones(len(lo)),A_ub=csc_matrix(np.asarray(A,float)),b_ub=np.asarray(b,float),bounds=list(zip(lo,up)),method='highs',options={'presolve':True}) if lo else None
    def inner(self,A,b,vars,need,lo,up):
        self.i+=1
        if self.i>self.limit:raise RuntimeError('limit')
        if any(lo[j]>up[j] for j in range(len(lo))):return ['X',-1]
        sh=[b[x]-sum(A[x][j]*lo[j] for j in range(len(lo))) for x in range(len(A))]
        for x,z in enumerate(sh):
            if z<0:return ['X',x]
        if sum(up)<need:return ['D',[]]
        if not vars:return ['X',-2]
        r=self.lp(A,b,lo,up)
        if r is not None and r.success:
            q=dual(r.ineqlin.marginals,A,b,lo,up,need)
            if q:
                ws,Q=q;self.d+=1;return ['D',[[x,w,Q] for x,w in sorted(ws.items())]]
            fr=[(min(z-math.floor(z),math.ceil(z)-z),up[j]-lo[j],j,z) for j,z in enumerate(r.x) if lo[j]<up[j] and abs(z-round(z))>1e-7]
            if not fr:return None
            _,_,j,z=max(fr);cut=math.floor(z+1e-9)
        else:
            js=[j for j in range(len(lo)) if lo[j]<up[j]]
            if not js:raise AssertionError('bad infeasible fixed')
            j=max(js,key=lambda x:up[x]-lo[x]);cut=(lo[j]+up[j])//2
        uu=list(up);uu[j]=cut;L=self.inner(A,b,vars,need,list(lo),uu)
        if L is None:return None
        ll=list(lo);ll[j]=cut+1;R=self.inner(A,b,vars,need,ll,list(up))
        if R is None:return None
        self.br+=1;return ['I',j,cut,L,R]
    def outer(self,fixed,remaining,forbidden,depth=0):
        self.o+=1;self.md=max(self.md,depth);need=sum(max(0,n) for n in remaining.values())
        cells,tos,vars,bad=build(fixed,remaining,forbidden)
        if bad:return ['G']
        A,b=model(remaining,tos,vars);k=max(q for q,n in remaining.items() if n>0)
        cs=sorted((v for v in vars if v[0]==k),key=lambda v:v[1])
        if not cs:return ['N',k]
        lo=[0]*len(vars);up=[v[4] for v in vars]
        # First use LP for an exact rational upper certificate.  If the LP
        # relaxation survives, a short integer solve distinguishes a genuinely
        # feasible aggregate vector (branch on an actual block orbit) from an
        # integer-infeasible aggregate system (then produce a replayable split tree).
        rr=self.lp(A,b,lo,up)
        p=None
        if rr is not None and rr.success:
            dq=dual(rr.ineqlin.marginals,A,b,lo,up,need)
            if dq:
                ws,Q=dq;self.i+=1;self.d+=1;p=['D',[[x,w,Q] for x,w in sorted(ws.items())]]
            else:
                AA=csc_matrix(np.asarray(A,float));lc=LinearConstraint(AA,-np.inf,np.asarray(b,float))
                mr=milp(c=-np.ones(len(vars)),integrality=np.ones(len(vars)),bounds=Bounds(np.zeros(len(vars)),np.asarray(up,float)),constraints=lc,options={'time_limit':1.0,'mip_rel_gap':0,'presolve':True,'disp':False})
                if not (mr.x is not None and -mr.fun>=need-1e-7):
                    p=self.inner(A,b,vars,need,lo,up)
        else:
            p=self.inner(A,b,vars,need,lo,up)
        if p is not None:return ['P',p]
        prior=set(forbidden.get(k,set()));ch=[]
        for v in cs:
            _k,pr,r,*_=v;nr=dict(remaining);nr[k]-=1;nf={q:set(s) for q,s in forbidden.items()};nf[k]=set(prior)
            ch.append(self.outer(fixed+[r],nr,nf,depth+1));prior.update(orbit_masks(cells,pr))
        return ['B',k,ch]
class Verify:
    def __init__(self):self.o=self.i=self.d=self.br=0
    def inner(self,node,A,b,vars,need,lo,up):
        self.i+=1
        if any(lo[j]>up[j] for j in range(len(lo))):return
        t=node[0]
        if t=='X':
            x=node[1]
            if x==-1:assert any(lo[j]>up[j] for j in range(len(lo)))
            elif x==-2:assert not vars
            else:assert b[x]-sum(A[x][j]*lo[j] for j in range(len(lo)))<0
            return
        if t=='D':
            e=node[1];Q=1 if not e else e[0][2];ws={};last=-1
            for x,w,q in e:assert last<x<len(A) and w>0 and q==Q;last=x;ws[x]=w
            assert bound(A,b,lo,up,ws,Q)<need*Q;self.d+=1;return
        assert t=='I';j,cut,L,R=node[1:];assert lo[j]<=cut<up[j]
        uu=list(up);uu[j]=cut;self.inner(L,A,b,vars,need,list(lo),uu)
        ll=list(lo);ll[j]=cut+1;self.inner(R,A,b,vars,need,ll,list(up));self.br+=1
    def outer(self,node,fixed,remaining,forbidden):
        self.o+=1;need=sum(max(0,n) for n in remaining.values());cells,tos,vars,bad=build(fixed,remaining,forbidden)
        if node[0]=='G':assert bad;return
        assert not bad;A,b=model(remaining,tos,vars);k=max(q for q,n in remaining.items() if n>0);cs=sorted((v for v in vars if v[0]==k),key=lambda v:v[1])
        if node[0]=='N':assert node==['N',k] and not cs;return
        if node[0]=='P':self.inner(node[1],A,b,vars,need,[0]*len(vars),[v[4] for v in vars]);return
        assert node[0]=='B' and node[1]==k and len(node[2])==len(cs)>0
        prior=set(forbidden.get(k,set()))
        for z,v in zip(node[2],cs):
            _k,pr,r,*_=v;nr=dict(remaining);nr[k]-=1;nf={q:set(s) for q,s in forbidden.items()};nf[k]=set(prior)
            self.outer(z,fixed+[r],nr,nf);prior.update(orbit_masks(cells,pr))
def generate(idx,out,limit):
    ps=patterns();assert len(ps)==303;p=ps[idx];rem=dict(Counter(p));k=max(rem);first=(1<<k)-1;rem[k]-=1
    t=time.time();g=Gen(limit);tree=g.outer([first],rem,{})
    obj={'format':'Z1217-local-v1','index':idx,'pattern':p,'first':first,'tree':tree,'stats':{'outer':g.o,'inner':g.i,'duals':g.d,'branches':g.br,'maxdepth':g.md,'seconds':time.time()-t}}
    with gzip.open(out,'wt',encoding='utf8',compresslevel=9) as f:json.dump(obj,f,separators=(',',':'))
    v=Verify();v.outer(tree,[first],rem,{})
    print('DONE',idx,obj['stats'],'VERIFY',v.__dict__,'bytes',os.path.getsize(out),flush=True)
def verify(path):
    with gzip.open(path,'rt',encoding='utf8') as f:o=json.load(f)
    ps=patterns();p=ps[o['index']];assert tuple(o['pattern'])==p;rem=dict(Counter(p));k=max(rem);first=(1<<k)-1;rem[k]-=1;assert o['first']==first
    v=Verify();v.outer(o['tree'],[first],rem,{});print('VERIFIED',o['index'],v.__dict__)
if __name__=='__main__':
    ap=argparse.ArgumentParser();s=ap.add_subparsers(dest='cmd',required=True);g=s.add_parser('generate');g.add_argument('index',type=int);g.add_argument('out');g.add_argument('--limit',type=int,default=1000000);v=s.add_parser('verify');v.add_argument('path');a=ap.parse_args();generate(a.index,a.out,a.limit) if a.cmd=='generate' else verify(a.path)
