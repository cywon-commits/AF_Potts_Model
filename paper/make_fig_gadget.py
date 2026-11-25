"""Figure of the reduction of Theorem 11 (fig_gadget.pdf). Panel (c) reads runs/cover_scan.log,
the output of `python3 cover_reduction.py scan K` for K = 3, 4, 5.
Run from the paper directory:  python3 make_fig_gadget.py"""
import re
from fractions import Fraction as F
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
C = {1: '#3b6fb6', 2: '#e08a2e', 3: '#f2d13c'}; M = {1: 'o', 2: 's', 3: '^'}
def pol(r, deg): return np.array([r*np.cos(np.radians(deg)), r*np.sin(np.radians(deg))])
def gadget(ax, truth):
    a = np.zeros(2); b = [pol(1.25, t) for t in (90, 210, 330)]; p = [pol(2.3, t) for t in (150, 270, 30)]
    Q = [(a, bj, 'ab') for bj in b] + [(p[0], b[0], 'pb'), (p[0], b[1], 'pb'), (p[1], b[1], 'pb'),
                                       (p[1], b[2], 'pb'), (p[2], b[2], 'pb'), (p[2], b[0], 'pb')]
    sA = 3 if truth else 1; sB = 1 if truth else 3; sd = 2
    for u, v, kind in Q:
        mid = (u + v) / 2; n = np.array([-(v - u)[1], (v - u)[0]]); n /= np.linalg.norm(n)
        if kind == 'pb' and np.dot(n, mid) < 0: n = -n
        d = mid + 0.55 * n
        for x, y in ((u, v), (u, d), (v, d)): ax.plot([x[0], y[0]], [x[1], y[1]], color='0.35', lw=1.2, zorder=1)
        ax.scatter(*d, s=55, marker=M[sd], color=C[sd], edgecolor='k', lw=0.6, zorder=3)
    for pj, t in zip(p, (150, 270, 30)):
        for dt in (-22, 22):
            e = pj + pol(0.95, t + dt); ax.plot([pj[0], e[0]], [pj[1], e[1]], color='0.35', lw=1.2, ls=(0, (3, 2)), zorder=1)
        ax.scatter(*pj, s=190, marker=M[sA], color=C[sA], edgecolor='k', lw=0.9, zorder=4)
    ax.scatter(*a, s=190, marker=M[sA], color=C[sA], edgecolor='k', lw=0.9, zorder=4)
    for bj in b: ax.scatter(*bj, s=190, marker=M[sB], color=C[sB], edgecolor='k', lw=0.9, zorder=4)
    ax.set_xlim(-3.6, 3.6); ax.set_ylim(-3.75, 3.1); ax.set_aspect('equal'); ax.axis('off')

def scan(path='../runs/cover_scan.log'):
    """{k: {'unsat': [(D3, gap), ...], 'sat': [...]}}; identical instances of a kind must agree."""
    out = {}
    for line in open(path):
        m = re.match(r'k=(\d+) (\w+)\s*\|(.*)', line)
        if not m: continue
        k, tag = int(m.group(1)), m.group(2)
        pts = [(F(a.strip()), F(b.strip())) for a, b in (t.split(':') for t in m.group(3).split('|'))]
        prev = out.setdefault(k, {}).setdefault(tag, pts)
        assert prev == pts, (k, tag)
    return out

fig = plt.figure(figsize=(13.2, 4.4)); gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.25], wspace=0.12)
ax = fig.add_subplot(gs[0]); gadget(ax, True);  ax.set_title('(a) true: side A in state 3', fontsize=11)
ax = fig.add_subplot(gs[1]); gadget(ax, False); ax.set_title('(b) false: side B in state 3', fontsize=11)
h = [Line2D([], [], marker=M[s], color='w', markerfacecolor=C[s], markeredgecolor='k', markersize=9, label=f'state {s}') for s in (1, 2, 3)]
h.append(Line2D([], [], color='0.35', ls=(0, (3, 2)), label='clause triangle'))
fig.legend(handles=h, loc='lower left', bbox_to_anchor=(0.16, 0.0), ncol=4, fontsize=9.5, frameon=False)
ax = fig.add_subplot(gs[2]); data = scan(); col = {3: '#3b6fb6', 4: '#2a9d5c', 5: '#b5483a'}
for k in sorted(data):
    x, y = zip(*data[k]['unsat'])
    ax.axvspan(k - 1, k, ymin=0, ymax=0.06, color=col[k], alpha=0.35, lw=0)
    ax.plot(x, y, marker='o', ms=5, color=col[k], label=f'$\\Delta={2*k}$ ($k={k}$), unsatisfiable')
    assert all(g == 0 for _, g in data[k]['sat'])
ax.plot([1, 5], [0, 0], color='k', lw=1.4, ls='--', label='satisfiable (all $k$)')
ax.set_xlabel('$D_3$', fontsize=11); ax.set_ylabel('$E_0-K$', fontsize=11); ax.set_ylim(-0.25, 3.3); ax.set_xlim(0.8, 5.2)
ax.legend(fontsize=9, loc='upper right', frameon=False); ax.set_title('(c)', fontsize=11, loc='left')
fig.savefig('figs/fig_gadget.pdf', bbox_inches='tight')
