#!/usr/bin/env python3
"""Exact deletion-closure of the new frontier bounds (standard library only)."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

# Public frontier upper bounds before the present closure, for comparison.
PRIOR={
 (13,17):112,(13,18):118,(13,19):124,(13,20):130,(13,21):135,(13,22):140,(13,23):144,
 (14,17):120,(14,18):127,(14,19):133,(14,20):140,(14,21):145,(14,22):150,(14,23):155,
 (15,17):128,(15,18):135,(15,19):142,(15,20):149,(15,21):154,(15,22):160,(15,23):165,
 (16,17):136,(16,18):144,(16,19):151,(16,20):158,(16,21):164,(16,22):169,(16,23):175,
}

# Upper bounds proved in verify_all.py.  Exact values are a subset once the
# published lower constructions are invoked.
SEEDS={(13,17):110,(13,18):116,(14,17):118,(14,18):124,(15,17):126,(15,18):132,(16,17):133}


def closure():
    upper=dict(PRIOR)
    provenance={k:'prior frontier' for k in upper}
    for k,v in SEEDS.items():
        if v<upper.get(k,10**9):
            upper[k]=v;provenance[k]='proved here'
    changed=True
    while changed:
        changed=False
        for (m,n),u in list(upper.items()):
            if m<16:
                v=(m+1)*u//m
                key=(m+1,n)
                if v<upper.get(key,10**9):
                    upper[key]=v;provenance[key]=f'row deletion from ({m},{n})<={u}';changed=True
            if n<23:
                v=(n+1)*u//n
                key=(m,n+1)
                if v<upper.get(key,10**9):
                    upper[key]=v;provenance[key]=f'column deletion from ({m},{n})<={u}';changed=True
    return upper,provenance


def main():
    upper,prov=closure()
    improvements=[]
    for key,old in sorted(PRIOR.items()):
        new=upper[key]
        if new<old:
            improvements.append({'m':key[0],'n':key[1],'old_upper':old,'new_upper':new,'improvement':old-new,'source':prov[key]})
    assert upper[(13,18)]==116
    assert upper[(14,17)]==118 and upper[(14,18)]==124
    assert upper[(15,17)]==126 and upper[(15,18)]==132
    assert upper[(16,17)]==133
    report={'status':'PASS','new_seed_bounds':{f'{m},{n}':v for (m,n),v in sorted(SEEDS.items())},
            'improved_cells':improvements,
            'closed_upper_table':{f'{m},{n}':upper[(m,n)] for m in range(13,17) for n in range(17,24)}}
    (ROOT/'reports/frontier_propagation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('improved frontier upper bounds:',len(improvements))
    for x in improvements:print(f"Z({x['m']},{x['n']}) <= {x['new_upper']}  (was {x['old_upper']})")

if __name__=='__main__':main()
