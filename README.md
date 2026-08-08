# Exact Zarankiewicz Values on Two Finite Frontier Slices

This repository contains one combined manuscript and three exact certificate-based computer-assisted proof systems:

\[
Z(12,n,3,3)=6n\ (18\le n\le22),\qquad Z(13,22,3,3)=137,
\]
\[
Z(13,18,3,3)=116,\ Z(14,17,3,3)=118,\ Z(14,18,3,3)=124,
\]
\[
Z(15,17,3,3)=126,\ Z(15,18,3,3)=132,
\qquad 132\le Z(16,17,3,3)\le133.
\]

**Author:** Koyar Afrasyab  
**Email:** koyar@kinvectum.com

The values at `n=18,19,20,21`, the 13-by-22 upper bound, the four neighboring
frontier equalities, and the 132-edge 16-by-17 construction are the assembled
claims. The `n=22` value and the 3-(12,6,2) design are explicitly treated as
prior/classical material.

## Status

The internal exact-arithmetic verification gates pass. The results have not yet undergone external peer review or independent clean-room reproduction.

## Verify the theorem

Requirements:

- Python 3.9 or later
- a C++17 compiler (`g++` or compatible)

```bash
cd proof
python3 verify_all.py
cd frontier_closure
./verify_release.sh
```

Expected final lines:

```text
ALL EXACT-VALUE VERIFICATION GATES PASSED
12-BY-18-THROUGH-22 GATE PASSED
RELEASE VERIFICATION PASSED
```

## Build the paper

A prebuilt PDF is in `paper/main.pdf`. To rebuild it:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Repository structure

- `paper/`: combined manuscript, bibliography, witness visualization, and PDF
- `proof/`: the 13-by-22 certificates, `proof/z12_18_21/`, and the corrected `proof/frontier_closure/` package
- `.github/workflows/verify.yml`: continuous verification on pushes and pull requests

## Proof trust boundary

The final proof uses exhaustive integer enumeration, Python exact rational arithmetic, explicit Farkas certificates, and explicit lower-bound witnesses. Floating-point optimization was used only during certificate discovery; no LP/MILP solver status is accepted as a premise. Earlier exploratory two-row deletion certificates are not retained: the explicit 126-edge and 132-edge witnesses rule out the former exact claims `Z(15,17)=125` and `Z(16,17)=130`, and no independently replayed certificate for the associated upper-bound claim is included.

## Citation

See `CITATION.cff`.

## License

Code and certificate-checking infrastructure are released under the MIT License. The manuscript text is released under CC BY 4.0; see `LICENSE-PAPER`.
