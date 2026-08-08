#!/usr/bin/env python3
"""Standard-library exact verifier for the Z(12,17;3,3)=103,
Z(12,18;3,3)=108, and Z(12,19;3,3)=114 package.

Trusted base: Python 3 standard library plus this file.  No LP/MILP/SAT solver,
floating point arithmetic, or generator output is trusted.
"""
from __future__ import annotations
import argparse,csv,gzip,json,os,sys,time,subprocess
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
from functools import lru_cache
from itertools import combinations,product
from math import comb,prod
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def C(n,k):return comb(n,k) if 0<=k<=n else 0

def gen_partitions(length,total,maximum,prefix=()):
    if length==0:
        if total==0:yield prefix
        return
    lo=max(0,total-maximum*(length-1));hi=min(maximum,total)
    for x in range(hi,lo-1,-1):yield from gen_partitions(length-1,total-x,x,prefix+(x,))
def z1217_patterns():return tuple(p for p in gen_partitions(17,104,12) if sum(C(x,3) for x in p)<=440)

@lru_cache(None)
def profiles(sizes,k):
    out=[];suf=[0]*(len(sizes)+1)
    for i in range(len(sizes)-1,-1,-1):suf[i]=suf[i+1]+sizes[i]
    def rec(i,left,cur):
        if i==len(sizes):
            if left==0:out.append(tuple(cur))
            return
        for x in range(max(0,left-suf[i+1]),min(sizes[i],left)+1):
            cur.append(x);rec(i+1,left-x,cur);cur.pop()
    rec(0,k,[]);return tuple(out)
def representative(cells,p):return sum(1<<r for cell,x in zip(cells,p) for r in cell[:x])
def orbit_size(sizes,p):return prod(C(n,x) for n,x in zip(sizes,p))
def orbit_masks(cells,p):
    choices=[tuple(sum(1<<r for r in q) for q in combinations(cell,x)) for cell,x in zip(cells,p)]
    for q in product(*choices):yield sum(q)

@lru_cache(None)
def profile_data3(sizes,k):
    us=profiles(sizes,3)
    return tuple((p,orbit_size(sizes,p),tuple(prod(C(x,y) for x,y in zip(p,u)) for u in us)) for p in profiles(sizes,k))

@lru_cache(None)
def profile_data32(sizes,k):
    us3=profiles(sizes,3);us2=profiles(sizes,2)
    return tuple((p,orbit_size(sizes,p),
                  tuple(prod(C(x,y) for x,y in zip(p,u)) for u in us3),
                  tuple(prod(C(x,y) for x,y in zip(p,u)) for u in us2))
                 for p in profiles(sizes,k))

def exact_bound(A,b,lower,upper,weights,Q):
    assert Q>0 and all(w>0 for w in weights.values())
    value=Q*sum(lower);coverage=[0]*len(lower)
    for i,w in weights.items():
        row=A[i]
        value+=w*(b[i]-sum(a*lower[j] for j,a in row))
        for j,a in row:coverage[j]+=w*a
    for j in range(len(lower)):
        if coverage[j]<Q:value+=(upper[j]-lower[j])*(Q-coverage[j])
    return value

def verify_inner(node,A,b,variables,need,lower,upper,counter):
    counter['inner']+=1
    if any(lower[j]>upper[j] for j in range(len(lower))):return
    assert isinstance(node,list) and node
    tag=node[0]
    if tag=='X':
        assert len(node)==2;i=node[1]
        if i==-1:assert any(lower[j]>upper[j] for j in range(len(lower)))
        elif i==-2:assert not variables
        else:
            assert 0<=i<len(A)
            assert b[i]-sum(a*lower[j] for j,a in A[i])<0
        return
    if tag=='D':
        assert len(node)==2;entries=node[1];Q=1 if not entries else entries[0][2]
        weights={};previous=-1
        for i,w,q in entries:
            assert isinstance(i,int) and previous<i<len(A);previous=i
            assert isinstance(w,int) and w>0 and isinstance(q,int) and q==Q and Q>0
            weights[i]=w
        assert exact_bound(A,b,lower,upper,weights,Q)<need*Q
        counter['duals']+=1;return
    assert tag=='I' and len(node)==5
    j,q,left,right=node[1:]
    assert isinstance(j,int) and isinstance(q,int) and 0<=j<len(lower) and lower[j]<=q<upper[j]
    ul=list(upper);ul[j]=q;verify_inner(left,A,b,variables,need,list(lower),ul,counter)
    lr=list(lower);lr[j]=q+1;verify_inner(right,A,b,variables,need,lr,list(upper),counter)
    counter['integer_branches']+=1

