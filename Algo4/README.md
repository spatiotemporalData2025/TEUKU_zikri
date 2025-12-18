# Spatio-Temporal Graphs (STG): A Unified Representation for Coupled Space–Time Dynamics


slides:
https://spatiotemporaldata2025.github.io/TEUKU_zikri/Algo4/

---

## Abstract
Many real-world dynamical systems exhibit **temporal evolution** together with **structured inter-dependencies** among entities. Classical time-series modeling treats each signal independently or assumes Euclidean locality, which can be inadequate for domains where interactions are constrained by **networks** (roads, power grids, skeleton joints) or **time-varying proximity** (multi-agent systems). A **Spatio-Temporal Graph (STG)** provides a principled representation that jointly encodes **(i) spatial interactions** (who influences whom) and **(ii) temporal continuity** (how each entity evolves over time). This README formalizes STGs, discusses when and why they should be used, and provides two executable reference implementations that construct STGs and generate visualizations for (a) moving agents with k-nearest-neighbor (kNN) dynamic connectivity and (b) fixed sensor networks with known topology and time-series signals.

---

## Keywords
Spatio-temporal modeling, graph neural networks, dynamic graphs, time-series forecasting, multi-agent systems, traffic prediction, sensor networks

---

## 1. Introduction
Spatio-temporal prediction and analysis appear in traffic forecasting, robotics, IoT monitoring, and activity recognition. In these domains, future observations at one node are not only a function of its own past, but also depend on other nodes connected through:
- **physical networks** (roads/cables/pipes),
- **kinematic structures** (human skeleton joints),
- **interaction graphs** that evolve with motion (swarm robotics).

Spatio-Temporal Graphs (STGs) address this by representing the system as a graph whose structure and features evolve across time. STG-based learning has motivated a large body of architectures for forecasting and recognition, including STGCN for traffic forecasting :contentReference[oaicite:0]{index=0}, DCRNN :contentReference[oaicite:1]{index=1}, Graph WaveNet :contentReference[oaicite:2]{index=2}, and ST-GCN for skeleton action recognition :contentReference[oaicite:3]{index=3}.

---

## 2. Related Work (high-level)
STG is a **representation**, not a single model. Prominent spatio-temporal graph neural models include:

- **STGCN**: convolutional spatial-temporal blocks for traffic networks :contentReference[oaicite:4]{index=4}  
- **DCRNN**: diffusion graph convolution + recurrent temporal modeling :contentReference[oaicite:5]{index=5}  
- **Graph WaveNet**: learns adaptive (hidden) spatial dependencies + dilated temporal convolutions :contentReference[oaicite:6]{index=6}  
- **ST-GCN**: graph conv on skeleton joints over time for action recognition :contentReference[oaicite:7]{index=7}  
- **Temporal Graph Networks (TGN)**: event-based dynamic graphs with memory modules :contentReference[oaicite:8]{index=8}  

This repository focuses on **constructing** STGs (space–time expansion) and **visualizing** them, which is the common foundation behind many of these models.

---

## 3. Problem Formulation
Let there be **N entities** (nodes) observed over **T discrete time steps**.
- Entity index: \( i \in \{0,\dots,N-1\} \)
- Time index: \( t \in \{0,\dots,T-1\} \)

Each entity has features \( \mathbf{x}_{i,t} \in \mathbb{R}^F \), e.g., sensor speed, robot pose, or joint coordinates.

**Goal (typical):** learn or analyze dependencies to perform forecasting, classification, anomaly detection, or control.  
Examples:
- Forecast \( \mathbf{x}_{:,t+1:t+H} \) given \( \mathbf{x}_{:,0:t} \)
- Detect anomalies that propagate through the network
- Recognize actions from skeleton trajectories

---

## 4. Definition of a Spatio-Temporal Graph (STG)

### 4.1 Space–time expanded graph
A common and practical STG construction is the **space–time expanded graph**:

- **STG node:** a pair \((i,t)\) meaning “entity \(i\) at time \(t\)”
- **STG vertex set:**
  \[
  \mathcal{V}^{ST} = \{(i,t)\ |\ i=0..N-1,\ t=0..T-1\}
  \]
  so \(|\mathcal{V}^{ST}| = N \cdot T\)

- **Two edge types:**
  1. **Spatial edges** (interaction at the same time):
     \[
     (i,t) \rightarrow (j,t)\ \ \text{if}\ \ j \in \mathcal{N}_t(i)
     \]
     where \(\mathcal{N}_t(i)\) is the neighbor set (possibly time-varying).
  2. **Temporal edges** (continuity of the same entity):
     \[
     (i,t) \rightarrow (i,t+1)
     \]

This yields a single graph where learning can be expressed as message passing across **space** and **time**.

### 4.2 Two dominant “spatial neighbor” regimes
1. **Fixed topology (static graph):**
   - Roads, power grid, factory wiring, pipelines
   - \(\mathcal{N}_t(i) = \mathcal{N}(i)\) (constant)
