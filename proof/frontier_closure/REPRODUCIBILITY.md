# Reproducibility

From this directory, run:

```bash
python3 verify_all.py
python3 mutation_tests.py
python3 frontier_propagation.py
```

For the dependency-complete replay, add `--verify-dependency` to the first
command. The trusted path uses only Python 3.9+ and the standard library. The
verifier reconstructs certificate inequalities and checks all witness row
triples with exact integer arithmetic.

The package intentionally separates certified statements from imported data:
the `Z(13,17;3,3)\le110` and `Z(16,17;3,3)\le133` endpoints are published
upper bounds used by the short deletion arguments. The `16 x 17` data here
proves only the 132-edge lower bound.
