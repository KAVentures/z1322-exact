#!/usr/bin/env python3
from itertools import product
from generate_cnf import CNF,lex_ge
from test_cardinality import dpll
for n in range(1,7):
    cnf=CNF(); cnf.nvars=2*n; lex_ge(cnf,list(range(1,n+1)),list(range(n+1,2*n+1)))
    for left in product([0,1],repeat=n):
        for right in product([0,1],repeat=n):
            assignment={i+1:bool(left[i]) for i in range(n)}; assignment.update({n+i+1:bool(right[i]) for i in range(n)})
            got=dpll([list(c) for c in cnf.clauses],assignment); want=left>=right; assert got==want,(n,left,right,got,want)
print('PASS: exhaustive lex semantics for lengths <=6')
