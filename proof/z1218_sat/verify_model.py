#!/usr/bin/env python3
"""Validate a SAT model independently against the original matrix problem."""
from __future__ import annotations
import argparse
from itertools import combinations
from pathlib import Path

R,C=12,18

def parse(path:Path):
    values={}
    status=None
    for line in path.read_text(errors='replace').splitlines():
        if line.startswith('s '):
            status=line[2:].strip()
        elif line.startswith('v '):
            for value in map(int,line[2:].split()):
                if value:
                    values[abs(value)]=value>0
    return status,values

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--branch',choices=['no8','row8'],required=True)
    ap.add_argument('--log',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    status,values=parse(args.log)
    assert status and 'SATISFIABLE' in status and 'UNSATISFIABLE' not in status,status
    assert all(i in values for i in range(1,R*C+1)),'model omits primary variables'
    matrix=[[int(values[1+r*C+c]) for c in range(C)] for r in range(R)]
    assert sum(map(sum,matrix))==109
    row_degrees=[sum(row) for row in matrix]
    col_degrees=[sum(matrix[r][c] for r in range(R)) for c in range(C)]
    assert min(col_degrees)>=5,(row_degrees,col_degrees)
    if args.branch=='no8':
        assert row_degrees==[10]+[9]*11,row_degrees
        assert matrix[0]==[1]*10+[0]*8
    else:
        assert row_degrees[0]==8 and min(row_degrees[1:])>=8,row_degrees
        assert matrix[0]==[1]*8+[0]*10
    for rows in combinations(range(R),3):
        common=[c for c in range(C) if all(matrix[r][c] for r in rows)]
        assert len(common)<=2,(rows,common)
    args.out.write_text('\n'.join(','.join(map(str,row)) for row in matrix)+'\n')
    print('VALID SAT WITNESS',args.branch,'row degrees',row_degrees,'column degrees',col_degrees)

if __name__=='__main__':
    main()
