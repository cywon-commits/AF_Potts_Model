"""Hardness reduction of Theorem 11 (maximum degree 2k, k-1 <= D3 < k).

Source problem: cubic monotone 1-in-3 SAT (n variables, n clauses, three distinct variables per
clause, three clauses per variable).
Variable gadget (7 core sites): ports p0,p1,p2 and hub a (side A), b0,b1,b2 (side B).
Odd cycles through one A and one B site: hub-b_j (x1), p_j-b_j (x alpha), b_j-p_{j+1} (x beta),
alpha+beta = k-1.  The first copy is a triangle (bond + private site), further copies are private
5-cycles.  Pads: k-3 private triangles at the hub.  Clause: triangle on one port of each variable.
Claim (k-1 <= D3 < k):  E0 >= K = (n/3)(10 D3 + 2k - 6), with equality iff 1-in-3 satisfiable.

Usage (from the repository root; needs ortools):
  python3 cover_reduction.py planar            planar instances, k = 3, 4
  python3 cover_reduction.py random K SEED N   N random cubic instances at k = K
  python3 cover_reduction.py scan K            E0 - K as a function of D3 (n = 6)
"""
import itertools, random, sys
import networkx as nx
from fractions import Fraction as F
from ortools.sat.python import cp_model

def build(n, clauses, k=3, ports=None):
    """ports[(x, ci)] = port index of variable x used by clause number ci (default: order of occurrence)."""
    G = nx.Graph(); cnt = itertools.count(); occ = {x: 0 for x in range(n)}
    al, be = (k - 1 + 1) // 2, (k - 1) // 2
    def cyc(u, v, first):
        if first:
            d = ('d', next(cnt)); G.add_edges_from([(u, v), (u, d), (v, d)])
        else:
            d1, d2, d3 = [('d', next(cnt)) for _ in range(3)]
            G.add_edges_from([(u, d1), (d1, v), (v, d2), (d2, d3), (d3, u)])
    for x in range(n):
        p = [('p', x, j) for j in range(3)]; b = [('b', x, j) for j in range(3)]; a = ('a', x)
        for j in range(3):
            cyc(a, b[j], True)
            for i in range(al): cyc(p[j], b[j], i == 0)
            for i in range(be): cyc(b[j], p[(j + 1) % 3], i == 0)
        for _ in range(k - 3):
            e1, e2 = ('d', next(cnt)), ('d', next(cnt)); G.add_edges_from([(a, e1), (e1, e2), (e2, a)])
    for ci, c in enumerate(clauses):
        assert len(set(c)) == 3
        pp = []
        for x in c:
            j = ports[(x, ci)] if ports else occ[x]; occ[x] += 1; pp.append(('p', x, j))
        G.add_edges_from(itertools.combinations(pp, 2))
    assert max(d for _, d in G.degree()) == 2 * k
    return G

def E0(G, D3, workers=8, fix_private=True):
    """Exact ground-state energy by CP-SAT. With fix_private, sites of degree two are restricted to
    states 1, 2 (allowed for D3 >= 1 by the threshold theorem)."""
    q = D3.denominator; m = cp_model.CpModel(); X = {}
    for v in G:
        if fix_private and G.degree(v) == 2:
            X[v] = [m.NewBoolVar(''), None, None]; X[v][1] = X[v][0].Not(); X[v][2] = None
        else:
            X[v] = [m.NewBoolVar('') for _ in range(3)]; m.AddExactlyOne(X[v])
    obj = []
    for u, v in G.edges():
        y = m.NewBoolVar('')
        for s in range(3):
            if X[u][s] is None or X[v][s] is None: continue
            m.AddBoolOr([X[u][s].Not(), X[v][s].Not(), y])
        obj.append(q * y)
    obj += [D3.numerator * X[v][2] for v in G if X[v][2] is not None]
    m.Minimize(sum(obj)); s = cp_model.CpSolver(); s.parameters.num_workers = workers
    st = s.Solve(m); assert st == cp_model.OPTIMAL, st
    return F(round(s.ObjectiveValue()), q)

def sat13(n, clauses):
    return any(all(sum(a[x] for x in c) == 1 for c in clauses) for a in itertools.product([0, 1], repeat=n))

def Kval(n, k, D3): return F(n, 3) * (10 * D3 + 2 * k - 6)

