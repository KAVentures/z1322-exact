#!/usr/bin/env python3
from itertools import combinations, permutations, product
from fractions import Fraction
from math import comb
from pathlib import Path
import subprocess, json, tempfile, os, sys

ROOT=Path(__file__).resolve().parent
BIN=Path(os.environ.get('LOCAL_SCREEN_BIN',ROOT/'local_screen_general'))
CERT=ROOT/'local_certs'
CCERT=ROOT/'completion_certs'
PTS=range(13)
TR=list(combinations(PTS,3)); PA=list(combinations(PTS,2))
TID={t:i for i,t in enumerate(TR)}; PID={p:i for i,p in enumerate(PA)}

screen_cache={}
def screen(s0,w,a,b,D):
    key=(s0,w,a,b,D)
    if key not in screen_cache:
        p=subprocess.run([str(BIN),str(s0),str(w),str(a),str(b),str(D),'1'],check=True,capture_output=True,text=True)
        d=json.loads(p.stdout)
        assert (d['s0'],d['w'],d['a'],d['b'],d['D'])==key
        screen_cache[key]=d
    return screen_cache[key]

def row_pairs(count6,count7,special_degree,c,D):
    contribution=comb(special_degree-1,2)*c if special_degree else 0
    return [(a,b) for a in range(count6+1) for b in range(count7+1)
            if contribution+10*a+15*b==132-D]

def assert_zero(s0,w,a,b,D,expected=None):
    d=screen(s0,w,a,b,D)
    assert d['survivors']==0,(s0,w,a,b,D,d['survivors'])
    if expected:
        assert (d['dists'],d['graphs'],d['survivors'])==expected
    return d

def y_vector(cert,n):
    y=[0]*n
    for i,v in cert['y']:
        assert 0<=i<n and y[i]==0
        y[i]=int(v)
    return y

def verify_factor_certificate(case,cert,sizes,counts):
    k=len(sizes); assert k==3
    V=[tuple(x) for x in case['types']]
    adj=[[0]*12 for _ in range(12)]
    for i,j,w in case['edges']:
        assert 0<=i<j<12 and 1<=w<=2
        adj[i][j]=adj[j][i]=w
    nr=12*k+66+k
    y=y_vector(cert,nr)
    rhs=[]
    for coord in range(k): rhs.extend(V[x][coord] for x in range(12))
    for x in range(12):
        for z in range(x+1,12): rhs.append(2-adj[x][z])
    rhs.extend(counts)
    assert sum(a*b for a,b in zip(y,rhs))==cert['rhs_num']<0
    pairw=[[0]*12 for _ in range(12)]; q=12*k
    for x in range(12):
        for z in range(x+1,12):
            pairw[x][z]=pairw[z][x]=y[q];q+=1
    least=None; n=0
    for coord,size in enumerate(sizes):
        eligible=[x for x in range(12) if V[x][coord]>0]
        base=y[12*k+66+coord]
        pw=y[12*coord:12*(coord+1)]
        for B in combinations(eligible,size):
            val=base+sum(pw[x] for x in B)
            val+=sum(pairw[B[i]][B[j]] for i in range(size) for j in range(i+1,size))
            assert val>=0,(case,B,val)
            least=val if least is None or val<least else least
            n+=1
    assert n==cert['cands'] and least==cert['min_num']
    return n

def load_certificates(paths):
    out=[]
    for path in paths:
        d=json.loads(path.read_text())
        start=d.get('start',0); end=d.get('end',start+len(d['certificates']))
        assert end-start==len(d['certificates'])
        out.append((start,end,d['certificates']))
    out.sort()
    return out

def verify_case_family(data,cert_paths,sizes,counts):
    cases=data['cases']; covered=[False]*len(cases); nvars=0
    for start,end,certs in load_certificates(cert_paths):
        assert 0<=start<=end<=len(cases)
        for i,c in enumerate(certs,start):
            assert not covered[i]; covered[i]=True
            nvars+=verify_factor_certificate(cases[i],c,sizes,counts)
    assert all(covered)
    return nvars

def verify_balanced_local_factor(data):
    d=json.loads((CERT/'bal_d7_infeasible_int.json').read_text())
    assert len(data['cases'])==4 and len(d['certificates'])==3
    n=0
    for c in d['certificates']:
        i=c['case_index']; assert i in (0,1,2)
        n+=verify_factor_certificate(data['cases'][i],c,(4,5,6),(0,8,3))
    return n

