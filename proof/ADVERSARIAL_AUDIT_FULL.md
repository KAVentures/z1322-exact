# Adversarial audit of the exact-value package

## Claims actually made

- the bundled 137-one matrix is `K_3,3`-free;
- no 138-one `13 x 22` matrix is `K_3,3`-free;
- therefore `Z(13,22,3,3)=137`.

## Failure modes explicitly checked

1. **Missing degree profiles.** All degrees 0 through 13 are enumerated. No informal degree window is assumed.
2. **Hidden simplicity assumption.** Column multiplicities are variables; repeated columns are allowed.
3. **Omitted leave graphs.** The local generator enumerates every multigraph realization with edge multiplicity 0, 1, or 2 for every exact point-degree sequence.
4. **Unsafe modular rank inference.** Modular rank is used only one way: a true incidence factorization with `q` columns has rank at most `q` over every field. Cases passing the modular tests are retained, not discarded.
5. **Unsafe determinant inference.** The square-determinant filter is used only when the incidence matrix would be square. Then `det(MM^T)=det(M)^2` is necessary.
6. **Trusting an LP/MILP status.** No solver status appears in the final proof. Every infeasible relaxation has a stored rational Farkas separator replayed exactly.
7. **Symmetry dropping cases.** The only symmetry reduction in the integral local branch explicitly constructs all 8,640 permutations used, verifies that each preserves point types and leave multiplicities, and canonically covers all 285 systems.
8. **Assuming a unique local completion.** The verifier finds all four completions of the surviving orbit representative and supplies a separate global certificate for each.
9. **Floating-point rounding.** Local certificates are stored after multiplication by a common denominator and replayed using integers. Completion certificates use `Fraction` arithmetic.
10. **Invalid lower-bound transcription.** The witness is checked by exhaustive enumeration of all 286 row triples.

## Mutation tests still desirable before publication

- corrupt one coefficient in each certificate family and confirm rejection;
- implement an independent local enumerator in a second language;
- replay the theorem in Lean, Isabelle, or Coq;
- obtain an external combinatorics expert's audit of the marked-row reduction;
- conduct a systematic priority search beyond ordinary web and arXiv indexing.

## Remaining epistemic limitations

This is a computer-assisted exact proof package, not yet a peer-reviewed theorem. The verifier and proof architecture have been internally adversarially checked, but independent reproduction is still required before a strong public priority claim.
