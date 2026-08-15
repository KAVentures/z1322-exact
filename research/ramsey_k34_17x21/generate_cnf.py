#!/usr/bin/env python3
import argparse
import itertools


class CNF:
    def __init__(self):
        self.nv = 0
        self.clauses = []

    def var(self):
        self.nv += 1
        return self.nv

    def add(self, *lits):
        self.clauses.append(tuple(int(x) for x in lits))

    def atmost(self, xs, k):
        """Sinz sequential-counter encoding of sum(xs) <= k."""
        n = len(xs)
        if k >= n:
            return
        if k < 0:
            self.add()
            return
        if k == 0:
            for x in xs:
                self.add(-x)
            return
        s = [[self.var() for _ in range(k)] for _ in range(n - 1)]
        self.add(-xs[0], s[0][0])
        for j in range(1, k):
            self.add(-s[0][j])
        for i in range(1, n - 1):
            self.add(-xs[i], s[i][0])
            self.add(-s[i - 1][0], s[i][0])
            for j in range(1, k):
                self.add(-xs[i], -s[i - 1][j - 1], s[i][j])
                self.add(-s[i - 1][j], s[i][j])
            self.add(-xs[i], -s[i - 1][k - 1])
        self.add(-xs[n - 1], -s[n - 2][k - 1])

    def and3(self, a, b, c):
        y = self.var()
        self.add(-y, a)
        self.add(-y, b)
        self.add(-y, c)
        self.add(-a, -b, -c, y)
        return y

    def and3neg(self, a, b, c):
        y = self.var()
        self.add(-y, -a)
        self.add(-y, -b)
        self.add(-y, -c)
        self.add(a, b, c, y)
        return y

    def write(self, path):
        with open(path, "w", encoding="ascii") as f:
            f.write(f"p cnf {self.nv} {len(self.clauses)}\n")
            for clause in self.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")


def build(ncols, row0_degree, path):
    cnf = CNF()
    x = [[cnf.var() for _ in range(ncols)] for _ in range(17)]

    # Completeness of the symmetry split:
    # after a global color swap, total red incidence is at most floor(17*n/2),
    # hence some row has red degree <= floor(n/2).  Permute that row to row 0,
    # then permute columns so its red entries are first.
    for j in range(ncols):
        cnf.add(x[0][j] if j < row0_degree else -x[0][j])

    for a, b, c in itertools.combinations(range(17), 3):
        red = []
        blue = []
        for j in range(ncols):
            red.append(cnf.and3(x[a][j], x[b][j], x[c][j]))
            blue.append(cnf.and3neg(x[a][j], x[b][j], x[c][j]))
        cnf.atmost(red, 3)
        cnf.atmost(blue, 3)

    cnf.write(path)
    print(
        f"N={ncols} r={row0_degree} vars={cnf.nv} "
        f"clauses={len(cnf.clauses)} out={path}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=21)
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    build(args.n, args.r, args.out)