def enumerate_case3_local(case):
    # Exhaustive local integral factorization of the sole fractionally feasible case.
    V=[tuple(x) for x in case['types']]
    adj=[[0]*12 for _ in range(12)]
    for i,j,w in case['edges']:adj[i][j]=adj[j][i]=w
    pairs=list(combinations(range(12),2)); pi={p:i for i,p in enumerate(pairs)}
    target=[2-adj[i][j] for i,j in pairs]
    C6=[]
    for B in combinations([i for i in range(12) if V[i][2]>0],6):
        C6.append((B,[pi[p] for p in combinations(B,2)]))
    need6=[V[i][2] for i in range(12)]; systems=[]
    def rec6(start,left,deg,pc,ch):
        if left==0:
            if deg==need6: systems.append(tuple(sorted(C6[i][0] for i in ch)))
            return
        for idx in range(start,len(C6)):
            B,ps=C6[idx]; nd=deg[:]
            for x in B:nd[x]+=1
            if any(nd[x]>need6[x] for x in range(12)):continue
            np=pc[:]
            for z in ps:
                np[z]+=1
                if np[z]>target[z]:break
            else: rec6(idx,left-1,nd,np,ch+[idx])
    rec6(0,3,[0]*12,[0]*66,[])
    assert len(systems)==285
    # Exact orbit cover under the full typed-leave automorphism group S2 x S3 x S6.
    perms=[]
    for h in permutations([1,2]):
      for l in permutations([3,4,5]):
       for p in permutations(range(6,12)):
        m=[0]*12;m[0]=0
        for s,t in zip([1,2],h):m[s]=t
        for s,t in zip([3,4,5],l):m[s]=t
        for s,t in zip(range(6,12),p):m[s]=t
        perms.append(m)
    assert len(perms)==8640
    for m in perms:
        assert all(V[m[i]]==V[i] for i in range(12))
        assert all(adj[m[i]][m[j]]==adj[i][j] for i in range(12) for j in range(12))
    def trans(s,m):return tuple(sorted(tuple(sorted(m[x] for x in B)) for B in s))
    def canon(s):return min(trans(s,m) for m in perms)
    orbits={}
    for s in systems:orbits.setdefault(canon(s),0);orbits[canon(s)]+=1
    assert sorted(orbits.values())==[15,90,180]
    results=[]
    for oi,(b6,mult) in enumerate(sorted(orbits.items())):
        rem=target[:]
        for B in b6:
            for p in combinations(B,2):rem[pi[p]]-=1
        need=[V[i][1] for i in range(12)]
        C5=[]
        for B in combinations([i for i in range(12) if need[i]>0],5):
            ps=[pi[p] for p in combinations(B,2)]
            if all(rem[z]>0 for z in ps):C5.append((B,ps))
        bypair=[[] for _ in pairs]
        for i,(B,ps) in enumerate(C5):
            for z in ps:bypair[z].append(i)
        sols=set();memo=set()
        def rec5(left,deg,rp,counts):
            key=(left,tuple(deg),tuple(rp))
            if key in memo:return
            if left==0:
                if not any(deg) and not any(rp):
                    blocks=[]
                    for i,n in enumerate(counts):blocks += [C5[i][0]]*n
                    sols.add(tuple(sorted(blocks)))
                return
            if sum(deg)!=5*left or sum(rp)!=10*left:return
            opts=None
            for z,v in enumerate(rp):
                if v<=0:continue
                oo=[]
                for i in bypair[z]:
                    B,ps=C5[i]
                    if all(deg[x]>0 for x in B) and all(rp[t]>0 for t in ps):oo.append(i)
                if not oo:memo.add(key);return
                if opts is None or len(oo)<len(opts):opts=oo
            if opts is None:return
            for i in opts:
                B,ps=C5[i];nd=deg[:];nr=rp[:]
                for x in B:nd[x]-=1
                for z in ps:nr[z]-=1
                counts[i]+=1;rec5(left-1,nd,nr,counts);counts[i]-=1
            memo.add(key)
        rec5(8,need[:],rem[:],[0]*len(C5))
        results.append((b6,tuple(sorted(sols)),mult))
    assert [len(x[1]) for x in results]==[0,0,4]
    return results[2][0],results[2][1]

