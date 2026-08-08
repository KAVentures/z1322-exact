#!/usr/bin/env python3
from __future__ import annotations
import argparse,gzip,json,math,os,time
from collections import Counter,defaultdict
from functools import lru_cache
from fractions import Fraction
from itertools import combinations,product
from math import comb,prod,gcd
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix

V=11
# (remaining type counts, initially fixed (marked,mask))
CASES={
 'A':({(1,5):7,(0,6):10},[(1,(1<<6)-1)]),
 'B':({(1,5):8,(0,6):9},[(0,(1<<7)-1)]),
}

def C(n,k):return comb(n,k) if 0<=k<=n else 0

def cell_partition(fixed):
    g=defaultdict(list)
    for r in range(V):
        s=0
        for j,(_m,b) in enumerate(fixed):
            if b>>r&1:s|=1<<j
        g[s].append(r)
    return tuple(tuple(g[s]) for s in sorted(g))

@lru_cache(None)
def profiles(sizes,k):
    out=[]; suf=[0]*(len(sizes)+1)
    for i in range(len(sizes)-1,-1,-1):suf[i]=suf[i+1]+sizes[i]
    def rec(i,left,cur):
        if i==len(sizes):
            if left==0:out.append(tuple(cur))
            return
        for x in range(max(0,left-suf[i+1]),min(sizes[i],left)+1):
            cur.append(x);rec(i+1,left-x,cur);cur.pop()
    rec(0,k,[]);return tuple(out)

def rep(cells,p):return sum(1<<r for cell,x in zip(cells,p) for r in cell[:x])
def osize(sizes,p):return prod(C(n,x) for n,x in zip(sizes,p))
def orbit_masks(cells,p):
    qs=[]
    for cell,x in zip(cells,p):qs.append(tuple(sum(1<<r for r in z) for z in combinations(cell,x)))
    for z in product(*qs):yield sum(z)

def build(fixed,remaining,forbidden):
    cells=cell_partition(fixed);sizes=tuple(map(len,cells))
    tos=[]
    for u in profiles(sizes,3):
        t=rep(cells,u);fm=sum((b&t)==t for _m,b in fixed)
        if fm>2:return cells,(),(),(),True
        tos.append((u,fm,osize(sizes,u)))
    pos=[]
    for u in profiles(sizes,2):
        t=rep(cells,u);fm=sum(m and (b&t)==t for m,b in fixed)
        if fm>2:return cells,(),(),(),True
        pos.append((u,fm,osize(sizes,u)))
    fc=Counter(b for _m,b in fixed);vars=[]
    for typ,needed in sorted(remaining.items(),key=lambda q:(-q[0][1],-q[0][0])):
        if needed<=0:continue
        mark,k=typ
        for p in profiles(sizes,k):
            r=rep(cells,p)
            if r in forbidden.get(typ,set()):continue
            o=osize(sizes,p);up=min(needed,2*o-(fc[r] if o==1 else 0))
            if up<=0:continue
            ht=tuple(prod(C(x,y) for x,y in zip(p,u)) for u,_,_ in tos)
            hp=tuple(prod(C(x,y) for x,y in zip(p,u)) for u,_,_ in pos)
            if any(fm==2 and h for h,(_u,fm,_o) in zip(ht,tos)):continue
            if mark and any(fm==2 and h for h,(_u,fm,_o) in zip(hp,pos)):continue
            vars.append((typ,p,r,o,up,ht,hp))
    return cells,tuple(tos),tuple(pos),tuple(vars),False

def model(fixed,remaining,cells,tos,pos,vars):
    A=[];b=[]
    for qi,(_u,fm,o) in enumerate(tos):A.append(tuple(v[5][qi] for v in vars));b.append((2-fm)*o)
    for qi,(_u,fm,o) in enumerate(pos):A.append(tuple(v[6][qi] if v[0][0] else 0 for v in vars));b.append((2-fm)*o)
    for typ,n in sorted(remaining.items(),key=lambda q:(-q[0][1],-q[0][0])):
        if n>0:A.append(tuple(v[0]==typ for v in vars));b.append(n)
    need=sum(max(0,n) for n in remaining.values())
    for ci,cell in enumerate(cells):
        r=cell[0];fd=sum((bb>>r)&1 for _m,bb in fixed)
        A.append(tuple(len(cell)-v[1][ci] for v in vars));b.append(len(cell)*(need-8+fd))
    return tuple(A),tuple(b)