# ---------- Z(12,17) bridge ----------
def z1217_cells(fixed):
    V=12;groups=defaultdict(list)
    for r in range(V):
        sig=sum(((b>>r)&1)<<j for j,b in enumerate(fixed));groups[sig].append(r)
    return tuple(tuple(groups[s]) for s in sorted(groups))
def z1217_build(fixed,remaining,forbidden):
    cells=z1217_cells(fixed);sizes=tuple(map(len,cells));triple_orbits=[]
    for u in profiles(sizes,3):
        t=representative(cells,u);fm=sum((b&t)==t for b in fixed)
        if fm>2:return cells,(),(),True
        triple_orbits.append((u,fm,orbit_size(sizes,u)))
    fc=Counter(fixed);variables=[]
    for k,needed in sorted(remaining.items(),reverse=True):
        if needed<=0:continue
        for p,osz,h in profile_data3(sizes,k):
            r=representative(cells,p)
            if r in forbidden.get(k,set()):continue
            upper=min(needed,2*osz-(fc[r] if osz==1 else 0)) if k>=3 else needed
            if upper<=0:continue
            if any(fm==2 and q for q,(_u,fm,_n) in zip(h,triple_orbits)):continue
            variables.append((k,p,r,osz,upper,h))
    return cells,tuple(triple_orbits),tuple(variables),False
def z1217_model(remaining,tos,variables):
    A=[];b=[]
    for qi,(_u,fm,norb) in enumerate(tos):
        A.append(tuple((j,v[5][qi]) for j,v in enumerate(variables) if v[5][qi]));b.append((2-fm)*norb)
    for k,n in sorted(remaining.items(),reverse=True):
        if n>0:A.append(tuple((j,1) for j,v in enumerate(variables) if v[0]==k));b.append(n)
    return tuple(A),tuple(b)
def z1217_outer(node,fixed,remaining,forbidden,counter):
    counter['outer']+=1;need=sum(n for n in remaining.values() if n>0);assert need>0
    cells,tos,variables,bad=z1217_build(fixed,remaining,forbidden)
    if node[0]=='G':assert bad;return
    assert not bad;A,b=z1217_model(remaining,tos,variables)
    k=max(q for q,n in remaining.items() if n>0)
    candidates=sorted((v for v in variables if v[0]==k),key=lambda v:v[1])
    if node[0]=='N':assert node==['N',k] and not candidates;return
    if node[0]=='P':
        assert len(node)==2
        verify_inner(node[1],A,b,variables,need,[0]*len(variables),[v[4] for v in variables],counter);return
    assert node[0]=='B' and len(node)==3 and node[1]==k and len(node[2])==len(candidates)>0
    prior=set(forbidden.get(k,set()))
    for child,v in zip(node[2],candidates):
        _k,p,r,*_=v;nr=dict(remaining);nr[k]-=1
        nf={q:set(s) for q,s in forbidden.items()};nf[k]=set(prior)
        z1217_outer(child,fixed+[r],nr,nf,counter)
        prior.update(orbit_masks(cells,p))
def verify_z1217_part(args):
    profiles.cache_clear();profile_data3.cache_clear();profile_data32.cache_clear()
    path,index,pattern=args
    with gzip.open(path,'rt',encoding='utf8') as f:obj=json.load(f)
    assert obj['format']=='Z1217-local-v1' and obj['index']==index and tuple(obj['pattern'])==tuple(pattern)
    rem=dict(Counter(pattern));k=max(rem);first=(1<<k)-1;rem[k]-=1;assert obj['first']==first
    c=Counter();z1217_outer(obj['tree'],[first],rem,{},c)
    result=index,dict(c),os.path.getsize(path)
    profiles.cache_clear();profile_data3.cache_clear();profile_data32.cache_clear()
    return result

