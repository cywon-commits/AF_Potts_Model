"""Theorem 11, k = 3: unsatisfiable cubic monotone 1-in-3 instances with n = 6 have E0 > K.
Run from the repository root:  python3 cover_unsat_k3.py"""
import random, time
from fractions import Fraction as F
from cover_reduction import *
rng = random.Random(5); got = bad = tried = 0; t0 = time.time()
while got < 8 and time.time() - t0 < 420:
    cl = random_cubic(6, rng); tried += 1
    if sat13(6, cl): continue
    got += 1; G = build(6, cl, 3); gaps = []
    for D3 in [F(2), F(5, 2)]:
        gap = E0(G, D3) - Kval(6, 3, D3); gaps.append(str(gap))
        if gap <= 0: bad += 1; print('VIOLATION', cl, D3, gap)
    print(got, tried, gaps, round(time.time() - t0), flush=True)
print(f"k=3: {got} unsatisfiable n=6 instances out of {tried} sampled, violations={bad}")