def bound(A,b,lo,up,ws,Q):
    val=Q*sum(lo);cov=[0]*len(lo)
    for i,w in ws.items():
        val+=w*(b[i]-sum(A[i][j]*lo[j] for j in range(len(lo))))
        for j,a in enumerate(A[i]):cov[j]+=w*a
    for j in range(len(lo)):
        if cov[j]<Q:val+=(up[j]-lo[j])*(Q-cov[j])
    return val

def rational_dual(marg,A,b,lo,up,need):
    ys=[max(0.0,-float(x)) for x in marg]
    for Q in [10**q for q in range(3,13)]+[2**24,2**32,2**40,2**48]:
        ws={i:int(v*Q+.5) for i,v in enumerate(ys) if v>1e-13};ws={i:w for i,w in ws.items() if w>0}
        if bound(A,b,lo,up,ws,Q)<need*Q:
            g=Q
            for w in ws.values():g=gcd(g,w)
            if g>1:Q//=g;ws={i:w//g for i,w in ws.items()}
            return ws,Q
    return None

class Gen:
    def __init__(self,limit):self.limit=limit;self.outer=self.inner=self.duals=self.branches=0;self.maxdepth=0;self.start=time.time()
    def lp(self,A,b,lo,up):
        if not lo:return None
        return linprog(-np.ones(len(lo)),A_ub=csc_matrix(np.asarray(A,float)),b_ub=np.asarray(b,float),bounds=list(zip(lo,up)),method='highs',options={'presolve':True})
    def inner_proof(self,A,b,vars,need,lo,up):
        self.inner+=1
        if self.inner>self.limit:raise RuntimeError('node limit')
        if any(lo[j]>up[j] for j in range(len(lo))):return ['X',-1]
        shifted=[b[i]-sum(A[i][j]*lo[j] for j in range(len(lo))) for i in range(len(A))]
        for i,x in enumerate(shifted):
            if x<0:return ['X',i]
        if sum(up)<need:return ['D',[]]
        if not vars:return ['X',-2]
        r=self.lp(A,b,lo,up)
        if r is not None and r.success:
            d=rational_dual(r.ineqlin.marginals,A,b,lo,up,need)
            if d:
                ws,Q=d;self.duals+=1;return ['D',[[i,w,Q] for i,w in sorted(ws.items())]]
            frac=[(min(z-math.floor(z),math.ceil(z)-z),up[j]-lo[j],j,z) for j,z in enumerate(r.x) if lo[j]<up[j] and abs(z-round(z))>1e-7]
            if not frac:return None
            _,_,j,z=max(frac);q=math.floor(z+1e-9)
        else:
            js=[j for j in range(len(lo)) if lo[j]<up[j]]
            if not js:raise AssertionError('infeasible fixed assignment without violated row')
            j=max(js,key=lambda x:up[x]-lo[x]);q=(lo[j]+up[j])//2
        ul=list(up);ul[j]=q;L=self.inner_proof(A,b,vars,need,list(lo),ul)
        if L is None:return None
        lr=list(lo);lr[j]=q+1;R=self.inner_proof(A,b,vars,need,lr,list(up))
        if R is None:return None
        self.branches+=1;return ['I',j,q,L,R]
    def outer_proof(self,fixed,remaining,forbidden,depth=0):
        self.outer+=1;self.maxdepth=max(self.maxdepth,depth)
        if self.outer%25==0:print('outer',self.outer,'inner',self.inner,'depth',depth,'sec',round(time.time()-self.start,1),flush=True)
        need=sum(max(0,n) for n in remaining.values());assert need>0
        cells,tos,pos,vars,bad=build(fixed,remaining,forbidden)
        if bad:return ['G']
        A,b=model(fixed,remaining,cells,tos,pos,vars)
        typ=max((t for t,n in remaining.items() if n>0),key=lambda t:(t[1],t[0]))
        cands=sorted((v for v in vars if v[0]==typ),key=lambda v:v[1])
        if not cands:return ['N',[typ[0],typ[1]]]
        p=self.inner_proof(A,b,vars,need,[0]*len(vars),[v[4] for v in vars])
        if p is not None:return ['P',p]
        prior=set(forbidden.get(typ,set()));children=[]
        for v in cands:
            _t,pr,r,*_=v;nr=dict(remaining);nr[typ]-=1
            nf={q:set(s) for q,s in forbidden.items()};nf[typ]=set(prior)
            children.append(self.outer_proof(fixed+[(typ[0],r)],nr,nf,depth+1))
            prior.update(orbit_masks(cells,pr))
        return ['B',[typ[0],typ[1]],children]

