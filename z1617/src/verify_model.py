#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from itertools import combinations
from pathlib import Path
R,C=16,17
def parse(path):
 status=None;vals={}
 for line in path.read_text(errors='replace').splitlines():
  if line.startswith('s '):status=line[2:].strip()
  elif line.startswith('v '):
   for z in map(int,line[2:].split()):
    if z:vals[abs(z)]=z>0
 return status,vals
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--log',type=Path,required=True);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 status,v=parse(a.log);assert status and 'SATISFIABLE' in status and 'UNSATISFIABLE' not in status,status
 assert all(i in v for i in range(1,R*C+1))
 A=[[int(v[1+r*C+c]) for c in range(C)] for r in range(R)]
 man=json.loads(a.manifest.read_text());rd=[sum(z) for z in A];cd=[sum(A[r][c] for r in range(R)) for c in range(C)]
 assert rd==man['row_degrees'],(rd,man['row_degrees']);assert sum(rd)==133;assert min(cd)>=5
 for rows in combinations(range(R),3):
  common=[c for c in range(C) if all(A[r][c] for r in rows)]
  assert len(common)<=2,(rows,common)
 a.out.write_text('\n'.join(','.join(map(str,row)) for row in A)+'\n')
 print('VALID 133-EDGE WITNESS','row_degrees',rd,'column_degrees',cd)
if __name__=='__main__':main()
