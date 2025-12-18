# Spatio-Temporal Graphs (STG): A Unified Representation for Coupled Space–Time Dynamics

**Slides:** https://spatiotemporaldata2025.github.io/TEUKU_zikri/Algo4/

Many real-world dynamical systems evolve over time while also exhibiting structured dependencies among entities.
In such settings, the future state of one entity is shaped not only by its own history, but also by information
arriving through an interaction structure: physical networks (roads, power grids, pipelines), kinematic linkages
(skeleton joints), or time-varying proximity (multi-agent systems). A **Spatio-Temporal Graph (STG)** is a
representation designed to encode this coupling by combining **spatial interactions** with **temporal continuity**
in a single graph object.

A common STG construction is the **space–time expansion**. Given **N** entities observed over **T** discrete time
steps, each STG node corresponds to a pair `(i, t)`, meaning “entity i at time t”. Two edge types are defined:
- **Spatial edges** at the same time: `(i, t) -> (j, t)` if `j` is a neighbor of `i` at time `t`.
- **Temporal edges** across time: `(i, t) -> (i, t+1)`.

This representation is typically used when the underlying process is **coupled** (propagation along topology,
non-Euclidean structure, or time-varying neighborhoods). In such cases, per-node time-series modeling can ignore
structural constraints and under-represent how signals influence other parts of the system.

---

## STG Definition (Space–Time Expanded Form)

**Vertex set**
- Nodes are indexed by entity `i in {0..N-1}` and time `t in {0..T-1}`.
- STG vertices: `V_ST = {(i, t)}` with `|V_ST| = N * T`.

**Edge set**
- Spatial edges: `(i, t) -> (j, t)` if `j in N_t(i)`.
- Temporal edges: `(i, t) -> (i, t+1)`.

> Notes on neighborhood `N_t(i)`:
> - **Static topology:** `N_t(i) = N(i)` (roads, power grids, fixed sensor networks)
> - **Dynamic topology:** `N_t(i)` changes over time (kNN from positions in multi-agent systems)

---

## Construction Used in This Repository

### Node indexing
A space–time node `(i, t)` is mapped to an integer ID:

- Plain form: `id(i,t) = t*N + i`

### Temporal edges
For all `i` and `t = 0..T-2`:

- Plain form: `id(i,t) -> id(i,t+1)`

### Spatial edges
Two implementations are provided:
- **Dynamic kNN edges** per time step (moving agents)
- **Static adjacency expansion** (grid sensor network)

### Edge typing (for diagnostics)
Edges are labeled:
- `0` = spatial
- `1` = temporal

---

## Programs

### Program 1 — STG implementation & visualization (`stg_theory.py`)
Implements:
- STG data structure (space–time expansion)
- builders for dynamic kNN and static adjacency
- visualization utilities

Outputs (PNG) to `out/`:
- `traj_spatial_snapshot.png`
- `traj_3d.png`
- `grid_graph_snapshot.png`
- `grid_heatmap.png`

Run:
```bash
python stg_theory.py
