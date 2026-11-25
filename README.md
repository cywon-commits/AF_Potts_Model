# AF_Potts_Model

Code and data for

> J. Choi, S. Yoo, C. Kim, H. Y. Kwon, and C. Won,
> *Coordination three heals, coordination four is hard: the antiferromagnetic Potts model with a costly third state.*

The model is the antiferromagnetic three-state Potts model with an on-site energy cost $D_3$ for
the third state,

    E(s) = sum_<uv> delta(s_u, s_v) + D3 * #{sites in state 3},   s : V -> {1, 2, 3},

on arbitrary (mostly planar) lattices. The repository contains the exact solvers, the
certification and constructive healing algorithms, every script that produces a number, table or
figure of the article and its Supplemental Material, the raw data, and the LaTeX sources.

## Setup

```
pip install -r requirements.txt       # networkx, numpy, scipy (HiGHS), matplotlib, ortools
```

Python 3.10 or later. Some checks enumerate graphs with `nauty-geng` (Debian/Ubuntu package
`nauty`). Run every script from the repository root unless noted. To build the article you need
TeX Live with REVTeX 4.2 (`texlive-publishers`):

```
cd paper && latexmk -pdf supplementary.tex && latexmk -pdf main.tex
```

`main.tex` appends the pages of the compiled `supplementary.pdf` after its references (with `graphicx`), so
the Supplemental Material must be compiled first.

## Layout

| Path | Contents |
|---|---|
| `*.py` (root) | solvers, algorithms, lattice generators and the main reproduction scripts |
| `checks/` | additional verification scripts for the healing theorem and its constructive version |
| `runs/` | raw logs and data: exhaustive enumeration, greedy augmentation, timing, the Δ = 4 reduction test, the 18-site counterexample |
| `penrose_runs/` | exact energy curves of the ten Penrose patches, the 140-rhombus ground states |
| `supp_runs/` | evidence for Supplemental Note A (`planarity_evidence.json`) |
| `paper/` | LaTeX sources, bibliography, figures and the figure scripts |

### Core modules

| File | Purpose |
|---|---|
| `potts_exact.py` | exact minimum of E(s) by mixed-integer programming (HiGHS); exact energy envelope `curve()` |
| `ising_tjoin.py` | planar Ising ground state as a minimum T-join (matching in the dual) |
| `heal_check.py` | certification algorithm: Ising ground state + 2-SAT choice of endpoints |
| `constructive_heal.py` | constructive healing: greedy augmentation + exchange chain (fr-oracle version) and `heal_from_ground_state` (one Ising ground state suffices) |
| `heal_moves.py`, `heal_core.py` | enumeration of maximum cuts and healability per cut |
| `lattices3.py`, `deg3_lattices.py`, `penrose.py` | coordination-three lattices (truncated Penrose, Voronoi foam, defect honeycomb, star, truncated rhombille) and Penrose P3 patches (de Bruijn pentagrid) |
| `cnr_reduction.py` | the planar Δ = 4 reduction graph of Choi, Nakajima and Rim |
| `cover_reduction.py` | the Δ = 2k reduction of Theorem 11 from cubic planar monotone 1-in-3 SAT, with an exact CP-SAT solver |
| `verify_delta3_reduction.py` | the subcubic reduction graph of Johnson et al. (Algorithmica 2025, Thm 11) |

## Where each result comes from