def verify_z1217_chunk(tasks):
    return [verify_z1217_part(t) for t in tasks]

def _external_chunk(kind,directory,start_index,end_index):
    cmd=[sys.executable,str(Path(__file__).resolve()),'--worker-kind',kind,
         '--worker-directory',str(directory),'--worker-start',str(start_index),
         '--worker-end',str(end_index)]
    cp=subprocess.run(cmd,check=True,capture_output=True,text=True)
    return json.loads(cp.stdout)

def verify_z1217(directory,jobs):
    pats=z1217_patterns();assert len(pats)==303
    d=Path(directory);expected={f'{i:03d}.json.gz' for i in range(303)};present={p.name for p in d.glob('*.json.gz')};assert present==expected,{'missing':sorted(expected-present),'extra':sorted(present-expected)}
    results=[];chunks=[(i,min(i+12,303)) for i in range(0,303,12)]
    with ThreadPoolExecutor(max_workers=max(1,jobs)) as ex:
        for f in as_completed([ex.submit(_external_chunk,'z1217',d,a,b) for a,b in chunks]):
            results.extend(f.result())
    results.sort();assert [r[0] for r in results]==list(range(303))
    agg=Counter()
    for _i,c,_s in results:agg.update(c)
    return {'patterns':303,'bytes':sum(r[2] for r in results),**dict(agg)}


# ---------- self-contained Z(11,18) upper bound ----------
def z1118_patterns():return tuple(p for p in gen_partitions(18,102,11) if sum(C(x,3) for x in p)<=330)
def z1118_cells(fixed):
    groups=defaultdict(list)
    for r in range(11):
        sig=sum(((b>>r)&1)<<j for j,b in enumerate(fixed));groups[sig].append(r)
    return tuple(tuple(groups[s]) for s in sorted(groups))
def z1118_build(fixed,remaining,forbidden):
    cells=z1118_cells(fixed);sizes=tuple(map(len,cells));triple_orbits=[]
    for u in profiles(sizes,3):
        t=representative(cells,u);fm=sum((b&t)==t for b in fixed)
        if fm>2:return cells,(),(),True
        triple_orbits.append((u,fm,orbit_size(sizes,u)))
    fc=Counter(fixed);variables=[]
    for k,needed in sorted(remaining.items(),reverse=True):
        if needed<=0:continue
        for p,osz,h in profile_data3(sizes,k):
            r=representative(cells,p)
            if r in forbidden.get(k,set()):continue
            upper=min(needed,2*osz-(fc[r] if osz==1 else 0)) if k>=3 else needed
            if upper<=0:continue
            if any(fm==2 and q for q,(_u,fm,_n) in zip(h,triple_orbits)):continue
            variables.append((k,p,r,osz,upper,h))
    return cells,tuple(triple_orbits),tuple(variables),False
def z1118_outer(node,fixed,remaining,forbidden,counter):
    counter['outer']+=1;need=sum(n for n in remaining.values() if n>0);assert need>0
    cells,tos,variables,bad=z1118_build(fixed,remaining,forbidden)
    if node[0]=='G':assert bad;return
    assert not bad;A,b=z1217_model(remaining,tos,variables)
    k=max(q for q,n in remaining.items() if n>0)
    candidates=sorted((v for v in variables if v[0]==k),key=lambda v:v[1])
    if node[0]=='N':assert node==['N',k] and not candidates;return
    if node[0]=='P':verify_inner(node[1],A,b,variables,need,[0]*len(variables),[v[4] for v in variables],counter);return
    assert node[0]=='B' and len(node)==3 and node[1]==k and len(node[2])==len(candidates)>0
    prior=set(forbidden.get(k,set()))
    for child,v in zip(node[2],candidates):
        _k,p,r,*_=v;nr=dict(remaining);nr[k]-=1
        nf={q:set(s) for q,s in forbidden.items()};nf[k]=set(prior)
        z1118_outer(child,fixed+[r],nr,nf,counter);prior.update(orbit_masks(cells,p))
