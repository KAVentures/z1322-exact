# Proof note: `Z(13,22,3,3)=137`

## 1. Statement

A binary `13 x 22` matrix is `K_3,3`-free when no three rows and three columns form an all-one submatrix. Equivalently, treat every column as a subset of the thirteen row labels. The condition is that every row triple is contained in at most two columns.

The package proves:

> **Theorem.** `Z(13,22,3,3)=137`.

The checked matrix in `data/z13_22_137_blocks.json` gives the lower bound. It remains to exclude 138 ones.

## 2. Global degree-profile reduction

For column degrees `d_j`, triple counting gives

\[
\sum_{j=1}^{22}\binom{d_j}{3}\le 2\binom{13}{3}=572.
\]

Exact degree enumeration leaves 83 profiles at 138 ones. Rational block-polytope separators exclude 77. A separate marked-row argument excludes `6^18 7^3 9^1`. The only profiles left are

\[
6^{16}7^6,
\quad 5^1 6^{14}7^7,
\quad 5^2 6^{12}7^8,
\quad 4^1 6^{13}7^8,
\quad 5^3 6^{10}7^9.
\]

The scripts `enumerate138.py` and `verify_138_reduction.py` independently replay this reduction.

## 3. Marked-row leave method

Fix a row `r`. For a row triple `T`, write

\[
\delta_T=2-\lambda_T\ge0,
\qquad
D_r=\sum_{T\ni r}\delta_T.
\]

Delete `r` from every column containing it. The resulting residual blocks live on twelve points. Define a leave multigraph `L_r` by giving the pair `{x,y}` multiplicity `delta_{rxy}`. It has total edge multiplicity `D_r`.

Suppose a residual point `x` lies in `u_{x,s}` residual blocks of size `s`. Pair capacity through `{r,x}` gives

\[
e_x=22-\sum_s(s-1)u_{x,s},
\]

where `e_x` is the degree of `x` in the leave. Also

\[
\sum_x u_{x,s}=s n_s,
\qquad
\sum_x e_x=2D_r.
\]

These identities give a finite list of point types. The C++ verifier exhaustively enumerates every loopless leave multigraph of maximum edge multiplicity two with the prescribed degrees.

Let `M` be the point-by-residual-block incidence matrix. Its Gram matrix is

\[
Q=MM^T,
\qquad
Q_{xx}=\sum_su_{x,s},
\qquad
Q_{xy}=2-\delta_{rxy}.
\]

Hence `rank(Q)` cannot exceed the number of residual blocks. When there are exactly twelve blocks, `det(Q)=det(M)^2` must be a nonnegative integer square. Modular rank tests and the determinant-square test discard most local cases without approximation.

For every surviving local case, the verifier considers all residual blocks compatible with the point types. The exact equations impose:

- every point's incidence in each block-size class;
- every pair's required multiplicity `2-delta_xy`;
- the number of blocks in each class.

If `Ax=b, x>=0` were feasible, it would include every integral local design. A stored integer-scaled Farkas vector `y` satisfies

\[
A^Ty\ge0,
\qquad
b^Ty<0,
\]

and therefore excludes the case exactly.

## 4. The common deficit-seven configuration

Four of the five profiles can force a row outside all degree-five columns with `D_r=7`. Local arithmetic leaves the possibilities `(a,b)=(5,5),(8,3),(11,1)`, where `a` and `b` count degree-six and degree-seven columns through `r`.

- `(11,1)` has no point-type distribution;
- all 8,641 leave graphs for `(5,5)` fail the rank condition;
- `(8,3)` leaves four Gram-surviving cases.

Three of those four have exact local Farkas certificates. The fourth is handled integrally:

1. there are exactly 285 possible systems for the three residual size-six blocks;
2. the typed-leave automorphism group partitions them into three orbits of sizes 15, 180, and 90;
3. the first two orbit representatives have no residual size-five completion;
4. the last has exactly four completions.

For each of those four local completions, and separately for each relevant global degree profile, a rational completion certificate excludes all remaining columns. This produces sixteen exact completion certificates.

## 5. Profile-by-profile finish

### `6^16 7^6`

The total marked-row deficit is 126 and every row deficit is `2 mod 5`. If no row has deficit 2 or 7, the total is at least `13*12=156`. Every deficit-two local type is impossible. Every deficit-seven type is impossible by the common analysis above. Thus this profile cannot occur.

### `5^1 6^14 7^7`

Let `c` record whether the row lies in the unique degree-five column. Deficits are `2-c mod 5`. Deficit 2 for `c=0` and deficit 1 for `c=1` are locally impossible. The next baseline is 7 outside and 6 inside. Its total is

\[
8\cdot7+5\cdot6=86,
\]

while the required total is 111. Since all increases occur in steps of five, some row attains the baseline. Outside rows are excluded by the common deficit-seven argument; all inside deficit-six cases fail point-type or rank screening.

### `5^2 6^12 7^8`

Let `c` be the number of the two degree-five columns containing the row. The initial cases `(c,D)=(0,2),(1,1),(2,0)` are locally impossible. The next baseline has total

\[
7\cdot13-10=81,
\]

compared with the required total 96, so a baseline row exists. Cases `c=0` and `c=1` reduce to the preceding arguments. For `c=2,D=5`, the possible `(a,b)` values are

\[
(10,1),(7,3),(4,5),(1,7).
\]

The last has no point types. The remaining cases yield respectively 195, 217, and 28 screened local instances, all carrying exact Farkas certificates.

### `5^3 6^10 7^9`

The initial cases for `c=0,1,2` are impossible. The baseline total is

\[
7\cdot13-15=76,
\]

while the required total is 81, so a baseline row exists. The branches `c=0,1,2` are already excluded. For `c=3,D=4`, the possible values are

\[
(a,b)=(8,2),(5,4),(2,6).
\]

Exact screening leaves 4,746, 656, and 3 instances. All 5,405 have exact integer-scaled rational Farkas certificates.

### `4^1 6^13 7^8`

There are nine rows outside and four rows inside the degree-four column. The minimum-residue baseline is

\[
9\cdot2+4\cdot4=34,
\]

and the required total is 84. If neither minimum occurred, the total would be at least 99. Outside deficit-two rows are impossible. For an inside deficit-four row, the residual degree-four column has size three. The two nontrivial local types leave 12 and 3 screened cases, all excluded by exact Farkas certificates.

Thus all five profiles are impossible, and no 138-one matrix exists.

## 6. Conclusion

The explicit 137-one witness and the 138-edge exclusion give

\[
\boxed{Z(13,22,3,3)=137}.
\]

## 7. Trust boundary

The load-bearing verification uses only:

- exhaustive integer enumeration in `local_screen_general.cpp`;
- Python standard-library integer and `Fraction` arithmetic;
- explicit finite Farkas certificates;
- an explicit 137-one witness.

Floating-point optimization was used only to discover certificates. A solver's feasibility status is never accepted as a premise.

The complete gate checks 125,983 block coefficients for the 139-edge proof, 390,039 for the initial 138-edge reduction, and 5,262,392 for the final local proof: 5,778,414 exact coefficient inequalities in total.
