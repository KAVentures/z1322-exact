# Reproducibility notes

The load-bearing verification uses a GCC- or Clang-compatible C++17 compiler and the Python standard library. The local enumerator uses the widely supported `__int128` extension for exact determinant arithmetic; GCC and Clang are the supported compiler families.

Run `make verify` from the repository root. The scripts regenerate the finite degree-profile space, replay every exact rational or integer-scaled Farkas certificate, exhaustively enumerate all marked-row local cases used in the proof, and validate the 137-edge witness. Set `CXX=clang++` or another GCC-/Clang-compatible compiler when `c++` is not the desired default.

The verification gate compiles its C++ helper in a temporary directory and leaves no generated binary in the checkout.

Discovery scripts under `proof/discovery/` are non-load-bearing. Floating-point solvers were used to find candidate dual separators, but all accepted separators are replayed exactly.

See `proof/ADVERSARIAL_AUDIT_FULL.md` for the current audit and remaining desirable independent checks.
