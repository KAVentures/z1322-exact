#!/usr/bin/env python3
from pathlib import Path
import os
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
print('\n=== z12_18_21/verify_all_exact.py ===',flush=True)
subprocess.run([sys.executable,str(ROOT/'z12_18_21'/'verify_all_exact.py'),
                '--root',str(ROOT/'z12_18_21'),'--jobs',str(max(1,min(4,os.cpu_count() or 1))),
                '--report',str(ROOT/'z12_18_21'/'reproduced_verification_report.json')],check=True)
subprocess.run([sys.executable,str(ROOT/'z12_18_21'/'mutation_tests.py')],check=True)
print('\n12-BY-18-THROUGH-22 GATE PASSED')
