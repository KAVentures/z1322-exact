# Proof note: `Z(12,n;3,3)=6n` for `18 <= n <= 22`

## 1. Block formulation

Let the rows be `[12]={1,...,12}` and identify column `j` with its support `B_j subseteq [12]`. The matrix is `K_{3,3}`-free exactly when

\[
\lambda_T:=|\{j:T\subseteq B_j\}|\le 2
\qquad (T\in \binom{[12]}3).
\]

Repeated columns are allowed. Deleting ones preserves this property.

## 2. The 12-by-17 lower bound

The file `data/z12_17_103_witness_verified.csv` has 103 ones. Its column
degrees are `7,6^16`, its row degrees are

```text
9,9,8,8,8,9,9,8,8,8,8,11,
```

and the histogram of row-triple multiplicities is

```text
multiplicity 0:  14 triples
multiplicity 1:  57 triples
multiplicity 2: 149 triples.
```

Thus every row triple occurs at most twice and `Z(12,17;3,3) >= 103`.

## 3. The 12-by-18 lower bound

The file `data/z12_18_108_witness_verified.csv` has 108 ones. Its column degrees are all six, its row degrees are

```text
10,9,9,9,9,9,7,9,8,8,10,11,
```

and the histogram of row-triple multiplicities is

```text
multiplicity 0:   6 triples
multiplicity 1:  68 triples
multiplicity 2: 146 triples.
```

Thus every row triple occurs at most twice and `Z(12,18;3,3) >= 108`.

## 4. The 12-by-19 lower bound

The file `data/z12_19_114_witness_verified.csv` has 114 ones. Its column
degrees are all six, its row degrees are

```text
8,10,11,9,10,10,8,9,10,9,10,10,
```

and the histogram of row-triple multiplicities is

```text
multiplicity 0:   3 triples
multiplicity 1:  54 triples
multiplicity 2: 163 triples.
```

Thus every row triple occurs at most twice and `Z(12,19;3,3) >= 114`.

## 5. The 12-by-19 upper bound

If a valid `12 x 19` matrix had 115 ones, one column would have degree at
most `floor(115/19)=6`. Deleting it would leave at least 109 ones in a valid
`12 x 18` matrix, contradicting the already established upper bound
`Z(12,18;3,3) <= 108`. Therefore `Z(12,19;3,3) <= 114`.

## 6. Propagation through 12-by-22

The exact 12-by-18 certificate proves the starting upper bound. The minimum-column deletion lemma gives

\[
Z(12,n;3,3)\le\left\lfloor\frac{n}{n-1}Z(12,n-1;3,3)\right\rfloor.
\]

Applying it successively gives upper bounds 114, 120, 126, and 132 for
`n=19,20,21,22`. The five nested witness CSVs have respectively 108, 114,
120, 126, and 132 ones, so all five bounds are attained.

## 7. Two self-contained deletion bounds

### 3.1 The bound `Z(12,17;3,3) <= 103`

It suffices to exclude exactly 104 ones. If the sorted column degrees are
`c_1 >= ... >= c_17`, then

\[
\sum_j c_j=104,
\qquad
\sum_j\binom{c_j}{3}\le 2\binom{12}{3}=440.
\]

The verifier independently enumerates all nonincreasing integer degree sequences satisfying these constraints and obtains exactly 303 patterns. One orbit certificate excludes each pattern.

### 3.2 The bound `Z(11,18;3,3) <= 101`

Likewise, excluding exactly 102 ones reduces to the 51 nonincreasing degree patterns satisfying

\[
\sum_j c_j=102,
\qquad
\sum_j\binom{c_j}{3}\le 2\binom{11}{3}=330.
\]

The 51 certificates in `certificates/z1118/` exclude them all.

## 8. Reduction of 109 ones to four cases

Assume a valid `12 x 18` matrix has 109 ones.

If a column had degree at most five, deleting it would leave at least 104 ones in a `12 x 17` matrix, contradicting Section 3.1. Hence every column has degree at least six. Since their total degree is 109, the degree multiset is forced:

\[
7^1 6^{17}.
\]

If a row had degree at most seven, deleting it would leave at least 102 ones in an `11 x 18` matrix, contradicting Section 3.2. Hence every row has degree at least eight.

There are now two alternatives.