def verify_z1118_part(args):
    profiles.cache_clear();profile_data3.cache_clear();profile_data32.cache_clear()
    path,index,pattern=args
    with gzip.open(path,'rt',encoding='utf8') as f:obj=json.load(f)
    assert obj['format']=='Z1118-local-v1' and obj['index']==index and tuple(obj['pattern'])==tuple(pattern)
    rem=dict(Counter(pattern));k=max(rem);first=(1<<k)-1;rem[k]-=1;assert obj['first']==first
    c=Counter();z1118_outer(obj['tree'],[first],rem,{},c)
    result=index,dict(c),os.path.getsize(path)
    profiles.cache_clear();profile_data3.cache_clear();profile_data32.cache_clear()
    return result

def verify_z1118_chunk(tasks):
    return [verify_z1118_part(t) for t in tasks]

def verify_z1118(directory,jobs):
    pats=z1118_patterns();assert len(pats)==51
    d=Path(directory);expected={f'{i:03d}.json.gz' for i in range(51)};present={p.name for p in d.glob('*.json.gz')};assert present==expected
    results=[];chunks=[(i,min(i+12,51)) for i in range(0,51,12)]
    with ThreadPoolExecutor(max_workers=max(1,jobs)) as ex:
        for f in as_completed([ex.submit(_external_chunk,'z1118',d,a,b) for a,b in chunks]):
            results.extend(f.result())
    results.sort();assert [r[0] for r in results]==list(range(51));agg=Counter()
    for _i,c,_s in results:agg.update(c)
    return {'patterns':51,'bytes':sum(r[2] for r in results),**dict(agg)}

def verify_reduction_logic():
    # A 109-one candidate: Z(12,17)<=103 forces every column degree >=6.
    assert 109-5==104>103
    col_degrees=[7]+[6]*17
    assert len(col_degrees)==18 and sum(col_degrees)==109 and min(col_degrees)==6
    # Z(11,18)<=101 forces every row degree >=8.
    assert 109-7==102>101
    # If no degree-8 row occurs, the row sum forces 10,9^11.
    no8_rows=[10]+[9]*11
    assert len(no8_rows)==12 and sum(no8_rows)==109
    # A degree-8 row is incident with the unique 7-column or it is not: cases A/B.
    # The unique 7-column contains the unique degree-10 row or it does not: cases I/O.
    return {'forced_column_degrees':col_degrees,'no8_row_degrees':no8_rows,
            'row8_cases':['7-column incident','7-column nonincident'],
            'no8_cases':['7-column contains degree-10 row','7-column avoids degree-10 row']}

# ---------- no-degree-8 branch ----------
NO8_CASES={'I':0,'O':7};NO8_FIX=(1<<7)-1
def no8_cells(fixed,high):
    groups=defaultdict(list)
    for r in range(12):
        sig=1 if r==high else 0
        for j,b in enumerate(fixed):
            if b>>r&1:sig|=1<<(j+1)
        groups[sig].append(r)
    return tuple(tuple(groups[s]) for s in sorted(groups))
def no8_build(fixed,forbidden,high):
    cells=no8_cells(fixed,high);sizes=tuple(map(len,cells));tos=[]
    for u in profiles(sizes,3):
        t=representative(cells,u);fm=sum((b&t)==t for b in fixed)
        if fm>2:return cells,(),(),True
        tos.append((u,fm,orbit_size(sizes,u)))
    fc=Counter(fixed);variables=[];remaining=18-len(fixed)
    for p,osz,h in profile_data3(sizes,6):
        r=representative(cells,p)
        if r in forbidden:continue
        upper=min(remaining,2*osz-(fc[r] if osz==1 else 0))
        if upper<=0:continue
        if any(fm==2 and q for q,(_u,fm,_n) in zip(h,tos)):continue
        variables.append((p,r,osz,upper,h))
    return cells,tuple(tos),tuple(variables),False
