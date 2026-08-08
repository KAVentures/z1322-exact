#!/usr/bin/env python3
"""Compare deterministic proof invariants while ignoring wall-clock time."""
import json,sys
from pathlib import Path

def strip(obj):
    if isinstance(obj,dict):return {k:strip(v) for k,v in obj.items() if k!='wall_seconds'}
    if isinstance(obj,list):return [strip(x) for x in obj]
    return obj
if len(sys.argv)!=3:raise SystemExit('usage: compare_report.py reference.json reproduced.json')
a=strip(json.loads(Path(sys.argv[1]).read_text()))
b=strip(json.loads(Path(sys.argv[2]).read_text()))
assert a==b,'reproduced report differs from reference invariants'
print('REPORT INVARIANTS MATCH')
