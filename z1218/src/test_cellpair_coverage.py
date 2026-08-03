#!/usr/bin/env python3
"""Executable exhaustiveness checks for corrected hard-cell profiles."""
from generate_cellpair_shard import all_profiles,HARD_D0

ps=all_profiles()
assert len(ps)==201, len(ps)
keys={(p['branch'],p['d0'],p['d1'],p['q']) for p in ps}
assert len(keys)==len(ps)
assert [p['id'] for p in ps]==list(range(len(ps)))

# Every composition of the 11 unmarked rows into 11,10,01,00 cells whose
# first-column degree is hard and whose second-column degree is allowed maps
# to exactly one profile, and conversely.
for branch,d0s in HARD_D0.items():
    for d0 in d0s:
        seen=set()
        for n11 in range(12):
          for n10 in range(12-n11):
           for n01 in range(12-n11-n10):
            n00=11-n11-n10-n01
            D0=1+n11+n10; d1=1+n11+n01; q=1+n11
            if D0==d0 and 5<=d1<=12:
                k=(branch,d0,d1,q)
                assert k in keys, (k,(n11,n10,n01,n00))
                seen.add(k)
        expected={k for k in keys if k[0]==branch and k[1]==d0}
        assert seen==expected,(branch,d0,len(seen),len(expected))

for p in ps:
    assert p['n11']==p['q']-1
    assert p['n10']==p['d0']-p['q']
    assert p['n01']==p['d1']-p['q']
    assert p['n00']==12-p['d0']-p['d1']+p['q']
    assert sum(p[k] for k in ('n11','n10','n01','n00'))==11
    assert min(p[k] for k in ('n11','n10','n01','n00'))>=0
print(f'PASS: {len(ps)} disjoint profiles exhaust all corrected hard (branch,d0,d1,q) cases')
