"""Independent check of the triangle-tree examples of Ma and Zhang (open problem (1) of the article):
in the graph G_h (9*2^h - 6 sites, maximum degree three) the set S of non-root apices is a stuck
tight set with fr(G - S) = 1, and reaching an augmentable tight set of the same size requires
exactly h exchanges.  fr is computed by integer programming (HiGHS); the minimum displacement
|S minus R| over independent sets R with one site in every triangle is an integer programme as well.

Run from the repository root:   python3 checks/triangle_tree_chain.py [HMAX]     (default 3)
"""
import sys
import numpy as np
import networkx as nx
from scipy.optimize import milp, LinearConstraint, Bounds

def build(h):
    """Root block 0 with children 1, 2, 3; block u > 0 of depth < h has children 2u+2, 2u+3.
    Site (u, 0) is the apex of block u; the root uses all three sites for its children."""
    depth = {0: 0, 1: 1, 2: 1, 3: 1}; children = {0: [1, 2, 3]}; nodes = [0, 1, 2, 3]; queue = [1, 2, 3]
    while queue:
        u = queue.pop(0); children[u] = []
        if depth[u] < h:
            for c in (2 * u + 2, 2 * u + 3):
                depth[c] = depth[u] + 1; children[u].append(c); nodes.append(c); queue.append(c)
    G = nx.Graph()
    for u in nodes:
        G.add_edges_from([((u, 0), (u, 1)), ((u, 1), (u, 2)), ((u, 0), (u, 2))])
        for c, slot in zip(children[u], [0, 1, 2] if u == 0 else [1, 2]): G.add_edge((u, slot), (c, 0))
    return G, nodes, {(u, 0) for u in nodes if u != 0}

def fr(G):
    """Minimum number of monochromatic bonds of a two-colouring."""
    vs = list(G); idx = {v: i for i, v in enumerate(vs)}; n = len(vs); E = [(idx[a], idx[b]) for a, b in G.edges()]
    m = len(E)
    if m == 0: return 0
    c = np.zeros(n + m); c[n:] = -1; A = []; ub = []
    for k, (a, b) in enumerate(E):                       # y_e = 1 only if the bond is bichromatic
        r = np.zeros(n + m); r[n + k] = 1; r[a] = -1; r[b] = -1; A.append(r); ub.append(0)
        r = np.zeros(n + m); r[n + k] = 1; r[a] = 1; r[b] = 1; A.append(r); ub.append(2)
    res = milp(c, constraints=LinearConstraint(np.array(A), -np.inf, ub), integrality=np.ones(n + m), bounds=Bounds(0, 1))
    return m - int(round(-res.fun))

def displacement(G, nodes, S):
    vs = list(G); idx = {v: i for i, v in enumerate(vs)}; n = len(vs); A = []; lb = []; ub = []
    for u in nodes:
        r = np.zeros(n); r[[idx[(u, k)] for k in range(3)]] = 1; A.append(r); lb.append(1); ub.append(1)
    for a, b in G.edges():
        r = np.zeros(n); r[idx[a]] = 1; r[idx[b]] = 1; A.append(r); lb.append(-np.inf); ub.append(1)
    c = np.array([-1.0 if v in S else 0.0 for v in vs])
    res = milp(c, constraints=LinearConstraint(np.array(A), lb, ub), integrality=np.ones(n), bounds=Bounds(0, 1))
    return len(S) - int(round(-res.fun))

for h in range(1, (int(sys.argv[1]) if len(sys.argv) > 1 else 3) + 1):
    G, nodes, S = build(h); B = len(nodes)
    assert G.number_of_nodes() == 9 * 2**h - 6 and max(d for _, d in G.degree()) == 3
    assert fr(G) == B and fr(G.subgraph(set(G) - S)) == 1                      # S is tight, one frustrated bond left
    assert all(any(w in S for w in G[v]) for v in G if v not in S)             # S is stuck
    d = displacement(G, nodes, S); assert d == h
    print(f"h={h}: sites={G.number_of_nodes()}, triangles={B}, fr={B}, |S|={B-1}, exchanges needed={d}")
