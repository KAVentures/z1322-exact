#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
subprocess.run(['g++','-O3','-std=c++17',str(ROOT/'local_screen_general.cpp'),'-o',str(ROOT/'local_screen_general')],check=True)
# Independent gates can run concurrently; their outputs are replayed after completion.
scripts=['verify_137.py','verify_139.py','verify_138_reduction.py']
procs=[]
for s in scripts:
 procs.append((s,subprocess.Popen([sys.executable,str(ROOT/s)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)))
for s,p in procs:
 out,_=p.communicate()
 print(f'\n=== {s} ===\n{out}',end='',flush=True)
 if p.returncode:raise SystemExit(f'{s} failed with exit code {p.returncode}')
print('\n=== verify_138_full.py ===',flush=True)
subprocess.run([sys.executable,str(ROOT/'verify_138_full.py')],check=True)
print('\nALL EXACT-VALUE VERIFICATION GATES PASSED')
