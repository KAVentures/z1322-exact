#!/usr/bin/env python3
import argparse
import itertools


def parse_model(path):
    lits = []
    status = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("s "):
                status = line.strip()
            if line.startswith("v "):
                lits.extend(int(x) for x in line.split()[1:] if x != "0")
    return status, {abs(x): x > 0 for x in lits}


def verify(ncols, log_path):
    status, model = parse_model(log_path)
    if status is None or "SATISFIABLE" not in status or "UNSATISFIABLE" in status:
        raise SystemExit(f"not a SAT model: {status}")
    needed = 17 * ncols
    if any(v not in model for v in range(1, needed + 1)):
        raise SystemExit("solver model omits a matrix variable")
    x = [[model[1 + i * ncols + j] for j in range(ncols)] for i in range(17)]
    for a, b, c in itertools.combinations(range(17), 3):
        red = sum(x[a][j] and x[b][j] and x[c][j] for j in range(ncols))
        blue = sum((not x[a][j]) and (not x[b][j]) and (not x[c][j]) for j in range(ncols))
        if red > 3 or blue > 3:
            raise SystemExit(f"invalid triple {(a,b,c)} red={red} blue={blue}")
    print("SAT WITNESS VERIFIED")
    for row in x:
        print("".join("1" if z else "0" for z in row))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--log", required=True)
    a = p.parse_args()
    verify(a.n, a.log)