def random_cubic(n, rng):
    while True:
        slots = [x for x in range(n) for _ in range(3)]; rng.shuffle(slots)
        cl = [tuple(slots[3*i:3*i+3]) for i in range(n)]
        if all(len(set(c)) == 3 for c in cl): return cl

def planar_instance(H, var_nodes):
    """H: planar cubic bipartite incidence graph. Ports follow the rotation system of a planar embedding."""
    ok, emb = nx.check_planarity(H); assert ok
    vs = sorted(var_nodes); cs = sorted(set(H) - set(var_nodes)); vi = {v: i for i, v in enumerate(vs)}
    clauses, ports = [], {}
    for ci, c in enumerate(cs):
        clauses.append(tuple(vi[v] for v in H[c]))
    cidx = {c: i for i, c in enumerate(cs)}
    for v in vs:
        for j, c in enumerate(emb.neighbors_cw_order(v)): ports[(vi[v], cidx[c])] = j
    return len(vs), clauses, ports

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'planar':
        tests = {'cube': nx.hypercube_graph(3), 'hexagonal prism': nx.circular_ladder_graph(6),
                 'octagonal prism': nx.circular_ladder_graph(8), '12-prism': nx.circular_ladder_graph(12)}
        for name, H in tests.items():
            A, B = nx.bipartite.sets(H); n, cl, ports = planar_instance(H, A)
            sat = sat13(n, cl)
            for k in (3, 4):
                G = build(n, cl, k, ports); pl = nx.check_planarity(G)[0]
                out = f"{name:16s} k={k} n={n} N={G.number_of_nodes()} planar={pl} sat={sat}"
                for D3 in [F(k - 1), F(2 * k - 1, 2), F(5 * k - 1, 5)]:
                    out += f" | D3={D3}: E0-K={E0(G, D3) - Kval(n, k, D3)}"
                print(out, flush=True)
    if mode == 'random':
        k = int(sys.argv[2]); rng = random.Random(int(sys.argv[3])); trials = int(sys.argv[4]); bad = 0; ns = ny = 0
        for t in range(trials):
            n = rng.choice([3, 6, 6, 6, 9]); cl = random_cubic(n, rng); sat = sat13(n, cl); G = build(n, cl, k)
            for D3 in [F(k - 1), F(2 * k - 1, 2)]:
                gap = E0(G, D3) - Kval(n, k, D3)
                if gap < 0 or (gap == 0) != sat: bad += 1; print('VIOLATION', k, n, cl, D3, gap, sat)
            ns += sat; ny += not sat
        print(f"k={k}: {trials} random instances ({ns} sat, {ny} unsat), violations={bad}")
    if mode == 'small':                             # k = 3 below D3 = 1: no restriction on private sites
        rng = random.Random(int(sys.argv[2])); trials = int(sys.argv[3]); bad = 0; ns = ny = 0
        for t in range(trials):
            n = rng.choice([3, 3, 6]); cl = random_cubic(n, rng); sat = sat13(n, cl); G = build(n, cl, 3)
            for D3 in [F(1, 2), F(3, 2)]:
                gap = E0(G, D3, fix_private=False) - Kval(n, 3, D3)
                if gap < 0 or (gap == 0) != sat: bad += 1; print('VIOLATION', n, cl, D3, gap, sat)
            ns += sat; ny += not sat
        print(f"k=3, D3=1/2 and 3/2, private sites free: {trials} instances ({ns} sat, {ny} unsat), violations={bad}")
    if mode == 'scan':                              # where does the equivalence hold as a function of D3?
        k = int(sys.argv[2]); rng = random.Random(1)
        inst = []
        while len(inst) < 2:
            cl = random_cubic(6, rng)
            if not sat13(6, cl): inst.append(('unsat', cl))
        while len(inst) < 4:
            cl = random_cubic(6, rng)
            if sat13(6, cl): inst.append(('sat', cl))
        for tag, cl in inst:
            G = build(6, cl, k); out = f"k={k} {tag:5s}"
            for D3 in [F(1), F(3, 2), F(2), F(5, 2), F(3), F(7, 2), F(4), F(9, 2), F(5)]:
                if D3 > k: break
                out += f" | {D3}: {E0(G, D3) - Kval(6, k, D3)}"
            print(out, flush=True)
