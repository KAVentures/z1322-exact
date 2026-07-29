#!/usr/bin/env python3
"""Audit exhaustive case generation and guarded auxiliary encodings."""
from itertools import product
from math import comb
from generate_row8_profile_cnf import CNF,at_most,conditional_lex_ge,cases
from test_cardinality import dpll

cs=cases()
assert len(cs)==155
assert len({(tuple(c['profile']),tuple(c['selected'])) for c in cs})==155
for c in cs:
    assert len(c['profile'])==18 and sum(c['profile'])==101
    assert min(c['profile'])>=5
    assert sum(comb(d,3) for d in c['profile'])<=330
    assert len(c['selected'])==8 and len(c['unselected'])==10
    assert sorted(c['selected']+c['unselected'])==c['profile']
    assert sum(comb(d,2) for d in c['selected'])<=110

for n in range(1,6):
    for k in range(n+1):
        cnf=CNF();cnf.nvars=n+1;guard=n+1
        at_most(cnf,list(range(1,n+1)),k,guard)
        for bits in product([False,True],repeat=n):
            for gv in (False,True):
                assignment={i+1:bits[i] for i in range(n)};assignment[guard]=gv
                got=dpll([list(cl) for cl in cnf.clauses],assignment)
                want=(not gv) or sum(bits)<=k
                assert got==want,(n,k,bits,gv,got,want)

for n in range(1,6):
    cnf=CNF();cnf.nvars=2*n+1;guard=2*n+1
    A=list(range(1,n+1));B=list(range(n+1,2*n+1))
    conditional_lex_ge(cnf,A,B,guard)
    for left in product([False,True],repeat=n):
        for right in product([False,True],repeat=n):
            for gv in (False,True):
                assignment={A[i]:left[i] for i in range(n)}
                assignment.update({B[i]:right[i] for i in range(n)})
                assignment[guard]=gv
                got=dpll([list(cl) for cl in cnf.clauses],assignment)
                want=(not gv) or left>=right
                assert got==want,(n,left,right,gv,got,want)
print('PASS: 155-case audit and guarded encoding semantics')
