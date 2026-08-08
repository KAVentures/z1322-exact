#!/usr/bin/env python3
"""Exact standard-library verifier for a corrected finite-frontier package.

The package proves the exact values
    Z(13,18;3,3)=116, Z(14,17;3,3)=118, Z(14,18;3,3)=124,
    Z(15,17;3,3)=126, and Z(15,18;3,3)=132.
It also checks a 132-edge lower witness for Z(16,17;3,3); the imported
published upper bound is 133, so the certified interval is 132--133.

Trusted base: this source file, Python's standard library, and the bundled
certificate data.  Floating-point discovery scripts are not imported.

The proof uses the previously certified exact bounds Z(12,17)=103 and
Z(12,18)=108.  Their complete prior reproducibility package is bundled under
``dependencies/`` and its SHA-256 is checked here.  Use ``--verify-dependency``
to replay that package as well.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
from math import comb, prod
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M, N, E = 13, 18, 117
TRIPLES = tuple(combinations(range(M), 3))
PAIRS = tuple(combinations(range(M), 2))
DEPENDENCY_NAME = "Z1218_exact_108_REPRODUCIBILITY.zip"
# Filled from the bundled immutable archive at package assembly time.
DEPENDENCY_SHA256 = "3499036425840cc6d877817e918a5f55c4611bd5c04934e4c3f6eff1ae8f3ab8"

GLOBAL_EXCLUDED = {3, 5, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}
SURVIVING = {0, 1, 2, 4, 6, 7}


def C(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def popcount(x: int) -> int:
    """Python-3.9-compatible integer population count."""
    return bin(x).count("1")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify_witness(path: Path, m: int, n: int, edges: int) -> dict:
    """Directly verify a lower-bound witness from its column bitmasks."""
    obj = json.loads(path.read_text())
    assert obj["m"] == m and obj["n"] == n and obj["edges"] == edges
    masks = tuple(map(int, obj["column_masks"]))
    assert len(masks) == n and all(0 <= block < (1 << m) for block in masks)
    column_degrees = tuple(popcount(block) for block in masks)
    row_degrees = tuple(sum((block >> r) & 1 for block in masks) for r in range(m))
    assert sum(column_degrees) == edges
    histogram = Counter()
    for triple in combinations(range(m), 3):
        mask = sum(1 << r for r in triple)
        multiplicity = sum((block & mask) == mask for block in masks)
        assert multiplicity <= 2, (path.name, triple, multiplicity)
        histogram[multiplicity] += 1
    stored_hist = {int(k): int(v) for k, v in obj["triple_multiplicity_histogram"].items()}
    assert dict(sorted(histogram.items())) == dict(sorted(stored_hist.items()))
    assert tuple(obj["row_degrees"]) == row_degrees
    assert tuple(obj["column_degrees"]) == column_degrees
    csv_path = path.with_suffix(".csv")
    assert csv_path.is_file()
    with csv_path.open(newline="") as f:
        matrix = [tuple(map(int, row)) for row in csv.reader(f)]
    assert len(matrix) == m and all(len(row) == n for row in matrix)
    assert all(x in (0, 1) for row in matrix for x in row)
    reconstructed = tuple(
        sum(matrix[r][j] << r for r in range(m)) for j in range(n)
    )
    assert reconstructed == masks
    return {
        "file": str(path.relative_to(ROOT)),
        "m": m,
        "n": n,
        "edges": edges,
        "row_degrees": row_degrees,
        "column_degrees": column_degrees,
        "triple_multiplicity_histogram": dict(sorted(histogram.items())),
    }


def enumerate_column_profiles() -> tuple[tuple[int, ...], ...]:
    """All 18-column profiles of total degree 117 with every degree >= 6."""
    out: list[tuple[int, ...]] = []
    counts = [0] * (M + 1)

    def rec(d: int, left_n: int, left_sum: int, triple_sum: int) -> None:
        if d > M:
            if left_n == 0 and left_sum == 0 and triple_sum <= 2 * C(M, 3):
                out.append(tuple(counts))
            return
        for z in range(left_n + 1):
            if d * z > left_sum:
                break
            next_triples = triple_sum + z * C(d, 3)
            if next_triples > 2 * C(M, 3):
                break
            counts[d] = z
            rec(d + 1, left_n - z, left_sum - d * z, next_triples)
        counts[d] = 0

    rec(6, N, E, 0)
    return tuple(out)


def verify_global_certificate(path: Path, profiles: tuple[tuple[int, ...], ...]) -> dict:
    obj = json.loads(path.read_text())
    assert obj["m"] == M and obj["n"] == N and obj["e"] == E
    idx = int(path.name[1:4])
    hist = tuple(obj["hist"])
    assert idx < len(profiles) and hist == profiles[idx]
    cert = obj["cert"]
    fixed_degree = int(cert["fixed_degree"])
    assert hist[fixed_degree] > 0

    fixed = set(range(fixed_degree))
    remaining = list(hist)
    remaining[fixed_degree] -= 1
    active = [d for d, z in enumerate(remaining) if z]
    assert cert["thresholds"] == active
    expected_labels = [["degree", d] for d in active] + [["row", r] for r in range(M)]
    assert cert["labels"] == expected_labels

    alpha = list(map(int, cert["alpha"]))
    beta = list(map(int, cert["beta"]))
    assert all(a >= 0 for a in alpha)
    assert len(beta) == len(active) + M
    required_alpha = C(M, 3) + M + C(M, 2) + len(active) * C(M, 2)
    assert len(alpha) == required_alpha

    q = 0
    a_triple = alpha[q : q + len(TRIPLES)]
    q += len(TRIPLES)
    a_row = alpha[q : q + M]
    q += M
    a_pair = alpha[q : q + len(PAIRS)]
    q += len(PAIRS)
    a_threshold = []
    for _ in active:
        a_threshold.append(alpha[q : q + len(PAIRS)])
        q += len(PAIRS)
    assert q == len(alpha)

    # Reconstruct b^T alpha + e^T beta exactly.
    rhs = 0
    for a, triple in zip(a_triple, TRIPLES):
        rhs += a * (2 - int(set(triple) <= fixed))
    for r, a in enumerate(a_row):
        rhs += a * (132 - (C(fixed_degree - 1, 2) if r in fixed else 0))
    for pair, a in zip(PAIRS, a_pair):
        rhs += a * (22 - ((fixed_degree - 2) if set(pair) <= fixed else 0))
    for threshold, weights in zip(active, a_threshold):
        for pair, a in zip(PAIRS, weights):
            pair_capacity = 22 - ((fixed_degree - 2) if set(pair) <= fixed else 0)
            # Integer rounding cut: each selected degree >= threshold block
            # containing this pair consumes at least threshold-2 capacity.
            rhs += a * (pair_capacity // (threshold - 2))
    for j, d in enumerate(active):
        rhs += beta[j] * remaining[d]
    for r in range(M):
        rhs += beta[len(active) + r] * (9 - int(r in fixed))
    assert rhs == int(cert["rhs"]) < 0

    triple_index = {t: i for i, t in enumerate(TRIPLES)}
    pair_index = {p: i for i, p in enumerate(PAIRS)}
    degree_index = {d: i for i, d in enumerate(active)}
    min_coefficient = None
    variables = 0

    # Reconstruct every candidate block coefficient.  A true matrix would
    # yield a nonnegative multiplicity vector x; the checked dual combination
    # has all coefficients >= 0 but negative RHS, a Farkas contradiction.
    for d in active:
        for block in combinations(range(M), d):
            value = beta[degree_index[d]]
            value += sum(beta[len(active) + r] for r in block)
            value += sum(a_triple[triple_index[t]] for t in combinations(block, 3))
            value += C(d - 1, 2) * sum(a_row[r] for r in block)
            block_pairs = tuple(combinations(block, 2))
            value += (d - 2) * sum(a_pair[pair_index[p]] for p in block_pairs)
            for threshold, weights in zip(active, a_threshold):
                if d >= threshold:
                    value += sum(weights[pair_index[p]] for p in block_pairs)
            assert value >= 0, (path.name, d, block, value)
            min_coefficient = value if min_coefficient is None else min(min_coefficient, value)
            variables += 1

    assert min_coefficient == int(cert["mincoef"])
    return {
        "profile_index": idx,
        "fixed_degree": fixed_degree,
        "variables_checked": variables,
        "rhs": rhs,
        "minimum_coefficient": min_coefficient,
    }


# ---------- Exact verifier for local pair-packing orbit certificates ----------
LOCAL_V = 12


def cells_of(fixed: tuple[int, ...] | list[int]) -> tuple[tuple[int, ...], ...]:
    groups: defaultdict[int, list[int]] = defaultdict(list)
    for r in range(LOCAL_V):
        signature = sum(((block >> r) & 1) << j for j, block in enumerate(fixed))
        groups[signature].append(r)
    return tuple(tuple(groups[s]) for s in sorted(groups))


@lru_cache(None)
def orbit_profiles(cell_sizes: tuple[int, ...], k: int) -> tuple[tuple[int, ...], ...]:
    out: list[tuple[int, ...]] = []
    suffix = [0] * (len(cell_sizes) + 1)
    for i in range(len(cell_sizes) - 1, -1, -1):
        suffix[i] = suffix[i + 1] + cell_sizes[i]

    def rec(i: int, left: int, cur: list[int]) -> None:
        if i == len(cell_sizes):
            if left == 0:
                out.append(tuple(cur))
            return
        lo = max(0, left - suffix[i + 1])
        hi = min(cell_sizes[i], left)
        for x in range(lo, hi + 1):
            cur.append(x)
            rec(i + 1, left - x, cur)
            cur.pop()

    rec(0, k, [])
    return tuple(out)


def orbit_representative(cells: tuple[tuple[int, ...], ...], profile: tuple[int, ...]) -> int:
    return sum(1 << r for cell, x in zip(cells, profile) for r in cell[:x])


def orbit_size(cell_sizes: tuple[int, ...], profile: tuple[int, ...]) -> int:
    return prod(C(n, x) for n, x in zip(cell_sizes, profile))


def orbit_masks(cells: tuple[tuple[int, ...], ...], profile: tuple[int, ...]):
    choices = [
        tuple(sum(1 << r for r in subset) for subset in combinations(cell, x))
        for cell, x in zip(cells, profile)
    ]
    for selected in product(*choices):
        yield sum(selected)


def build_local_model(fixed, remaining, forbidden):
    cells = cells_of(tuple(fixed))
    sizes = tuple(map(len, cells))
    pair_orbits = []
    for pair_profile in orbit_profiles(sizes, 2):
        pair_mask = orbit_representative(cells, pair_profile)
        fixed_multiplicity = sum((block & pair_mask) == pair_mask for block in fixed)
        if fixed_multiplicity > 2:
            return cells, (), (), True
        pair_orbits.append((pair_profile, fixed_multiplicity, orbit_size(sizes, pair_profile)))

    fixed_counter = Counter(fixed)
    variables = []
    for k, needed in sorted(remaining.items(), reverse=True):
        if needed <= 0:
            continue
        for profile in orbit_profiles(sizes, k):
            representative = orbit_representative(cells, profile)
            if representative in forbidden.get(k, set()):
                continue
            osz = orbit_size(sizes, profile)
            # Blocks here have size >= 4. Three identical copies would repeat
            # each contained pair three times, so any support has multiplicity <=2.
            upper = min(needed, 2 * osz - (fixed_counter[representative] if osz == 1 else 0))
            if upper <= 0:
                continue
            incidences = tuple(
                prod(C(x, y) for x, y in zip(profile, pair_profile))
                for pair_profile, _, _ in pair_orbits
            )
            if any(
                fixed_mult == 2 and incidence
                for incidence, (_, fixed_mult, _) in zip(incidences, pair_orbits)
            ):
                continue
            variables.append((k, profile, representative, osz, upper, incidences))
    return cells, tuple(pair_orbits), tuple(variables), False


def local_aggregate_model(remaining, pair_orbits, variables):
    A, b = [], []
    for qi, (_, fixed_mult, osz) in enumerate(pair_orbits):
        A.append(tuple(v[5][qi] for v in variables))
        b.append((2 - fixed_mult) * osz)
    for k, number in sorted(remaining.items(), reverse=True):
        if number > 0:
            A.append(tuple(int(v[0] == k) for v in variables))
            b.append(number)
    return tuple(A), tuple(b)


def local_bound(A, b, lower, upper, weights, denominator):
    value = denominator * sum(lower)
    coverage = [0] * len(lower)
    for i, weight in weights.items():
        value += weight * (b[i] - sum(A[i][j] * lower[j] for j in range(len(lower))))
        for j, coefficient in enumerate(A[i]):
            coverage[j] += weight * coefficient
    for j in range(len(lower)):
        if coverage[j] < denominator:
            value += (upper[j] - lower[j]) * (denominator - coverage[j])
    return value


class LocalOrbitVerifier:
    def __init__(self):
        self.outer_nodes = 0
        self.inner_nodes = 0
        self.dual_leaves = 0
        self.integer_splits = 0

    def verify_inner(self, node, A, b, variables, need, lower, upper):
        self.inner_nodes += 1
        if any(lower[j] > upper[j] for j in range(len(lower))):
            return
        tag = node[0]
        if tag == "X":
            row = node[1]
            if row == -1:
                assert any(lower[j] > upper[j] for j in range(len(lower)))
            elif row == -2:
                assert not variables
            else:
                assert b[row] - sum(A[row][j] * lower[j] for j in range(len(lower))) < 0
            return
        if tag == "D":
            entries = node[1]
            denominator = 1 if not entries else entries[0][2]
            weights = {}
            previous = -1
            for row, numerator, q in entries:
                assert previous < row < len(A)
                assert numerator > 0 and q == denominator
                previous = row
                weights[row] = numerator
            assert local_bound(A, b, lower, upper, weights, denominator) < need * denominator
            self.dual_leaves += 1
            return
        assert tag == "I" and len(node) == 5
        j, cut, left, right = node[1:]
        assert lower[j] <= cut < upper[j]
        left_upper = list(upper)
        left_upper[j] = cut
        self.verify_inner(left, A, b, variables, need, list(lower), left_upper)
        right_lower = list(lower)
        right_lower[j] = cut + 1
        self.verify_inner(right, A, b, variables, need, right_lower, list(upper))
        self.integer_splits += 1

    def verify_outer(self, node, fixed, remaining, forbidden):
        self.outer_nodes += 1
        need = sum(max(0, n) for n in remaining.values())
        cells, pair_orbits, variables, bad = build_local_model(fixed, remaining, forbidden)
        if node[0] == "G":
            assert bad
            return
        assert not bad and need > 0
        A, b = local_aggregate_model(remaining, pair_orbits, variables)
        largest = max(k for k, n in remaining.items() if n > 0)
        candidates = sorted((v for v in variables if v[0] == largest), key=lambda v: v[1])
        if node[0] == "N":
            assert node == ["N", largest] and not candidates
            return
        if node[0] == "P":
            self.verify_inner(
                node[1], A, b, variables, need, [0] * len(variables), [v[4] for v in variables]
            )
            return
        assert node[0] == "B" and node[1] == largest and len(node[2]) == len(candidates) > 0
        prior = set(forbidden.get(largest, set()))
        for child, variable in zip(node[2], candidates):
            _, profile, representative, *_ = variable
            next_remaining = dict(remaining)
            next_remaining[largest] -= 1
            next_forbidden = {k: set(v) for k, v in forbidden.items()}
            next_forbidden[largest] = set(prior)
            self.verify_outer(child, fixed + [representative], next_remaining, next_forbidden)
            prior.update(orbit_masks(cells, profile))


def full_local_counts(obj: dict) -> dict[int, int]:
    if obj["format"] == "pair-orbit-generic-v1":
        return {int(k): int(v) for k, v in obj["counts"].items() if int(v) > 0}
    assert obj["format"] == "pair-orbit-a4-v1"
    counts = {int(k): int(v) for k, v in obj["remaining"].items() if int(v) > 0}
    for block in obj["fixed"]:
        degree = popcount(int(block))
        counts[degree] = counts.get(degree, 0) + 1
    return counts


def verify_local_certificate(path: Path, expected_counts: dict[int, int]) -> dict:
    with gzip.open(path, "rt", encoding="utf8") as f:
        obj = json.load(f)
    counts = full_local_counts(obj)
    assert counts == expected_counts, (path.name, counts, expected_counts)
    fixed = list(map(int, obj["fixed"]))
    remaining = {int(k): int(v) for k, v in obj["remaining"].items()}
    verifier = LocalOrbitVerifier()
    verifier.verify_outer(obj["tree"], fixed, remaining, {})
    return {
        "file": path.name,
        "counts": counts,
        "outer_nodes": verifier.outer_nodes,
        "inner_nodes": verifier.inner_nodes,
        "dual_leaves": verifier.dual_leaves,
        "integer_splits": verifier.integer_splits,
    }


# ---------- Exact necessary point-type screen for a marked row ----------

def point_type_feasible(residual_counts: dict[int, int]) -> bool:
    """Necessary feasibility of the twelve residual point incidence vectors.

    A residual block of size s through a residual point consumes s-1 of the
    pair capacity 22 through the marked row and that point.  The sum of point
    incidences in size-s blocks must be s*n_s.
    """
    sizes = tuple(sorted(residual_counts))
    multiplicities = tuple(residual_counts[s] for s in sizes)
    target = tuple(s * residual_counts[s] for s in sizes)
    point_types: list[tuple[int, ...]] = []

    def rec(i: int, cur: list[int], used_capacity: int) -> None:
        if i == len(sizes):
            point_types.append(tuple(cur))
            return
        s = sizes[i]
        for u in range(multiplicities[i] + 1):
            next_capacity = used_capacity + (s - 1) * u
            if next_capacity > 22:
                break
            cur.append(u)
            rec(i + 1, cur, next_capacity)
            cur.pop()

    rec(0, [], 0)

    @lru_cache(None)
    def dp(points_left: int, remaining_target: tuple[int, ...]) -> bool:
        if points_left == 0:
            return all(x == 0 for x in remaining_target)
        if any(x < 0 for x in remaining_target):
            return False
        for point_type in point_types:
            if all(point_type[i] <= remaining_target[i] for i in range(len(sizes))):
                nxt = tuple(remaining_target[i] - point_type[i] for i in range(len(sizes)))
                if dp(points_left - 1, nxt):
                    return True
        return False

    return dp(12, target)


def low_deficit_row_types(hist: tuple[int, ...]):
    active = tuple(d for d, number in enumerate(hist) if number)
    slack = 2 * C(M, 3) - sum(hist[d] * C(d, 3) for d in active)
    total_deficit = 3 * slack
    threshold = total_deficit // M
    out = []

    def rec(i: int, columns_left: int, cur: list[int]) -> None:
        if i == len(active):
            if columns_left != 0:
                return
            counts = tuple(cur)
            deficit = 132 - sum(c * C(d - 1, 2) for d, c in zip(active, counts))
            if 0 <= deficit <= threshold:
                residual = {d - 1: c for d, c in zip(active, counts) if c}
                out.append((deficit, counts, residual))
            return
        d = active[i]
        for c in range(min(hist[d], columns_left) + 1):
            cur.append(c)
            rec(i + 1, columns_left - c, cur)
            cur.pop()

    rec(0, 9, [])
    return active, slack, total_deficit, threshold, tuple(sorted(out))


def verify_new_upper_bound() -> dict:
    witness_specs = [
        ("z13_18_116_witness.json", 13, 18, 116),
        ("z14_17_118_witness.json", 14, 17, 118),
        ("z14_18_124_witness.json", 14, 18, 124),
        ("z15_17_126_witness.json", 15, 17, 126),
        ("z15_18_132_witness.json", 15, 18, 132),
        ("z16_17_132_witness_seed201.json", 16, 17, 132),
    ]
    witness_results = [
        verify_witness(ROOT / "data" / name, m, n, edges)
        for name, m, n, edges in witness_specs
    ]

    profiles = enumerate_column_profiles()
    assert len(profiles) == 19

    global_paths = sorted((ROOT / "certificates/global").glob("p*_f*.json"))
    assert len(global_paths) == 13
    global_results = [verify_global_certificate(path, profiles) for path in global_paths]
    excluded = {r["profile_index"] for r in global_results}
    assert excluded == GLOBAL_EXCLUDED
    assert set(range(19)) - excluded == SURVIVING

    # Verify every reusable local certificate independently before applying it.
    local_expected = [
        {5: 3, 6: 5, 7: 1},
        {5: 3, 6: 6},
        {5: 4, 6: 4, 7: 1},
        {5: 5, 6: 3, 7: 1},
        {5: 3, 6: 4, 7: 2},
        {5: 4, 6: 3, 7: 2},
        {5: 5, 6: 2, 7: 2},
        {5: 6, 6: 1, 7: 2},
        {5: 5, 6: 1, 7: 3},
        {5: 6, 7: 3},
        {5: 6, 6: 2, 9: 1},
    ]
    local_by_key = {}
    local_results = []
    for i, expected in enumerate(local_expected):
        result = verify_local_certificate(ROOT / f"certificates/local/pat{i:02d}.json.gz", expected)
        key = tuple(sorted(expected.items()))
        assert key not in local_by_key
        local_by_key[key] = result
        local_results.append(result)
    balanced = verify_local_certificate(
        ROOT / "certificates/local/balanced_a4.json.gz", {5: 4, 6: 5}
    )
    balanced_key = tuple(sorted({5: 4, 6: 5}.items()))
    assert balanced_key not in local_by_key
    local_by_key[balanced_key] = balanced
    local_results.append(balanced)

    profile_results = []
    for idx in sorted(SURVIVING):
        hist = profiles[idx]
        active, slack, total_deficit, threshold, row_types = low_deficit_row_types(hist)
        assert row_types, idx
        checked_types = []
        for deficit, counts, residual in row_types:
            feasible = point_type_feasible(residual)
            item = {
                "deficit": deficit,
                "column_incidence_counts": dict(zip(active, counts)),
                "residual_block_counts": residual,
                "point_type_feasible": feasible,
            }
            if feasible:
                key = tuple(sorted(residual.items()))
                assert key in local_by_key, (idx, deficit, residual)
                item["certificate"] = local_by_key[key]["file"]
            checked_types.append(item)
        # Every actual matrix has at least one row with D <= floor(sum D / 13).
        # Every possible such row type has just been shown impossible.
        profile_results.append(
            {
                "profile_index": idx,
                "column_profile": {d: hist[d] for d in active},
                "slack": slack,
                "total_row_deficit": total_deficit,
                "averaging_threshold": threshold,
                "low_deficit_row_types": checked_types,
                "conclusion": "impossible",
            }
        )

    assert len(global_results) + len(profile_results) == 19

    # Dependency arithmetic, reconstructed explicitly.
    # Z(12,17)<=103 implies Z(13,17)<=111: 112 edges would have a row
    # of degree at most floor(112/13)=8, leaving at least 104 edges.
    assert 112 // 13 == 8 and 112 - 8 == 104 > 103
    # Thus a 117-edge 13x18 candidate has minimum column degree 6.
    assert 117 - 5 == 112 > 111
    # Z(12,18)<=108 forces minimum row degree 9; total 117 forces 9^13.
    assert 117 - 8 == 109 > 108 and 13 * 9 == 117
    # New upper bound propagates to 14x18.
    assert 125 // 14 == 8 and 125 - 8 == 117 > 116

    # Published Table 4 gives Z(13,17)<=110.  Density deletion then gives
    # Z(14,17)<=118: a hypothetical 119-edge matrix has a row of degree at
    # most floor(119/14)=8, leaving at least 111 edges.
    assert 119 // 14 == 8 and 119 - 8 == 111 > 110

    # The new 126-edge witness closes Z(15,17): a hypothetical 127-edge
    # matrix has a row of degree at most floor(127/15)=8, leaving at least
    # 119 edges on 14x17, which exceeds the preceding bound 118.
    assert 127 // 15 == 8 and 127 - 8 == 119 > 118

    # Z(15,18)<=132 follows from Z(14,18)<=124 by deleting a minimum row
    # from a hypothetical 133-edge matrix.
    assert 133 // 15 == 8 and 133 - 8 == 125 > 124

    # The published Table 4 upper bound is Z(16,17)<=133.  Together with
    # the checked 132-edge witness this leaves the honest interval 132--133.
    assert 133 >= 132

    return {
        "status": "PASS",
        "exact_values": {
            "Z(13,18,3,3)": 116,
            "Z(14,17,3,3)": 118,
            "Z(14,18,3,3)": 124,
            "Z(15,17,3,3)": 126,
            "Z(15,18,3,3)": 132,
        },
        "interval": {"Z(16,17,3,3)": [132, 133]},
        "witnesses": witness_results,
        "corollary_uppers": [
            "Z(14,17,3,3) <= 118",
            "Z(14,18,3,3) <= 124",
            "Z(15,17,3,3) <= 126",
            "Z(15,18,3,3) <= 132",
            "Z(16,17,3,3) <= 133"
        ],
        "dependency_bounds": {"Z(12,17,3,3)": 103, "Z(12,18,3,3)": 108},
        "column_profiles": len(profiles),
        "global_certificates": len(global_results),
        "marked_row_profiles": len(profile_results),
        "local_orbit_certificates": len(local_results),
        "global_results": global_results,
        "local_results": local_results,
        "profile_results": profile_results,
    }


def verify_dependency_archive(replay: bool) -> dict:
    path = ROOT / "dependencies" / DEPENDENCY_NAME
    assert path.is_file()
    digest = sha256(path)
    assert digest == DEPENDENCY_SHA256, (digest, DEPENDENCY_SHA256)
    result = {"file": DEPENDENCY_NAME, "sha256": digest, "replayed": False}
    if replay:
        with tempfile.TemporaryDirectory(prefix="z1218-dependency-") as td:
            with zipfile.ZipFile(path) as zf:
                zf.extractall(td)
            dependency_jobs = max(1, min(8, os.cpu_count() or 1))
            command = [
                sys.executable, str(Path(td) / "verify_all_exact.py"),
                "--jobs", str(dependency_jobs),
                "--report", "dependency_verification_report.json",
            ]
            proc = subprocess.run(command, cwd=td, text=True, capture_output=True)
            if proc.returncode != 0:
                print(proc.stdout)
                print(proc.stderr, file=sys.stderr)
                raise SystemExit("dependency replay failed")
            assert "VERIFIED: Z(12,18,3,3)=108" in proc.stdout
            result["replayed"] = True
            result["final_output"] = proc.stdout.strip().splitlines()[-1]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-dependency",
        action="store_true",
        help="also fully replay the bundled Z(12,17)/Z(12,18) dependency package",
    )
    parser.add_argument("--report", default="reports/verification_report.json")
    args = parser.parse_args()

    dependency = verify_dependency_archive(args.verify_dependency)
    proof = verify_new_upper_bound()
    report = {"dependency": dependency, **proof}
    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(f"verified {proof['global_certificates']}/13 global Farkas certificates")
    print(f"verified {proof['local_orbit_certificates']}/12 local orbit certificates")
    print("excluded all 19 possible 117-edge column profiles")
    print("verified 6/6 explicit lower-bound witnesses")
    print("VERIFIED: Z(13,18,3,3) = 116")
    print("VERIFIED: Z(14,17,3,3) = 118")
    print("VERIFIED: Z(14,18,3,3) = 124")
    print("VERIFIED: Z(15,17,3,3) = 126")
    print("VERIFIED: Z(15,18,3,3) = 132")
    print("VERIFIED: 132 <= Z(16,17,3,3) <= 133")
    if args.verify_dependency:
        print("VERIFIED: bundled dependency proof replay passed")


if __name__ == "__main__":
    main()
