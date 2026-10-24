"""Exhaustive check of the q-state generalisation (Remark in Sec. V):
if max degree <= q and no component is K_{q+1}, then ioct_{q-1}(G) = fr_{q-1}(G), where
fr_{q-1} is the minimum number of monochromatic bonds of a (q-1)-colouring and ioct_{q-1} the
minimum size of an independent set whose removal leaves a (q-1)-colourable graph.

Usage:  nauty-geng -c -D4 N | python3 checks/healing_general_q.py 4
(reads graph6 from stdin; brute force over all colourings, so N <= 10 is practical)
"""
import sys, itertools
import numpy as np
import networkx as nx

q = int(sys.argv[1])
cache = {}
def colourings(n, k):
    if (n, k) not in cache:
        cache[(n, k)] = np.array(list(itertools.product(range(k), repeat=n)), dtype=np.int8)
    return cache[(n, k)]

tot = nontriv = bad = 0
for line in sys.stdin:
    G = nx.from_graph6_bytes(line.strip().encode())
    n = G.number_of_nodes(); E = np.array(G.edges())
    tot += 1
    if n == q + 1 and G.number_of_edges() == n * (n - 1) // 2:
        continue                                   # K_{q+1}: excluded
    C = colourings(n, q - 1)
    fr = int((C[:, E[:, 0]] == C[:, E[:, 1]]).sum(1).min())
    if fr == 0:
        continue
    nontriv += 1
    C = colourings(n, q)                           # colour q-1 = costly state
    proper = (C[:, E[:, 0]] != C[:, E[:, 1]]).all(1)
    ioct = int((C[proper] == q - 1).sum(1).min()) if proper.any() else None
    if ioct != fr:
        bad += 1; print("counterexample", line.strip(), fr, ioct)
print(f"q={q}: graphs={tot}, non-(q-1)-colourable={nontriv}, counterexamples={bad}")
