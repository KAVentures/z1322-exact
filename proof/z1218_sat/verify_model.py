#!/usr/bin/env python3
from __future__ import annotations
import argparse
from itertools import combinations
from pathlib import Path
R,C=12,18
def parse(path):
    values={}; status=None
    for line in path.read_text(errors='replace').splitlines():
        if line.startswith('s '): status=line[2:].strip()
        elif line.startswith('v '):
            for value in map(int,line[2:].split()):
                if value: values[abs(value)]=value>0
    return status,values
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--branch',choices=['no8','row8'],required=True); ap.add_argument('--log',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); status,values=parse(a.log)
    assert status and 'SATISFIABLE' in status and 'UNSATISFIABLE' not in status,status
    assert all(i in values for i in range(1,R*C+1))
    M=[[int(values[1+r*C+c]) for c in range(C)] for r in range(R)]
    assert sum(map(sum,M))==109
    rd=[sum(row) for row in M]; cd=[sum(M[r][c] for r in range(R)) for c in range(C)]
    assert min(cd)>=5
    if a.branch=='no8': assert rd==[10]+[9]*11 and M[0]==[1]*10+[0]*8
    else: assert rd[0]==8 and min(rd[1:])>=8 and M[0]==[1]*8+[0]*10
    for rows in combinations(range(R),3): assert sum(all(M[r][c] for r in rows) for c in range(C))<=2
    a.out.write_text('\n'.join(','.join(map(str,row)) for row in M)+'\n'); print('VALID SAT WITNESS',a.branch,rd,cd)
if __name__=='__main__': main()