- A row of degree eight exists. Normalize one such row. The unique degree-seven column either contains it (**case A**) or avoids it (**case B**).
- No row has degree eight. Then every row has degree at least nine, and the row-degree sum 109 forces `10^1 9^11`. The unique degree-seven column either contains the degree-ten row (**case I**) or avoids it (**case O**).

These are exactly the four final certificate files in `certificates/z1218/`.

## 9. Orbit certificate framework

Fix some column supports. Two rows are placed in the same cell when they have the same membership signature in every fixed column. If the cell sizes are `n_1,...,n_s`, the row stabilizer is

\[
H=\operatorname{Sym}(n_1)\times\cdots\times\operatorname{Sym}(n_s).
\]

A candidate `k`-column orbit is represented by a profile
`p=(p_1,...,p_s)`, where `p_i` rows are chosen from cell `i`. Its orbit size is

\[
N_p=\prod_i\binom{n_i}{p_i}.
\]

A row-triple orbit is represented by `u=(u_1,...,u_s)` with `sum u_i=3`, and has size

\[
N_u=\prod_i\binom{n_i}{u_i}.
\]

A block of profile `p` contains

\[
h(u,p)=\prod_i\binom{p_i}{u_i}
\]

triples of profile `u`. If the already fixed columns contain each triple of this orbit `lambda_u` times and `x_p` is the number of remaining columns selected from orbit `p`, every completion satisfies

\[
\sum_p h(u,p)x_p\le (2-\lambda_u)N_u. \tag{1}
\]

The row-8 cases have a second, marked family: the columns containing the deleted row. A pair of residual rows may occur in at most two marked blocks, because adding the deleted row would otherwise form a forbidden row triple. Pair-orbit inequalities analogous to (1) are therefore included. Exact column counts and the required row-degree or absence budgets are included as additional linear inequalities.

## 10. Exact rational leaves

At a certificate node, the verifier reconstructs an integer system

\[
Ax\le b,
\qquad l\le x\le u,
\]

where `x` records orbit multiplicities. For any nonnegative rational vector `y`, every feasible integer or real `x` satisfies

\[
\mathbf 1^Tx
\le
\mathbf 1^Tl+y^T(b-Al)
+
\sum_j (u_j-l_j)\max\{0,1-(A^Ty)_j\}. \tag{2}
\]

A dual leaf stores nonnegative integer numerators over one positive common denominator. The verifier evaluates (2) with Python integers only. If its right side is strictly below the number of columns still required, the node is impossible.

An integer node branches exhaustively as

\[
x_j\le q
\quad\text{or}\quad
x_j\ge q+1.
\]

An outer node chooses the first occupied candidate orbit, fixes its canonical representative, and forbids all earlier orbits. Because the forbidden union is invariant under the current stabilizer, every completion is represented in exactly one child. Induction on the inner split tree and then on the outer orbit tree proves every accepted certificate exhaustive.

## 11. Certificate totals

| Component | Patterns/cases | Outer nodes | Inner nodes | Dual leaves | Integer branches |
|---|---:|---:|---:|---:|---:|
| `Z(12,17) <= 103` | 303 | 3,607 | 26,725 | 14,651 | 11,764 |
| `Z(11,18) <= 101` | 51 | 160 | 785 | 451 | 320 |
| Case I | 1 | 1 | 1 | 1 | 0 |
| Case O | 1 | 71 | 217 | 139 | 75 |
| Case A | 1 | 77 | 6,290 | 3,077 | 3,109 |
| Case B | 1 | 31 | 2,696 | 1,342 | 1,335 |

All counts are recomputed by `verify_all_exact.py`; generator statistics are not trusted.

## 12. Conclusion

The certificates give `Z(12,17;3,3) <= 103` and exclude all four forms of a
hypothetical 109-one 12-by-18 matrix. Therefore `Z(12,18;3,3) <= 108`. The
five explicit witnesses give the reverse inequalities, and the deletion
chain gives the corresponding upper bounds, so

\[
\boxed{Z(12,n;3,3)=6n\quad(18\le n\le22)}.
\]

## 13. Reproducibility and limitations

The trusted verifier uses the Python standard library and exact integer arithmetic. `mutation_tests.py` confirms that a corrupted witness, a corrupted rational leaf, and corrupted bridge metadata are rejected. `SHA256SUMS.txt` binds all load-bearing inputs.

The result is a computer-assisted proof awaiting independent expert reproduction and peer review. The included generation scripts use SciPy/HiGHS only to discover certificates and are outside the trust boundary.