def F(q):return Fraction(q[0],q[1])
def verify_completion_certificate(path,expected_profile,solution_index,b6,b5):
    d=json.loads(path.read_text()); assert d['profile']==expected_profile and d['solution_index']==solution_index
    fixed=[set(B) for B in d['fixed_blocks']]; assert all(12 in B for B in fixed)
    expected=[set(B)|{12} for B in b6]+[set(B)|{12} for B in b5]
    assert sorted(map(sorted,fixed))==sorted(map(sorted,expected))
    counts={int(k):int(v) for k,v in d['remaining_counts'].items()};active=d['active_degrees']
    al=list(map(F,d['alpha']));be=list(map(F,d['beta']));assert len(al)==377 and len(be)==len(active) and all(x>=0 for x in al)
    rhs=[2-sum(set(t)<=B for B in fixed) for t in TR]
    rhs += [132-sum(comb(len(B)-1,2) for B in fixed if r in B) for r in PTS]
    rhs += [22-sum((len(B)-2) for B in fixed if set(p)<=B) for p in PA]
    assert min(rhs)>=0
    value=sum(x*y for x,y in zip(al,rhs))+sum(be[i]*counts[deg] for i,deg in enumerate(active))
    assert value==F(d['rhs'])<0
    least=None;n=0
    for i,deg in enumerate(active):
        for B in combinations(range(12),deg): # remaining columns exclude the marked row 12
            val=be[i]
            val+=sum(al[TID[t]] for t in combinations(B,3))
            val+=comb(deg-1,2)*sum(al[286+r] for r in B)
            val+=(deg-2)*sum(al[299+PID[p]] for p in combinations(B,2))
            assert val>=0,(path,B,val)
            least=val if least is None or val<least else least;n+=1
    assert least==F(d['min_coefficient'])
    return n

def verify_common_d7_and_completions():
    data=screen(4,0,8,3,7)
    assert (data['dists'],data['graphs'],data['survivors'])==(37,6733,4)
    n=verify_balanced_local_factor(data)
    b6,sols=enumerate_case3_local(data['cases'][3])
    profile_counts={'P0':{6:8,7:3},'PA':{5:1,6:6,7:4},'PB':{5:2,6:4,7:5},'PC':{5:3,6:2,7:6}}
    for pname in profile_counts:
        for i,b5 in enumerate(sols):
            path=CCERT/f'{pname}_s{i}.json'
            n+=verify_completion_certificate(path,pname,i,b6,b5)
    return n

def check_profile_arithmetic(counts):
    edges=sum(d*n for d,n in counts.items());cols=sum(counts.values())
    assert edges==138 and cols==22
    slack=2*comb(13,3)-sum(n*comb(d,3) for d,n in counts.items())
    return slack,3*slack

