"""Lattice helpers used by paper/make_figs.py: faces of a straight-line planar drawing, the star
(3.12.12) lattice and the truncated rhombille lattice."""
import math

import numpy as np

from lattices3 import truncated, truncated_penrose, defect_honeycomb, random_cubic


def geometric_faces(n, edges, pos):
    """Faces of a straight-line planar drawing (outer face dropped)."""
    nbrs = {v: [] for v in range(n)}
    for u, v in edges:
        nbrs[u].append(v); nbrs[v].append(u)
    for v in nbrs:
        x0, y0 = pos[v]
        nbrs[v].sort(key=lambda w: math.atan2(pos[w][1] - y0, pos[w][0] - x0))
    seen = set(); faces = []
    for u in range(n):
        for v in nbrs[u]:
            if (u, v) in seen:
                continue
            f = []; a, b = u, v
            while (a, b) not in seen:
                seen.add((a, b)); f.append(a)
                L = nbrs[b]; i = L.index(a)
                a, b = b, L[(i - 1) % len(L)]
            faces.append(f)
    def area(f):
        return 0.5 * sum(pos[f[i]][0] * pos[f[(i + 1) % len(f)]][1] - pos[f[(i + 1) % len(f)]][0] * pos[f[i]][1] for i in range(len(f)))
    faces = [f for f in faces if area(f) > 0]          # keep one orientation (inner faces)
    big = max(faces, key=lambda f: abs(area(f)))
    return [f for f in faces if f is not big]


def star_lattice(L=7):
    """Honeycomb (Delaunay dual of triangular-lattice points), then truncated."""
    from lattices3 import delaunay_dual
    pts = np.array([(i + 0.5 * (j % 2), j * math.sqrt(3) / 2) for j in range(L) for i in range(L)])
    n, E, pos, info = delaunay_dual(pts)
    return truncated({v: tuple(pos[v]) for v in range(n)}, E)


def truncated_rhombille(L=5):
    """Rhombille tiling: triangular-lattice points (degree 6) + triangle centres (degree 3)."""
    from scipy.spatial import Delaunay
    pts = np.array([(i + 0.5 * j, j * math.sqrt(3) / 2) for j in range(L) for i in range(L)])
    tri = Delaunay(pts)
    Vpos = {("p", k): tuple(p) for k, p in enumerate(pts)}
    E = []
    for t_idx, t in enumerate(tri.simplices):
        c = pts[t].mean(axis=0)
        Vpos[("c", t_idx)] = tuple(c)
        for k in t:
            E.append((("c", t_idx), ("p", int(k))))
    return truncated(Vpos, E)
