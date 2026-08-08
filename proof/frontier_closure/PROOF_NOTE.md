# Corrected frontier proof note

This package contains the exact certificate proof of

\[
Z(13,18;3,3)=116
\]

and the explicit witnesses and deletion consequences needed for

\[
Z(14,17;3,3)=118,\quad Z(14,18;3,3)=124,
\]
\[
Z(15,17;3,3)=126,\quad Z(15,18;3,3)=132.
\]

It also records a checked 132-edge witness and the published upper bound
\(Z(16,17;3,3)\le133\), hence
\[
132\le Z(16,17;3,3)\le133.
\]

## The certificate-backed core: `Z(13,18)=116`

The bundled dependency package certifies \(Z(12,17;3,3)=103\) and
\(Z(12,18;3,3)=108\). A hypothetical 117-edge \(13\times18\) matrix would
therefore have every row of degree nine and every column of degree at least
six. Triple counting leaves exactly 19 column-degree profiles. The verifier
reconstructs these profiles, replays 13 exact global Farkas certificates, and
handles the six surviving profiles by marked-row deficit averaging, point-type
enumeration, and 12 exact pair-orbit certificates. The 116-edge witness is
checked over all row triples. This proves the first equality.

## Safe deletion consequences

We use the density lemma in its one-row form: a matrix with \(e\) edges on
\(m\) rows has a row of degree at most \(\lfloor e/m\rfloor\), so deletion
leaves at least \(e-\lfloor e/m\rfloor\) edges.

The published upper table gives \(Z(13,17;3,3)\le110\). Thus a hypothetical
119-edge \(14\times17\) matrix would leave at least
\[
119-\lfloor119/14\rfloor=111>110,
\]
so \(Z(14,17)\le118\). The supplied 118-edge witness gives equality.

From \(Z(13,18)=116\), a hypothetical 125-edge \(14\times18\) matrix would
leave at least \(125-\lfloor125/14\rfloor=117>116\); the 124-edge witness
therefore gives \(Z(14,18)=124\).

From \(Z(14,17)=118\), a hypothetical 127-edge \(15\times17\) matrix would
leave at least \(127-\lfloor127/15\rfloor=119>118\). The new 126-edge witness
therefore gives \(Z(15,17)=126\).

From \(Z(14,18)=124\), a hypothetical 133-edge \(15\times18\) matrix would
leave at least \(133-\lfloor133/15\rfloor=125>124\). The 132-edge witness
therefore gives \(Z(15,18)=132\).

The 132-edge \(16\times17\) witness is independently checked in
`data/z16_17_132_witness_seed201.json`. The upper endpoint 133 is imported
from the published table; this package does not claim to exclude 133 edges.

## Boundary of an exploratory argument

If \(c_{ij}\) denotes the number of columns containing both rows \(i\) and
\(j\), deleting those rows removes \(d_i+d_j-c_{ij}\) edges, so the remaining
edge count is \(e-d_i-d_j+c_{ij}\). The earlier exploratory certificates based
on this reduction are not retained: the explicit 126-edge and 132-edge
witnesses rule out the former exact claims \(Z(15,17)=125\) and
\(Z(16,17)=130\), and no independently replayed certificate for the associated
upper-bound claim is included. The corrected theorem boundary is the one
stated above.

All load-bearing certificate and witness checks are performed by
`verify_all.py`, using only the Python standard library and exact integer
arithmetic. `mutation_tests.py` checks that corrupted witnesses and
certificates are rejected.
