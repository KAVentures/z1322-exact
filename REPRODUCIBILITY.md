# Reproducibility notes

The load-bearing verification uses only a C++17 compiler and the Python standard library.

Run `make verify` from the repository root. The scripts regenerate the finite degree-profile space, replay every exact rational or integer-scaled Farkas certificate, exhaustively enumerate all marked-row local cases used in the proof, and validate the 137-edge witness.

Discovery scripts under `proof/discovery/` are non-load-bearing. Floating-point solvers were used to find candidate dual separators, but all accepted separators are replayed exactly.

See `proof/ADVERSARIAL_AUDIT_FULL.md` for the current audit and remaining desirable independent checks.
