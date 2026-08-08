#!/usr/bin/env python3
from itertools import combinations
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
obj=json.loads((ROOT/'data/z13_22_137_blocks.json').read_text())
blocks=[tuple(B) for B in obj['blocks']]
assert len(blocks)==22
assert all(len(set(B))==len(B) and all(0<=x<13 for x in B) for B in blocks)
assert sum(map(len,blocks))==137
counts={T:0 for T in combinations(range(13),3)}
for B in blocks:
    for T in combinations(sorted(B),3): counts[T]+=1
assert max(counts.values())<=2
print('PASS: checked 137-one K_3,3-free witness')
