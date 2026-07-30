#!/usr/bin/env python3
from itertools import product
from generate_cnf import CNF,at_most,at_least,exactly
def dpll(clauses,assign):
    while True:
        changed=False; reduced=[]
        for clause in clauses:
            sat=False; undec=[]
            for lit in clause:
                var=abs(lit)
                if var in assign:
                    if assign[var]==(lit>0): sat=True; break
                else: undec.append(lit)
            if sat: continue
            if not undec: return False
            if len(undec)==1:
                lit=undec[0]; var=abs(lit); value=lit>0
                if var in assign and assign[var]!=value: return False
                if var not in assign: assign[var]=value; changed=True
            reduced.append(undec)
        clauses=reduced
        if not changed: break
    if not clauses: return True
    var=abs(clauses[0][0])
    for value in (False,True):
        child=dict(assign); child[var]=value
        if dpll(clauses,child): return True
    return False
def sat_extension(clauses,bits): return dpll([list(c) for c in clauses],{i+1:bool(b) for i,b in enumerate(bits)})
for n in range(1,8):
    for k in range(n+1):
        tests=[('at_most',at_most,lambda s,k=k:s<=k),('at_least',at_least,lambda s,k=k:s>=k),('exactly',exactly,lambda s,k=k:s==k)]
        for kind,fn,predicate in tests:
            cnf=CNF(); cnf.nvars=n; fn(cnf,list(range(1,n+1)),k)
            for bits in product([False,True],repeat=n):
                got=sat_extension(cnf.clauses,bits); want=predicate(sum(bits)); assert got==want,(n,k,kind,bits,got,want)
print('PASS: exhaustive cardinality semantics for n<=7')
