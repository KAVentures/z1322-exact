# The Exact Zarankiewicz Number Z(13,22,3,3)

This repository contains a manuscript and an exact certificate-based computer-assisted proof of

\[
Z(13,22,3,3)=137.
\]

**Author:** Koyar Afrasyab  
**Email:** koyar@kinvectum.com

## Status

The internal exact-arithmetic verification gate passes. The result has not yet undergone external peer review or independent clean-room reproduction.

## Verify the theorem

Requirements:

- Python 3.9 or later
- a C++17 compiler (`g++` or compatible)

```bash
cd proof
python3 verify_all.py
```

Expected final line:

```text
ALL EXACT-VALUE VERIFICATION GATES PASSED
```

## Build the paper

A prebuilt PDF is in `paper/main.pdf`. To rebuild it:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Repository structure

- `paper/`: manuscript source, bibliography, witness visualization, and PDF
- `proof/`: witness, exact enumerators, certificates, audit, and verification scripts
- `.github/workflows/verify.yml`: continuous verification on pushes and pull requests

## Proof trust boundary

The final proof uses exhaustive integer enumeration, Python exact rational arithmetic, explicit Farkas certificates, and an explicit 137-edge witness. Floating-point optimization was used only during certificate discovery; no LP/MILP solver status is accepted as a premise.

## Citation

See `CITATION.cff`.

## License

Code and certificate-checking infrastructure are released under the MIT License. The manuscript text is released under CC BY 4.0; see `LICENSE-PAPER`.
