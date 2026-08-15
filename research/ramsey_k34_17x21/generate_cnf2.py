#!/usr/bin/env python3
import argparse
import itertools
from generate_cnf import CNF


def build(ncols, r, s, a, path):
    if not (0 <= r <= s <= ncols):
        raise SystemExit("require 0 <= r <= s <= n")
    if not (0 <= a <= min(r, s) and r + s - a <= ncols):
        raise SystemExit("invalid overlap")

    cnf = CNF()
    x = [[cnf.var() for _ in range(ncols)] for _ in range(17)]

    # Canonical column classes for the two lowest-degree rows:
    # (11), (10), (01), (00).
    sizes = [a, r - a, s - a, ncols - r - s + a]
    bits = [(1, 1), (1, 0), (0, 1), (0, 0)]
    p = 0
    for size, (b0, b1) in zip(sizes, bits):
        for j in range(p, p + size):
            cnf.add(x[0][j] if b0 else -x[0][j])
            cnf.add(x[1][j] if b1 else -x[1][j])
        p += size

    # row 1 is the second-lowest red degree, so every remaining row has
    # degree at least s.  Encode number of zeroes <= n-s.
    for i in range(2, 17):
        cnf.atmost([-x[i][j] for j in range(ncols)], ncols - s)

    # Exact avoidance condition: every triple has at most 3 all-red and
    # at most 3 all-blue columns.
    for u, v, w in itertools.combinations(range(17), 3):
        red = []
        blue = []
        for j in range(ncols):
            red.append(cnf.and3(x[u][j], x[v][j], x[w][j]))
            blue.append(cnf.and3neg(x[u][j], x[v][j], x[w][j]))
        cnf.atmost(red, 3)
        cnf.atmost(blue, 3)

    cnf.write(path)
    print(
        f"N={ncols} branch=({r},{s},{a}) vars={cnf.nv} "
        f"clauses={len(cnf.clauses)} out={path}"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=21)
    p.add_argument("--r", type=int, required=True)
    p.add_argument("--s", type=int, required=True)
    p.add_argument("--a", type=int, required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    build(args.n, args.r, args.s, args.a, args.out)
