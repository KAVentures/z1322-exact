# Proof-producing SAT attack on the final edge of Z(12,18,3,3)

This directory attacks a hypothetical 109-one `12 x 18` Boolean matrix with no all-one `3 x 3` submatrix.

The search is split exhaustively by minimum row degree.

* `no8`: all rows have degree at least 9. Since the total is 109, the row degrees are `10,9^11`. Row and column symmetry fix the degree-10 row as row 0, incident with columns 0--9.
* `row8`: a degree-8 row exists. Symmetry fixes it as row 0, incident with columns 0--7. Deleting this row leaves a 101-edge `11 x 18` extremal design. Since `Z(11,17,3,3)=96`, every old column has degree at least 5.

`generate_cnf.py` emits every `K_{3,3}` clause explicitly and uses a tested sequential counter for cardinality constraints. Columns inside each marked-row incidence class are lexicographically sorted; this is a pure column-permutation symmetry break. `test_cardinality.py` and `test_lex.py` exhaustively check the auxiliary encodings on small instances.

The workflow accepts UNSAT only after DRAT-trim verifies CaDiCaL's emitted proof. A SAT result is decoded and independently checked by `verify_model.py` against the original 109-edge matrix problem.