def no8_model(fixed,cells,tos,variables,high):
    A=[];b=[];remaining=18-len(fixed)
    for qi,(_u,fm,norb) in enumerate(tos):A.append(tuple((j,v[4][qi]) for j,v in enumerate(variables) if v[4][qi]));b.append((2-fm)*norb)
    A.append(tuple((j,1) for j in range(len(variables))));b.append(remaining)
    for ci,cell in enumerate(cells):
        r=cell[0];target=10 if r==high else 9;fixed_degree=sum((bb>>r)&1 for bb in fixed);required=target-fixed_degree
        assert 0<=required<=remaining
        A.append(tuple((j,v[0][ci]) for j,v in enumerate(variables) if v[0][ci]));b.append(len(cell)*required)
        A.append(tuple((j,len(cell)-v[0][ci]) for j,v in enumerate(variables) if len(cell)-v[0][ci]));b.append(len(cell)*(remaining-required))
    return tuple(A),tuple(b),remaining
def no8_outer(node,fixed,forbidden,high,counter):
    counter['outer']+=1;cells,tos,variables,bad=no8_build(fixed,forbidden,high)
    if node[0]=='G':assert bad;return
    assert not bad;A,b,need=no8_model(fixed,cells,tos,variables,high);candidates=sorted(variables,key=lambda v:v[0])
    if node[0]=='N':assert node==['N'] and not candidates;return
    if node[0]=='P':verify_inner(node[1],A,b,variables,need,[0]*len(variables),[v[3] for v in variables],counter);return
    assert node[0]=='B' and len(node)==2 and len(node[1])==len(candidates)>0
    prior=set(forbidden)
    for child,v in zip(node[1],candidates):
        p,r,*_=v;no8_outer(child,fixed+[r],set(prior),high,counter);prior.update(orbit_masks(cells,p))
def verify_no8(path):
    with gzip.open(path,'rt',encoding='utf8') as f:o=json.load(f)
    assert o['format']=='Z1218-no8-forced-v1' and o['case'] in NO8_CASES
    c=Counter();no8_outer(o['tree'],[NO8_FIX],set(),NO8_CASES[o['case']],c);return {'case':o['case'],**dict(c),'bytes':os.path.getsize(path)}

# ---------- degree-8-row branch ----------
ROW8_CASES={'A':({(1,5):7,(0,6):10},[(1,(1<<6)-1)]),'B':({(1,5):8,(0,6):9},[(0,(1<<7)-1)])}
def row8_cells(fixed):
    groups=defaultdict(list)
    for r in range(11):
        sig=0
        for j,(_m,b) in enumerate(fixed):
            if b>>r&1:sig|=1<<j
        groups[sig].append(r)
    return tuple(tuple(groups[s]) for s in sorted(groups))
def row8_build(fixed,remaining,forbidden):
    cells=row8_cells(fixed);sizes=tuple(map(len,cells));tos=[];pos=[]
    for u in profiles(sizes,3):
        t=representative(cells,u);fm=sum((b&t)==t for _m,b in fixed)
        if fm>2:return cells,(),(),(),True
        tos.append((u,fm,orbit_size(sizes,u)))
    for u in profiles(sizes,2):
        t=representative(cells,u);fm=sum(m and (b&t)==t for m,b in fixed)
        if fm>2:return cells,(),(),(),True
        pos.append((u,fm,orbit_size(sizes,u)))
    fc=Counter(b for _m,b in fixed);variables=[]
    for typ,needed in sorted(remaining.items(),key=lambda q:(-q[0][1],-q[0][0])):
        if needed<=0:continue
        mark,k=typ
        for p,osz,ht,hp in profile_data32(sizes,k):
            r=representative(cells,p)
            if r in forbidden.get(typ,set()):continue
            upper=min(needed,2*osz-(fc[r] if osz==1 else 0))
            if upper<=0:continue
            if any(fm==2 and q for q,(_u,fm,_n) in zip(ht,tos)):continue
            if mark and any(fm==2 and q for q,(_u,fm,_n) in zip(hp,pos)):continue
            variables.append((typ,p,r,osz,upper,ht,hp))
    return cells,tuple(tos),tuple(pos),tuple(variables),False
