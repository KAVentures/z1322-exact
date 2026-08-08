# Certificate generators (not trusted)

These scripts were used to discover the compressed orbit trees:

- `z1217_orbit_proof.py`: 303 exclusions for 104 ones in `12 x 17`.
- `z1118_orbit_proof.py`: 51 exclusions for 102 ones in `11 x 18`.
- `no8_forced_orbit_proof.py`: the two `10,9^11` final cases.
- `row8_orbit_proof.py`: the two degree-8-row final cases.

They require NumPy and SciPy/HiGHS and may take substantial time. They are deliberately outside the trusted base: `verify_all_exact.py` reconstructs every orbit, inequality, branch, and rational calculation without importing these files or calling an optimization solver.
