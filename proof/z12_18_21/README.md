# Exact values of `Z(12,18;3,3)` through `Z(12,22;3,3)`

This archive contains the manuscript and complete reproducibility package for

\[
\boxed{Z(12,n;3,3)=6n\quad(18\le n\le22)}.
\]

## arXiv submission

The primary manuscript is `main.tex`. It is self-contained and uses no external
figures or bibliography files. The source of record is `main.tex`; upload the
source-only archive for arXiv. The bundled
`reference_pdf/Z1218_exact_108.pdf` is retained as a convenience/provenance
rendering of the earlier 12-by-18-only layout, not as a load-bearing proof
input. The combined manuscript is in the repository's `paper/main.tex`; this
subdirectory retains the standalone 12-by-18-through-22 proof package.

## One-command exact replay

From a clean extraction:

```bash
./verify.sh
```

The command:

1. verifies every file listed in `SHA256SUMS.txt`;
2. checks the explicit 103-one, 108-one, 114-one, 120-one, 126-one, and
   132-one witnesses;
3. replays 303 exact certificates proving `Z(12,17;3,3) <= 103`;
4. replays 51 exact certificates proving `Z(11,18;3,3) <= 101`;
5. replays all four exhaustive 109-edge terminal cases;
6. checks the deletion chain through `Z(12,22;3,3) <= 132`;
7. compares deterministic proof statistics with the reference report; and
8. runs adversarial mutation tests that must be rejected.

A successful run ends with:

```text
VERIFIED: Z(12,18,3,3)=108; Z(12,19,3,3)=114; Z(12,20,3,3)=120; Z(12,21,3,3)=126; Z(12,22,3,3)=132
ALL MUTATION TESTS PASSED
PACKAGE VERIFICATION PASSED
```

Set `JOBS=1 ./verify.sh` for a sequential replay. On Linux the script uses
`sha256sum`; on macOS it falls back to `shasum -a 256`. The verifier uses only Python's
standard library and exact arithmetic; no LP, MILP, SAT solver, floating-point
infeasibility result, or network access is used.

## Proof contents

- `main.tex` - manuscript source.
- `reference_pdf/` - reference manuscript rendering and provenance base.
- `tools/patch_reference_pdf.py` - optional, non-load-bearing PDF synchronization script.
- `verify_all_exact.py` - trusted exact checker.
- `certificates/z1217/` - 303 neighboring-bound certificates.
- `certificates/z1118/` - 51 neighboring-bound certificates.
- `certificates/z1218/` - four final exhaustive-case certificates.
- `data/` - explicit witnesses for the nested 12-by-18 through 12-by-22 family.
- `mutation_tests.py` - negative-control tests.
- `reports/` - reference replay report and log.
- `generators/` - optional, non-trusted discovery/regeneration scripts.
- `PROOF_NOTE.md` - detailed proof and certificate explanation.
- `STATUS.md` - claim boundary and review status.
- `CLAIM_BOUNDARY.md` - explicit statement of what is and is not claimed.
- `NOVELTY_AUDIT.md` - dated literature/public-preprint search record.
- `SHA256SUMS.txt` - integrity manifest.

## Trust boundary

The load-bearing proof base consists of the Python standard library,
`verify_all_exact.py`, and the hashed witness/certificate data. The generator
scripts and reference logs are retained for transparency but are not trusted by
the checker.

The result is internally exactly verified but has not yet undergone independent
expert reproduction or peer review.
