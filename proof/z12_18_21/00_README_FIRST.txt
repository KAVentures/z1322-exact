ARXIV / REPRODUCIBILITY BUNDLE
==============================

Main manuscript source: main.tex
Reference paper rendering: reference_pdf/Z1218_exact_108.pdf
The combined manuscript states Z(12,n;3,3)=6n for 18<=n<=22, alongside
the separate Z(13,22;3,3)=137 theorem.

To reproduce the complete computer-assisted proof from a clean extraction:

    ./verify.sh

The verification requires Python 3 and standard Unix tools only. The trusted
proof checker itself uses only the Python standard library and exact integer /
rational arithmetic. The generator scripts under generators/ are included for
provenance but are not part of the trusted proof base.

A successful replay ends with:

    VERIFIED: Z(12,18,3,3)=108; Z(12,19,3,3)=114; Z(12,20,3,3)=120; Z(12,21,3,3)=126; Z(12,22,3,3)=132
    ALL MUTATION TESTS PASSED
    PACKAGE VERIFICATION PASSED

For arXiv, select main.tex as the primary TeX file if prompted.
