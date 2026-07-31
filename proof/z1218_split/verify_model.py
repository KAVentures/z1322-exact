#!/usr/bin/env python3
from itertools import combinations
from pathlib import Path
import argparse
R,C=12,18

def parse(path):
    vals={}; status=None
    for line in Path(path).read_text(errors='replace').splitlines():
        if line.startswith('s '): status=line[2:].strip()
        elif line.startswith('v '):
            for z in map(int,line[2:].split()):
                if z: vals[abs(z)]=z>0
    return status,vals

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--branch',choices=['no8','row8'],required=True); ap.add_argument('--log',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    status,v=parse(a.log); assert status and 'SATISFIABLE' in status and 'UNSATISFIABLE' not in status,status
    assert all(i in v for i in range(1,R*C+1))
    M=[[int(v[1+r*C+c]) for c in range(C)] for r in range(R)]
    assert sum(map(sum,M))==109
    rd=[sum(x) for x in M]; cd=[sum(M[r][c] for r in range(R)) for c in range(C)]
    assert min(cd)>=5
    if a.branch=='no8': assert rd==[10]+[9]*11 and M[0]==[1]*10+[0]*8
    else: assert rd[0]==8 and min(rd[1:])>=8 and M[0]==[1]*8+[0]*10
    for rs in combinations(range(R),3):
        common=[c for c in range(C) if all(M[r][c] for r in rs)]
        assert len(common)<=2,(rs,common)
    Path(a.out).write_text('\n'.join(','.join(map(str,row)) for row in M)+'\n')
    print('VALID 109-EDGE WITNESS',a.branch,'rows',rd,'cols',cd)
if __name__=='__main__': main()
