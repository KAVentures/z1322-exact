# Proof-producing SAT attack on the final edge of Z(12,18,3,3)

This directory attacks a hypothetical 109-one `12 x 18` Boolean matrix with no all-one `3 x 3` submatrix.

The search is split exhaustively by minimum row degree.

* `no8`: all rows have degree at least 9. Since the total is 109, the row degrees are `10,9^11`. Row and column symmetry fix the degree-10 row as row 0, incident with columns 0--9.
* `row8`: a degree-8 row exists. Symmetry fixes it as row 0, incident with columns 0--7. Deleting any row leaves an `11 x 18` matrix with at most 101 ones, so every row has degree at least 8.

In both branches every column has degree at least 5: deleting a column of degree at most 4 would leave at least 105 ones on `12 x 17`, contradicting the established upper bound 104.

`generate_cnf.py` emits every `K_{3,3}` clause explicitly and uses a tested sequential counter for all cardinality constraints. Columns inside each marked-row incidence class are lexicographically sorted; this is a pure column-permutation symmetry break. `test_cardinality.py` and `test_lex.py` exhaustively check the auxiliary encodings on small instances.

The GitHub Actions workflow builds pinned CaDiCaL and DRAT-trim sources. An UNSAT result is accepted only after DRAT-trim verifies the emitted proof. A SAT result is independently decoded and checked by `verify_model.py`.