def row8_model(fixed,remaining,cells,tos,pos,variables):
    A=[];b=[]
    for qi,(_u,fm,norb) in enumerate(tos):A.append(tuple((j,v[5][qi]) for j,v in enumerate(variables) if v[5][qi]));b.append((2-fm)*norb)
    for qi,(_u,fm,norb) in enumerate(pos):A.append(tuple((j,v[6][qi]) for j,v in enumerate(variables) if v[0][0] and v[6][qi]));b.append((2-fm)*norb)
    for typ,n in sorted(remaining.items(),key=lambda q:(-q[0][1],-q[0][0])):
        if n>0:A.append(tuple((j,1) for j,v in enumerate(variables) if v[0]==typ));b.append(n)
    need=sum(n for n in remaining.values() if n>0)
    for ci,cell in enumerate(cells):
        r=cell[0];fixed_degree=sum((bb>>r)&1 for _m,bb in fixed)
        A.append(tuple((j,len(cell)-v[1][ci]) for j,v in enumerate(variables) if len(cell)-v[1][ci]));b.append(len(cell)*(need-8+fixed_degree))
    return tuple(A),tuple(b),need
def row8_outer(node,fixed,remaining,forbidden,counter):
    counter['outer']+=1;cells,tos,pos,variables,bad=row8_build(fixed,remaining,forbidden)
    if node[0]=='G':assert bad;return
    assert not bad;A,b,need=row8_model(fixed,remaining,cells,tos,pos,variables)
    typ=max((t for t,n in remaining.items() if n>0),key=lambda t:(t[1],t[0]));candidates=sorted((v for v in variables if v[0]==typ),key=lambda v:v[1])
    if node[0]=='N':assert node==['N',[typ[0],typ[1]]] and not candidates;return
    if node[0]=='P':verify_inner(node[1],A,b,variables,need,[0]*len(variables),[v[4] for v in variables],counter);return
    assert node[0]=='B' and len(node)==3 and node[1]==[typ[0],typ[1]] and len(node[2])==len(candidates)>0
    prior=set(forbidden.get(typ,set()))
    for child,v in zip(node[2],candidates):
        _t,p,r,*_=v;nr=dict(remaining);nr[typ]-=1;nf={q:set(s) for q,s in forbidden.items()};nf[typ]=set(prior)
        row8_outer(child,fixed+[(typ[0],r)],nr,nf,counter);prior.update(orbit_masks(cells,p))
def verify_row8(path):
    with gzip.open(path,'rt',encoding='utf8') as f:o=json.load(f)
    assert o['format']=='Z1218-row8-orbit-v2' and o['case'] in ROW8_CASES
    rem,fixed=ROW8_CASES[o['case']];c=Counter();row8_outer(o['tree'],list(fixed),dict(rem),{},c);return {'case':o['case'],**dict(c),'bytes':os.path.getsize(path)}

def verify_matrix(path,n,total):
    A=[list(map(int,row)) for row in csv.reader(open(path,newline=''))]
    assert len(A)==12 and all(len(row)==n and all(x in (0,1) for x in row) for row in A)
    assert sum(map(sum,A))==total
    hist=Counter()
    for triple in combinations(range(12),3):
        m=sum(all(A[r][j] for r in triple) for j in range(n));assert m<=2;hist[m]+=1
    return {'ones':total,'row_degrees':[sum(r) for r in A],'column_degrees':[sum(A[r][j] for r in range(12)) for j in range(n)],'triple_histogram':dict(sorted(hist.items()))}

def verify_108(path): return verify_matrix(path,18,108)

def verify_103(path): return verify_matrix(path,17,103)

def verify_114(path): return verify_matrix(path,19,114)
def verify_120(path): return verify_matrix(path,20,120)
def verify_126(path): return verify_matrix(path,21,126)
def verify_132(path): return verify_matrix(path,22,132)

def verify_z1219_deletion_bound():
    # If a 12x19 admissible matrix had 115 ones, a column would have degree
    # at most floor(115/19)=6. Deleting it leaves at least 109 ones in a
    # 12x18 admissible matrix, contradicting the verified 108 upper bound.
    hypothetical=115;columns=19;prior_upper=108
    column_degree_upper=hypothetical//columns
    residual_lower=hypothetical-column_degree_upper
    assert column_degree_upper==6 and residual_lower==109 and residual_lower>prior_upper
    return {'hypothetical_ones':hypothetical,'columns':columns,
            'deleted_column_degree_at_most':column_degree_upper,
            'residual_ones_at_least':residual_lower,
            'prior_z1218_upper':prior_upper,'contradiction':True}

