#!/usr/bin/env python3
"""Generate exhaustive corrected two-column shards for hard Z(12,18,3,3) cases.

The base formula fixes row 0 and lexicographically orders columns inside the
row-0-neighbour and row-0-nonneighbour groups. We additionally impose row
DoubleLex on rows 1..11. For the first two selected columns, every feasible
profile is specified by

  d0 = degree(column 0), d1 = degree(column 1),
  q  = |column 0 intersect column 1|,

where row 0 belongs to both columns. Hence

  n11=q-1, n10=d0-q, n01=d1-q, n00=12-d0-d1+q.

All four counts must be nonnegative. We use the complete range
max(1,d0+d1-12) <= q <= min(d0,d1); there is deliberately no q<=3 cap.
Under row lex order the four cells occur as 11,10,01,00, so fixing their bits
is equivalent to fixing (d0,d1,q) and materially simplifies the SAT instance.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from generate_cnf import build, write, lex_ge, x, R, C

HARD_D0 = {"no8": (5,), "row8": (5,6,7,8,9,10)}

def all_profiles():
    out=[]
    for branch in ("no8","row8"):
        for d0 in HARD_D0[branch]:
            for d1 in range(5,13):
                lo=max(1,d0+d1-12)
                hi=min(d0,d1)
                for q in range(lo,hi+1):
                    counts=(q-1,d0-q,d1-q,12-d0-d1+q) # 11,10,01,00
                    assert sum(counts)==11 and min(counts)>=0
                    out.append({
                        "id":len(out),"branch":branch,"d0":d0,"d1":d1,
                        "q":q,"n11":counts[0],"n10":counts[1],
                        "n01":counts[2],"n00":counts[3],
                    })
    return out

def add_profile(cnf,p):
    row=1
    for b0,b1,key in ((1,1,"n11"),(1,0,"n10"),(0,1,"n01"),(0,0,"n00")):
        for _ in range(p[key]):
            cnf.unit(x(row,0) if b0 else -x(row,0))
            cnf.unit(x(row,1) if b1 else -x(row,1))
            row+=1
    assert row==R
    # Full row DoubleLex. The first two bits already place the four cells;
    # these constraints order rows inside each cell by the remaining bits.
    for r in range(1,R-1):
        lex_ge(cnf,[x(r,c) for c in range(C)],
                   [x(r+1,c) for c in range(C)])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--profile-id',type=int)
    ap.add_argument('--out',type=Path)
    ap.add_argument('--manifest',type=Path)
    ap.add_argument('--list',action='store_true')
    a=ap.parse_args()
    ps=all_profiles()
    if a.list:
        print(json.dumps(ps,indent=2)); return
    if a.profile_id is None or a.out is None:
        ap.error('--profile-id and --out are required unless --list is used')
    if not 0 <= a.profile_id < len(ps):
        ap.error(f'profile id must be in 0..{len(ps)-1}')
    p=ps[a.profile_id]
    cnf=build(p['branch'])
    add_profile(cnf,p)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    tag=f"{p['branch']}-doublelex-d0{p['d0']}-d1{p['d1']}-q{p['q']}"
    write(cnf,a.out,tag)
    if a.manifest:
        a.manifest.write_text(json.dumps({**p,'tag':tag,'vars':cnf.nvars,'clauses':len(cnf.clauses)},indent=2)+'\n')
    print(json.dumps({**p,'tag':tag,'vars':cnf.nvars,'clauses':len(cnf.clauses)}))

if __name__=='__main__': main()