| Article item | Command | Data |
|---|---|---|
| Threshold theorem, wheel proposition (Sec. III) | `python3 verify_theorem_A.py` | printed |
| Healing theorem: exhaustive check, n ≤ 12 (27 523 graphs) | `python3 exhaustive_heal.py 12` | `runs/exhaustive_12.log` |
| Healing theorem: intermediate lemmas, n ≤ 11 | `python3 checks/healing_lemmas_exhaustive.py 11` | printed |
| Healing theorem: tight sets, n ≤ 9 | `python3 checks/healing_tight_exhaustive.py 9` | printed |
| Healing theorem: exact optimisation, 251 graphs with 14–60 vertices | `python3 checks/healing_milp_stress.py SEED N1 N2` | printed |
| Healing theorem: exact optimisation, 1 386 graphs with 16–100 vertices | `python3 checks/healing_milp_large.py SEED SECONDS` | printed |
| Healing theorem: random test of the chain lemma | `python3 checks/healing_chain_random.py SEED NGRAPHS` | printed |
| Greedy augmentation, 972 runs (Appendix A) | `python3 greedy_heal.py SEED COUNT 12 20` | `runs/greedy_12_20.log` |
| Strong version is false (18-site graph) | `python3 strong_version_check.py` | `runs/strong_version_counterexample.json` |
| Constructive version: stuck sets first at 12 vertices | `python3 checks/constructive_stuck_search.py geng "-c -D3" 12` | printed |
| Constructive version: exchange chains | `python3 checks/constructive_deep_chain.py SEED NGRAPHS NMAX` | printed |
| One Ising ground state suffices (corollary) | `python3 checks/constructive_single_groundstate.py geng "-c -D3" 12 3` and `... lattices 5` | printed |
| Constructive procedure: timing on lattices | `python3 constructive_heal.py timing` | printed |
| Certification algorithm: Table I, Fig. 8 | `python3 timing_cert.py > runs/timing_cert.jsonl` | `runs/timing_cert.jsonl` |
| Δ = 4 hardness: satisfiable formulas | `python3 cnr_reduction.py SEED COUNT` | printed |
| Δ = 4 hardness: unsatisfiable 8-clause formula | `python3 cnr_unsat_test.py` | `runs/cnr_unsat.log` |
| Δ = 4 hardness: planarity of the construction (307 formulas) | `python3 cnr_planarity_check.py 300 1` | printed |
| Theorem 11 (Δ = 2k): planar instances, k = 3, 4 | `python3 cover_reduction.py planar` | `runs/cover_planar.log` |
| Theorem 11: random instances, k = 3, 4, 5 | `python3 cover_reduction.py random K 1 N` (N = 40, 24, 10) | `runs/cover_random_k*.log` |
| Theorem 11: unsatisfiable instances, k = 3 | `python3 cover_unsat_k3.py` | `runs/cover_unsat_k3.log` |
| Theorem 11: gap E0 − K against D3 (Fig. 4c) | `for k in 3 4 5; do python3 cover_reduction.py scan $k; done > runs/cover_scan.log` | `runs/cover_scan.log` |
| Theorem 11, k = 3 below D3 = 1 (private sites unrestricted) | `python3 cover_reduction.py small 1 12` | `runs/cover_small_k3.log` |
| Open problem (1): triangle trees of Ma and Zhang need h exchanges | `python3 checks/triangle_tree_chain.py 4` | printed |
| Penrose face-adjacency graph: exact energy curves (Fig. 6) | `python3 penrose_boundary.py RADIUS SEED > penrose_runs/rRADIUS_sSEED.json` | `penrose_runs/r*_s*.json` |
| Penrose 140-rhombus ground states (Fig. 6a–c) | `python3 make_penrose_states.py` | `penrose_runs/penrose_states.json` |
| Penrose quick scan | `python3 penrose_scan.py RADIUS [SEED]` | printed |
| Supplemental Note A: Table S1, random instances | `python3 supp_planarity.py 300 1` | `supp_runs/planarity_evidence.json` |
| Supplemental Note A: reduction equivalence (80 formulas) | `python3 verify_delta3_reduction.py` | printed |
| Supplemental Note A: instance φ0 | `python3 planarity_gap.py` | printed |
| Figures 1–3, 5–8 and the timing table | `cd paper && python3 make_figs.py` | `paper/figs/` |
| Figure 4 | `cd paper && python3 make_fig_gadget.py` | `paper/figs/fig_gadget.pdf` |
| Figure S1 | `cd paper && python3 make_supp_figs.py` | `paper/figs/fig_supp_minor.pdf` |

Running times: the exhaustive check at n = 12, the largest timing runs (about 8 000 sites) and the
Penrose curves of the larger patches take minutes to hours; everything else finishes in seconds to
minutes.

## Citation

If you use this code or data, please cite the article above.