2. **Dynamic topology (time-varying graph):**
   - Multi-agent / swarm systems
   - kNN neighbors based on distance at time \(t\): \(\mathcal{N}_t(i) = \text{kNN}(\mathbf{p}_{:,t}, i)\)

Graph WaveNet emphasizes that the observed adjacency may be incomplete and proposes learning adaptive dependencies :contentReference[oaicite:9]{index=9}—a key motivation for considering both fixed and learned/dynamic graphs.

---

## 5. Why Use STG?

### 5.1 STG provides the correct inductive bias
If the process is **coupled**, i.e.:
- disturbances propagate through connections (congestion waves, cascading failures),
- nodes influence each other with delays,
then independent time-series models ignore structure and may underperform.

STG explicitly encodes that:
- “who affects whom” is constrained by topology or proximity,
- temporal evolution is not independent of interactions.

Traffic forecasting is a canonical example: road sensors exhibit strong spatial dependence and non-linear temporal dynamics, motivating models such as STGCN :contentReference[oaicite:10]{index=10} and DCRNN :contentReference[oaicite:11]{index=11}.

### 5.2 STG unifies heterogeneous domains
- **Traffic networks:** sensors as nodes, roads as edges :contentReference[oaicite:12]{index=12}  
- **Skeleton sequences:** joints as nodes, bones as edges :contentReference[oaicite:13]{index=13}  
- **Event-driven interactions:** nodes and edges change over time (TGN) :contentReference[oaicite:14]{index=14}  

A single formalism supports forecasting, classification, and anomaly tasks.

### 5.3 STG improves interpretability and debugging
Even before training deep models, STG construction lets you:
- inspect connectivity assumptions (fixed vs kNN),
- visualize propagation pathways,
- detect missing edges or overly dense graphs.

---

## 6. Method: STG Construction Used in This Repository

### 6.1 Node indexing
We map \((i,t)\) to a global integer ID:
\[
\text{id}(i,t) = t \cdot N + i
\]

### 6.2 Temporal edges
For all \(i\) and \(t=0..T-2\):
\[
\text{id}(i,t) \rightarrow \text{id}(i,t+1)
\]

### 6.3 Spatial edges
Two implementations are provided:
- **kNN spatial edges** per time step (dynamic graph)
- **Grid adjacency** expanded per time step (static graph)

### 6.4 Edge typing
Edges are labeled:
- 0 = spatial  
- 1 = temporal  
This is useful for heterogeneous message passing or diagnostics.

---

## 7. Experiments and Reproducible Visualizations

> These experiments are **synthetic** and intended to validate the representation and construction pipeline, not to claim state-of-the-art predictive performance.

### 7.1 Example 1 — Trajectory STG (dynamic kNN connectivity)
**Scenario:** multiple agents move in 2D; spatial edges connect k nearest neighbors at each time step.  
**Motivation:** models multi-agent interaction where neighborhood changes continuously.

**Script:** `stg_example_1_trajectories.py`  
**Outputs:**
- `traj_stg_timestep.png` (snapshot graph at a time index)
- `traj_stg_3d.png` (3D x–y–time trajectories)

### 7.2 Example 2 — Sensor/Traffic STG (static topology)
**Scenario:** sensors arranged in a grid; spatial edges are fixed adjacency; node values evolve as a moving wave (toy congestion).  
**Motivation:** fixed networks like traffic sensors or factory IoT arrays.

**Script:** `stg_example_2_sensors.py`  
**Outputs:**
- `sensor_graph.png` (node values + topology snapshot at time \(t\))
- `sensor_heatmap.png` (node values across time)

---

## 8. Complexity Analysis (construction)
Let:
- \(N\) nodes, \(T\) time steps
- \(E_s\) spatial edges per time (static case), or approx. \(N \cdot k\) (kNN case)

Then:
- **Temporal edges:** \(E_t = N(T-1)\)
- **Spatial edges expanded:** \(E_s^{ST} \approx T \cdot E_s\)

So total edges scale as:
\[
E^{ST} \approx T \cdot E_s + N(T-1)
\]

**Implication:** space–time expansion can become large for high-frequency sampling. This is why some methods prefer:
- temporal windowing,
- sparse sampling,
- event-based temporal graphs (e.g., TGN) :contentReference[oaicite:15]{index=15}.

---

## 9. Limitations and Practical Considerations
1. **Graph size explosion:** \(N \times T\) nodes can be large; consider windows or event-based modeling.
2. **Connectivity choice matters:** kNN may introduce spurious edges; static adjacency may miss hidden dependencies.
3. **Directionality and delays:** real systems may require directed edges and time-lagged spatial links.
4. **Irregular time:** discrete-time STG assumes fixed sampling; irregular data may be better modeled as event streams (TGN-style) :contentReference[oaicite:16]{index=16}.

---

## 10. Installation and Usage
### 10.1 Requirements
- Python 3.9+
- numpy
- matplotlib

Install:
```bash
pip install numpy matplotlib
