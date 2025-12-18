# Spatio-Temporal Graph (STG)

A **Spatio-Temporal Graph (STG)** is a graph representation for data that has both:
- **Spatial information** (location/geometry/topology): e.g., (x, y), GPS, 3D coordinates, road connectivity.
- **Temporal information** (time): e.g., discrete time steps t = 0, 1, 2, ... or continuous timestamps.

In short: an STG models **relationships in space** and **changes over time** in a single graph structure.

---

## 1) Core Components

### 1.1 Nodes
There are two common STG design choices:

**A) Node = entity (dynamic graph over time)**
- Nodes are entities: sensors, robots, intersections, people.
- The graph changes with time (a graph snapshot per time step).

**B) Node = (entity, time) pair (space-time expanded graph)**
- Each node is a pair: (entity i, time t)
- The graph is built once (static), but it explicitly contains time in its structure.

This README uses approach **(B)** because it is simple, explicit, and easy to construct.

---

## 2) Edges in an STG

An STG typically has at least two edge types:

### 2.1 Spatial edges
Edges connecting nodes at the **same time step** based on spatial relationships, for example:
- nearest neighbors (kNN graph),
- within a radius (radius graph),
- physical adjacency (road network),
- interaction/communication links.

Example:
- (robot1, t=10) connected to (robot2, t=10) because they are close.

### 2.2 Temporal edges
Edges connecting the **same entity across time**:
- (entity i, time t) → (entity i, time t+1)

You can also make them bidirectional if your model needs backward flow of information.

---

## 3) Node and Edge Features

### 3.1 Node features (X)
Each node can store a feature vector such as:
- position: [x, y] or [x, y, z]
- velocity: [vx, vy]
- sensor measurements: temperature, pressure, etc.
- learned embeddings

### 3.2 Edge features / weights (optional)
Each edge may have:
- distance between nodes (for spatial edges),
- time delta (for temporal edges),
- connection strength / confidence.

---

## 4) Common Output Format for GNNs

It is common to store:
- `node_features`: shape [num_nodes, feat_dim]
- `edge_index`: shape [2, num_edges] containing (src, dst)
- `edge_type`: shape [num_edges] (0 = spatial, 1 = temporal)
- `edge_weight`: shape [num_edges] (optional)

---

## 5) How to Build an STG from Trajectory Data

Assume you have:
- `positions[t, i] = [x, y]`
  - `t` = time index
  - `i` = entity index

Steps:
1. Create nodes for all (i, t)
2. Add temporal edges (i,t) -> (i,t+1)
3. Add spatial edges at each time t using kNN or radius rule
4. Optionally compute edge weights (inverse distance, Gaussian, etc.)

---

## 6) Quickstart

Run:
```bash
python stg_example.py