def verify_z1219_to_22_deletion_chain():
    # The minimum-column deletion lemma gives
    # Z(12,n) <= floor(n*Z(12,n-1)/(n-1)).
    chain=[]
    prior=108
    for n in (19,20,21,22):
        upper=(n*prior)//(n-1)
        expected={19:114,20:120,21:126,22:132}[n]
        assert upper==expected
        chain.append({'n':n,'prior_upper':prior,'upper_bound':upper})
        prior=upper
    return chain

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',default=str(ROOT))
    ap.add_argument('--jobs',type=int,default=max(1,min(4,os.cpu_count() or 1)))
    ap.add_argument('--report',default='verification_report.json')
    ap.add_argument('--worker-kind',choices=('z1217','z1118'),default=None,help=argparse.SUPPRESS)
    ap.add_argument('--worker-directory',default=None,help=argparse.SUPPRESS)
    ap.add_argument('--worker-index',type=int,default=None,help=argparse.SUPPRESS)
    ap.add_argument('--worker-start',type=int,default=None,help=argparse.SUPPRESS)
    ap.add_argument('--worker-end',type=int,default=None,help=argparse.SUPPRESS)
    a=ap.parse_args()
    if a.worker_kind:
        assert a.worker_directory is not None
        pats=z1217_patterns() if a.worker_kind=='z1217' else z1118_patterns()
        fn=verify_z1217_part if a.worker_kind=='z1217' else verify_z1118_part
        if a.worker_start is not None:
            assert a.worker_end is not None and 0<=a.worker_start<=a.worker_end<=len(pats)
            result=[]
            for i in range(a.worker_start,a.worker_end):
                result.append(fn((str(Path(a.worker_directory)/f'{i:03d}.json.gz'),i,pats[i])))
        else:
            assert a.worker_index is not None;i=a.worker_index
            result=fn((str(Path(a.worker_directory)/f'{i:03d}.json.gz'),i,pats[i]))
        print(json.dumps(result,separators=(',',':')))
        return
    root=Path(a.root);start=time.time()
    result={'format':'Z1219-full-verification-v1'}
    result['lower_bound_103']=verify_103(root/'data/z12_17_103_witness_verified.csv')
    result['lower_bound_108']=verify_108(root/'data/z12_18_108_witness_verified.csv')
    result['lower_bound_114']=verify_114(root/'data/z12_19_114_witness_verified.csv')
    result['lower_bound_120']=verify_120(root/'data/z12_20_120_witness_verified.csv')
    result['lower_bound_126']=verify_126(root/'data/z12_21_126_witness_verified.csv')
    result['lower_bound_132']=verify_132(root/'data/z12_22_132_witness_verified.csv')
    result['z1217_upper_103']=verify_z1217(root/'certificates/z1217',a.jobs)
    result['z1118_upper_101']=verify_z1118(root/'certificates/z1118',a.jobs)
    result['reduction_logic']=verify_reduction_logic()
    result['no8_cases']=[verify_no8(root/'certificates/z1218/no8_caseI_cert.json.gz'),verify_no8(root/'certificates/z1218/no8_caseO_cert.json.gz')]
    result['row8_cases']=[verify_row8(root/'certificates/z1218/row8_caseA_cert.json.gz'),verify_row8(root/'certificates/z1218/row8_caseB_cert.json.gz')]
    result['z1219_upper_114']=verify_z1219_deletion_bound()
    result['z1219_to_22_deletion_chain']=verify_z1219_to_22_deletion_chain()
    result['conclusion']='Z(12,17,3,3)=103; Z(12,18,3,3)=108; Z(12,19,3,3)=114; Z(12,20,3,3)=120; Z(12,21,3,3)=126; Z(12,22,3,3)=132'
    result['wall_seconds']=time.time()-start
    Path(a.report).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
    print('VERIFIED: Z(12,18,3,3)=108; Z(12,19,3,3)=114; Z(12,20,3,3)=120; Z(12,21,3,3)=126; Z(12,22,3,3)=132')
if __name__=='__main__':main()
