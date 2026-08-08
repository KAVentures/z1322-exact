# Corrected Zarankiewicz frontier package

This package contains a certificate-backed proof of

\[
Z(13,18;3,3)=116,
\quad Z(14,17;3,3)=118,
\quad Z(14,18;3,3)=124,
\]
\[
Z(15,17;3,3)=126,
\quad Z(15,18;3,3)=132.
\]

It also checks a 132-edge \(16\times17\) witness. Together with the published
upper bound \(Z(16,17;3,3)\le133\), the current certified interval is
\(132\le Z(16,17;3,3)\le133\). No exact value is asserted there.

## Reproduce

The trusted verifier uses Python 3.9+ and no third-party Python packages:

```bash
python3 verify_all.py
python3 mutation_tests.py
python3 frontier_propagation.py
```

The optional dependency replay is:

```bash
python3 verify_all.py --verify-dependency \
  --report reports/full_verification_report.json
```

The verifier is Python-3.9 compatible; it uses a standard-library population
count helper rather than `int.bit_count()`.

## Proof boundary

The `13 x 18` upper bound is replayed from 19 regenerated degree profiles, 13
global Farkas certificates, marked-row reductions, and 12 local orbit
certificates. All supplied witnesses are checked exhaustively over row triples.
The neighboring exact values use the one-row density deletion lemma and the
checked lower-bound witnesses. The upper bound 133 for `16 x 17` is an imported
published bound, not a new certificate in this directory.

Earlier exploratory two-row deletion certificates are not retained. With
row codegree (c_{ij}), deleting two rows leaves
`e - d_i - d_j + c_ij` edges; the explicit 126-edge and 132-edge witnesses
rule out the former exact claims `Z(15,17)=125` and `Z(16,17)=130`, while no
independently replayed certificate for the associated upper-bound claim is
included. See `PROOF_NOTE.md`.
