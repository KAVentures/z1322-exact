# Reproducibility notes

The load-bearing verification uses only a C++17 compiler and the Python standard library.

Run `make verify` from the repository root. The scripts regenerate the finite degree-profile space, replay every exact rational or integer-scaled Farkas certificate, exhaustively enumerate all marked-row local cases used in the 13-by-22 proof, validate the 137-edge witness, replay the 12-by-18 certificate family, validate the five nested 12-row witnesses, and check the deletion chain through 12-by-22. The target also runs the corrected frontier package, which verifies the 13-by-18 certificate, six frontier witnesses, and the deletion consequences.

Discovery scripts under `proof/discovery/` are non-load-bearing. Floating-point solvers were used to find candidate dual separators, but all accepted separators are replayed exactly.

See `proof/ADVERSARIAL_AUDIT_FULL.md` for the current audit and remaining desirable independent checks.
