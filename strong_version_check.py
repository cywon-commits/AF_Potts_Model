"""Check the 18-site counterexample to the strong version of the healing theorem (Appendix A):
of its 13 Ising ground states (maximum cuts), exactly one is not healable, i.e. admits no set of
pairwise non-adjacent sites containing exactly one endpoint of each frustrated bond.

Run from the repository root:   python3 strong_version_check.py
"""
import json

import networkx as nx

from heal_moves import all_max_cuts, sat_for_cut

d = json.load(open("runs/strong_version_counterexample.json"))
n, E = d["n"], [tuple(e) for e in d["edges"]]
G = nx.Graph(); G.add_edges_from(E)
fr, cuts = all_max_cuts(n, E)
healable = [sat_for_cut(n, E, t) for t in cuts]
print(f"n={n}, bonds={len(E)}, planar={nx.check_planarity(G)[0]}, fr={fr}, "
      f"Ising ground states={len(cuts)}, healable={sum(bool(h) for h in healable)}")
assert fr == d["fr"] and len(cuts) == d["n_max_cuts"] and sum(bool(h) for h in healable) == d["healable_cuts"]