def prove_profiles():
    checked=0
    # Common exact local computation and all four completion families.
    checked+=verify_common_d7_and_completions()

    # P0: 6^16 7^6.
    counts={6:16,7:6};slack,total=check_profile_arithmetic(counts);assert (slack,total)==(42,126)
    p2=row_pairs(16,6,None,0,2);assert p2==[(4,6),(7,4),(10,2),(13,0)]
    for a,b in p2:assert_zero(4,0,a,b,2)
    p7=row_pairs(16,6,None,0,7);assert p7==[(5,5),(8,3),(11,1)]
    assert_zero(4,0,5,5,7,(19,8641,0));assert_zero(4,0,11,1,7,(0,0,0))
    assert 13*12>total # if neither D=2 nor D=7 occurs, every D is at least 12

    # PA: 5^1 6^14 7^7.
    counts={5:1,6:14,7:7};slack,total=check_profile_arithmetic(counts);assert (slack,total)==(37,111)
    for a,b in row_pairs(14,7,5,0,2):assert_zero(4,0,a,b,2)
    for a,b in row_pairs(14,7,5,1,1):assert_zero(4,1,a,b,1)
    assert 8*7+5*6==86 and total-86==25 and 86+13*5>total
    for a,b in row_pairs(14,7,5,0,7):
        if (a,b)!=(8,3):assert_zero(4,0,a,b,7)
    pa6=row_pairs(14,7,5,1,6);assert pa6==[(3,6),(6,4),(9,2),(12,0)]
    expected={(12,0):(0,0,0),(9,2):(0,0,0),(6,4):(508,43715,0),(3,6):(6,534,0)}
    for a,b in pa6:assert_zero(4,1,a,b,6,expected[(a,b)])

    # PB: 5^2 6^12 7^8.
    counts={5:2,6:12,7:8};slack,total=check_profile_arithmetic(counts);assert (slack,total)==(32,96)
    for c,D in [(0,2),(1,1),(2,0)]:
        for a,b in row_pairs(12,8,5,c,D):assert_zero(4,c,a,b,D)
    assert 7*13-10==81 and total-81==15 and 81+13*5>total
    for a,b in row_pairs(12,8,5,0,7):
        if (a,b)!=(8,3):assert_zero(4,0,a,b,7)
    for a,b in row_pairs(12,8,5,1,6):assert_zero(4,1,a,b,6)
    pb5=row_pairs(12,8,5,2,5);assert pb5==[(1,7),(4,5),(7,3),(10,1)]
    assert_zero(4,2,1,7,5,(0,0,0))
    fam=[((4,2,10,1,5),[CERT/'c2_10_1_int_0_195.json'],(4,5,6),(2,10,1),195),
         ((4,2,7,3,5),[CERT/'c2_7_3_int_0_217.json'],(4,5,6),(2,7,3),217),
         ((4,2,4,5,5),[CERT/'c2_4_5_int_0_28.json'],(4,5,6),(2,4,5),28)]
    for key,paths,sizes,cnts,ncases in fam:
        d=screen(*key);assert len(d['cases'])==ncases;checked+=verify_case_family(d,paths,sizes,cnts)

    # PC: 5^3 6^10 7^9.
    counts={5:3,6:10,7:9};slack,total=check_profile_arithmetic(counts);assert (slack,total)==(27,81)
    for c,D in [(0,2),(1,1),(2,0)]:
        for a,b in row_pairs(10,9,5,c,D):assert_zero(4,c,a,b,D)
    assert 7*13-15==76 and total-76==5 and 76+13*5>total
    for a,b in row_pairs(10,9,5,0,7):
        if (a,b)!=(8,3):assert_zero(4,0,a,b,7)
    for a,b in row_pairs(10,9,5,1,6):assert_zero(4,1,a,b,6)
    # c=2,D=5 is already covered by the three PB factor families and the zero case above.
    pc4=row_pairs(10,9,5,3,4);assert pc4==[(2,6),(5,4),(8,2)]
    paths8=sorted(CERT.glob('c3_8_2_int_*.json'))
    fam=[((4,3,8,2,4),paths8,(4,5,6),(3,8,2),4746),
         ((4,3,5,4,4),[CERT/'c3_5_4_int_0_656.json'],(4,5,6),(3,5,4),656),
         ((4,3,2,6,4),[CERT/'c3_2_6_int_0_3.json'],(4,5,6),(3,2,6),3)]
    for key,paths,sizes,cnts,ncases in fam:
        d=screen(*key);assert len(d['cases'])==ncases;checked+=verify_case_family(d,paths,sizes,cnts)

    # PD: 4^1 6^13 7^8.
    counts={4:1,6:13,7:8};slack,total=check_profile_arithmetic(counts);assert (slack,total)==(28,84)
    for a,b in row_pairs(13,8,4,0,2):assert_zero(4,0,a,b,2)
    assert 9*2+4*4==34 and total-34==50 and 34+13*5>total
    pd4=row_pairs(13,8,4,1,4);assert pd4==[(2,7),(5,5),(8,3),(11,1)]
    assert_zero(3,1,2,7,4,(0,0,0));assert_zero(3,1,11,1,4,(0,0,0))
    d=screen(3,1,8,3,4);assert (d['dists'],d['graphs'],d['survivors'])==(41,367,12)
    checked+=verify_case_family(d,[CERT/'p3_8_3_int.json'],(3,5,6),(1,8,3))
    d=screen(3,1,5,5,4);assert (d['dists'],d['graphs'],d['survivors'])==(48,275,3)
    checked+=verify_case_family(d,[CERT/'p3_5_5_int.json'],(3,5,6),(1,5,5))
    return checked

if __name__=='__main__':
    n=prove_profiles()
    report={'status':'PASS','theorem':'No 13x22 K_3,3-free binary matrix has 138 ones.',
            'five_profiles_excluded':True,'local_factor_block_variables_checked':n,
            'screen_instances':len(screen_cache),'conclusion':'Z(13,22,3,3)=137'}
    (ROOT/'reports/verify_138_full_report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
