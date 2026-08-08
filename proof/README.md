# Exact resolution of `Z(13,22,3,3)`

This package proves

\[
\boxed{Z(13,22,3,3)=137}.
\]

The lower bound is an explicit checked 137-one matrix. The upper bound is a finite exact proof that no 138-one matrix exists.

## Reproduce

Requirements:

- Python 3.9 or later;
- a C++17 compiler (`g++`);
- no Python third-party packages.

Run:

```bash
python3 verify_all.py
```

Expected final line:

```text
ALL EXACT-VALUE VERIFICATION GATES PASSED
```

On the development machine the complete gate took about 32 seconds.

## What the gate checks

1. the explicit 137-one witness is `K_3,3`-free;
2. all 27 degree profiles at 139 edges are impossible;
3. all 83 degree profiles at 138 edges are reduced exactly;
4. the 77 profiles with global rational separators are replayed;
5. the elementary exclusion of `6^18 7^3 9^1` is checked;
6. the five previously surviving profiles are excluded by exact local leave-graph enumeration, rank/determinant tests, local Farkas certificates, exhaustive local factorization, and global completion certificates;
7. 5,262,392 local candidate-block coefficient inequalities are checked with exact integer arithmetic.

The discovery phase used floating-point LP solvers to locate separators. Solver status is not part of the proof. The bundled verifier reconstructs the finite instances and checks the rational certificates exactly.

## Main files

- `PROOF_NOTE.md` — mathematical proof architecture;
- `verify_all.py` — one-command gate;
- `verify_138_full.py` — exclusion of the final five 138-edge profiles;
- `local_screen_general.cpp` — exact local type and leave-multigraph enumerator;
- `local_certs/` — exact local Farkas certificates;
- `completion_certs/` — exact global completion certificates;
- `data/z13_22_137_blocks.json` — lower-bound witness;
- `ADVERSARIAL_AUDIT_FULL.md` — trust boundary and failure-mode audit.

## Epistemic status

The artifact is an internally reproducible exact computer-assisted proof. It has not yet been independently audited, formally verified in a proof assistant, or peer reviewed. Priority and literature claims therefore remain provisional.
