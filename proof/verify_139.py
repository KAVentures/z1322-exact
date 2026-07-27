#!/usr/bin/env python3
from itertools import combinations
from fractions import Fraction
from math import comb
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
PTS=range(13)
TR=list(combinations(PTS,3)); PA=list(combinations(PTS,2))
TID={t:i for i,t in enumerate(TR)}; PID={p:i for i,p in enumerate(PA)}
PEN=[comb(d,3)-15*d+70 for d in range(14)]

def enumerate_profiles():
    out=[]
    def rec(d,leftn,lefts,c,pen):
        if d==13:
            n=leftn
            if 13*n!=lefts or pen+PEN[13]*n>27:return
            cc=c+[n]
            inc=sum(cc[i]*comb(i,3) for i in range(14))
            if inc<=572: out.append(tuple(cc))
            return
        for n in range(leftn+1):
            if d*n>lefts:break
            np=pen+PEN[d]*n
            if np<=27:rec(d+1,leftn-n,lefts-d*n,c+[n],np)
    rec(0,22,139,[],0)
    return sorted(out)

def F(q):return Fraction(q[0],q[1])
def contains(mask,sub):return mask&sub==sub

def verify_cert(path):
    d=json.loads(path.read_text())
    counts={int(k):int(v) for k,v in d['counts'].items()}
    f=d['fixed_degree']; fixed=sum(1<<i for i in d['fixed_block'])
    assert d['fixed_block']==list(range(f))
    counts[f]-=1
    active=d['active_degrees']
    alpha=list(map(F,d['alpha'])); beta=list(map(F,d['beta']))
    assert len(alpha)==286+13+78 and all(x>=0 for x in alpha)
    assert len(beta)==len(active)
    rhs=[]
    for t in TR:
        tm=sum(1<<i for i in t);rhs.append(2-int(contains(fixed,tm)))
    for r in PTS:rhs.append(132-(comb(f-1,2) if fixed>>r&1 else 0))
    for p in PA:
        pm=(1<<p[0])|(1<<p[1]);rhs.append(22-((f-2) if contains(fixed,pm) else 0))
    value=sum(a*b for a,b in zip(alpha,rhs))+sum(beta[i]*counts[deg] for i,deg in enumerate(active))
    assert value==F(d['rhs'])<0
    least=None;nvars=0
    for i,deg in enumerate(active):
        for B in combinations(PTS,deg):
            bm=sum(1<<x for x in B); val=beta[i]
            for j,t in enumerate(TR):
                tm=(1<<t[0])|(1<<t[1])|(1<<t[2])
                if contains(bm,tm):val+=alpha[j]
            w=comb(deg-1,2)
            for r in B:val+=w*alpha[286+r]
            for j,p in enumerate(PA):
                pm=(1<<p[0])|(1<<p[1])
                if contains(bm,pm):val+=(deg-2)*alpha[299+j]
            assert val>=0,(path,B,val)
            least=val if least is None or val<least else least;nvars+=1
    assert least==F(d['min_coefficient'])
    return tuple((int(k),int(v)+(1 if int(k)==f else 0)) for k,v in sorted(counts.items()) if v+(1 if k==f else 0)),nvars,value

def verify_balanced_lemma():
    # In profile 6^15 7^7, total triple slack is 27.
    assert 2*comb(13,3)-(15*comb(6,3)+7*comb(7,3))==27
    # D_r=132-10a-15b=2+5k_r and sum k_r=11, so some row has k=0.
    assert (3*27-13*2)//5==11 and 11<13
    # For k=0, 2a+3b=26. Pair-capacity bounds leave only (7,4).
    candidates=[]
    for a in range(16):
        for b in range(8):
            if 2*a+3*b==26:candidates.append((a,b))
    assert candidates==[(4,6),(7,4),(10,2),(13,0)]
    def max_u(n,total_v):
        # For a pair through r, 4u+5v<=22, so u<=floor((22-5v)/4).
        dp=[-10**9]*(total_v+1);dp[0]=0
        for _ in range(n):
            nd=[-10**9]*(total_v+1)
            for s in range(total_v+1):
                for v in range(5):
                    if s>=v:nd[s]=max(nd[s],dp[s-v]+(22-5*v)//4)
            dp=nd
        return dp[total_v]
    viable=[]
    for a,b in candidates:
        if 5*a<=max_u(12,6*b):viable.append((a,b))
    assert viable==[(7,4)]
    # D_r=2 gives a loopless deficit multigraph of total edge multiplicity two,
    # so each pair-deficit degree is at most two. Enumerate forced local types.
    types=[]
    for v in range(5):
        for u in range(6):
            e=22-4*u-5*v
            if 0<=e<=2:types.append((u,v,e))
    sols=[]
    def rec(i,n,su,sv,se,cs):
        if i==len(types):
            if (n,su,sv,se)==(12,35,24,4):sols.append(tuple(cs))
            return
        u,v,e=types[i]
        for z in range(13-n):
            if su+z*u>35 or sv+z*v>24 or se+z*e>4:break
            rec(i+1,n+z,su+z*u,sv+z*v,se+z*e,cs+[z])
    rec(0,0,0,0,0,[])
    # identify distributions by multiset of (u,v,e)
    dist=[]
    for cs in sols:
        dist.append(sorted([types[i] for i,z in enumerate(cs) for _ in range(z)]))
    expected=[
      sorted([(0,4,2)]+2*[(4,1,1)]+9*[(3,2,0)]),
      sorted([(0,4,2),(5,0,2)]+10*[(3,2,0)])]
    assert sorted(dist)==sorted(expected)
    # The common point c lies in all four 7-columns and no 6-column. Deleting r,c
    # gives a symmetric 2-(11,5,2) design. Any two blocks meet in 2 points.
    # But selected four 7-blocks have point degrees below, whose pairwise
    # intersection totals are sum C(v_y,2)=9 or 10, not C(4,2)*2=12.
    totals=[]
    for dd in expected:
        vs=[v for u,v,e in dd if not (u==0 and v==4 and e==2)]
        assert len(vs)==11 and sum(vs)==20
        totals.append(sum(comb(v,2) for v in vs))
    assert sorted(totals)==[9,10]
    assert comb(4,2)*2==12
    return {'candidate_row_counts':candidates,'viable':viable,'selected_intersection_totals':totals}

def main():
    profiles=enumerate_profiles();assert len(profiles)==27
    balanced=tuple([0]*6+[15,7]+[0]*6) # degrees 0..13
    assert balanced in profiles
    cert_profiles=[];totalvars=0
    for p in sorted((ROOT/'certs139').glob('p*.json')):
        cp,n,v=verify_cert(p); totalvars+=n
        arr=[0]*14
        for deg,c in cp:arr[deg]=c
        cert_profiles.append(tuple(arr))
    assert len(cert_profiles)==26 and len(set(cert_profiles))==26
    assert set(cert_profiles)==set(profiles)-{balanced}
    lemma=verify_balanced_lemma()
    report={'status':'PASS','profiles':27,'farkas_certificates':26,'checked_block_variables':totalvars,'balanced_profile':'6^15 7^7','balanced_lemma':lemma,'conclusion':'No 139-one K_3,3-free 13x22 binary matrix exists; Z(13,22,3,3)<=138.'}
    (ROOT/'reports/verify_139_report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