class Verify:
    def __init__(self):self.outer=self.inner=self.duals=self.branches=0
    def inner_check(self,node,A,b,vars,need,lo,up):
        self.inner+=1
        if any(lo[j]>up[j] for j in range(len(lo))):return
        tag=node[0]
        if tag=='X':
            i=node[1]
            if i==-1:assert any(lo[j]>up[j] for j in range(len(lo)))
            elif i==-2:assert not vars
            else:assert 0<=i<len(A) and b[i]-sum(A[i][j]*lo[j] for j in range(len(lo)))<0
            return
        if tag=='D':
            es=node[1];Q=1 if not es else es[0][2];ws={};last=-1
            for i,w,q in es:assert last<i<len(A) and w>0 and q==Q;last=i;ws[i]=w
            assert bound(A,b,lo,up,ws,Q)<need*Q
            self.duals+=1;return
        assert tag=='I' and len(node)==5
        j,q,L,R=node[1:];assert 0<=j<len(lo) and lo[j]<=q<up[j]
        ul=list(up);ul[j]=q;self.inner_check(L,A,b,vars,need,list(lo),ul)
        lr=list(lo);lr[j]=q+1;self.inner_check(R,A,b,vars,need,lr,list(up));self.branches+=1
    def outer_check(self,node,fixed,remaining,forbidden):
        self.outer+=1;need=sum(max(0,n) for n in remaining.values());assert need>0
        cells,tos,pos,vars,bad=build(fixed,remaining,forbidden)
        if node[0]=='G':assert bad;return
        assert not bad;A,b=model(fixed,remaining,cells,tos,pos,vars)
        typ=max((t for t,n in remaining.items() if n>0),key=lambda t:(t[1],t[0]))
        cands=sorted((v for v in vars if v[0]==typ),key=lambda v:v[1])
        if node[0]=='N':assert node==['N',[typ[0],typ[1]]] and not cands;return
        if node[0]=='P':self.inner_check(node[1],A,b,vars,need,[0]*len(vars),[v[4] for v in vars]);return
        assert node[0]=='B' and node[1]==[typ[0],typ[1]] and len(node[2])==len(cands)>0
        prior=set(forbidden.get(typ,set()))
        for ch,v in zip(node[2],cands):
            _t,pr,r,*_=v;nr=dict(remaining);nr[typ]-=1
            nf={q:set(s) for q,s in forbidden.items()};nf[typ]=set(prior)
            self.outer_check(ch,fixed+[(typ[0],r)],nr,nf)
            prior.update(orbit_masks(cells,pr))

def generate(case,out,limit):
    rem,fixed=CASES[case];g=Gen(limit);tree=g.outer_proof(list(fixed),dict(rem),{})
    p={'format':'Z1218-row8-orbit-v2','case':case,'tree':tree,'stats':{'outer':g.outer,'inner':g.inner,'duals':g.duals,'branches':g.branches,'maxdepth':g.maxdepth,'seconds':time.time()-g.start}}
    with gzip.open(out,'wt',encoding='utf8',compresslevel=9) as f:json.dump(p,f,separators=(',',':'))
    print('DONE',p['stats'],'bytes',os.path.getsize(out),flush=True)
    v=Verify();v.outer_check(tree,list(fixed),dict(rem),{});print('VERIFIED',v.__dict__,flush=True)

def verify(path):
    with gzip.open(path,'rt',encoding='utf8') as f:p=json.load(f)
    assert p['format']=='Z1218-row8-orbit-v2';rem,fixed=CASES[p['case']]
    v=Verify();v.outer_check(p['tree'],list(fixed),dict(rem),{});print('VERIFIED',p['case'],v.__dict__)

if __name__=='__main__':
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True)
    g=sp.add_parser('generate');g.add_argument('case',choices=CASES);g.add_argument('out');g.add_argument('--limit',type=int,default=1000000)
    v=sp.add_parser('verify');v.add_argument('path')
    a=ap.parse_args();generate(a.case,a.out,a.limit) if a.cmd=='generate' else verify(a.path)
