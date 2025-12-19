---
theme: default
title: Spatio-Temporal Graph (STG) on Citi Bike (GBFS)
info: Time-expanded STG + simple anomaly scoring
highlighter: shiki
---

# Spatio-Temporal Graph (STG) on Citi Bike (GBFS)

**Objective:** represent station availability as a *space–time* graph and visualize dynamics & anomalies.

- **Spatial:** stations influence nearby stations (kNN graph from GPS)
- **Temporal:** each station evolves over time (poll index)

---

## Data source and temporal sampling

**Open data (GBFS):**
- `station_information.json` → station coordinates + capacity
- `station_status.json` → bikes/docks availability (snapshot)

**Temporal axis in this demo**
- time step `t` = **poll index** (0, 1, 2, …)
- a short sequence is created by polling the status feed repeatedly

---

## STG representation (time-expanded graph)

Define an STG node as a pair:

$$
v = (i, t)
$$

- $i$ : station index  
- $t$ : time step (poll index)

Edges:
- Spatial (same time):
  $$
  (i,t)\leftrightarrow (j,t)\quad \text{if } j\in \mathrm{kNN}(i)
  $$
- Temporal:
  $$
  (i,t)\rightarrow (i,t+1)
  $$

---

## STG mapping used in implementation

A common indexing for time-expanded graphs:

$$
\mathrm{id}(i,t)=t\cdot N + i
$$

- $N$: number of stations  
- enables storing features as matrices like `bikes[t, i]`

---

## Anomaly scoring used in this demo

One-step predictor (self + neighbor mean):

$$
\hat{b}_i(t+1)=\alpha\, b_i(t) + (1-\alpha)\,\overline{b}_{\mathcal{N}(i)}(t)
$$

Residual:

$$
a_i(t+1)=\left|\, b_i(t+1)-\hat{b}_i(t+1)\,\right|
$$

Standardized per time step:

$$
z_i(t)=\frac{a_i(t)-\mu_t}{\sigma_t+\varepsilon}
$$

---
---

## Result: station map (latest anomaly)

<div style="display: flex; justify-content: center;">
  <img src="/figures/map_latest_anomaly.png" alt="Web application map" style="width: 74%; height: auto;" />
</div>

---

## Result: anomaly heatmap over time

<img src="/figures/anomaly_heatmap.png" alt="Web application map" style="width: 100%; height: auto;" />

---

## Result: time series (most anomalous station)

<img src="/figures/station_timeseries.png" alt="Web application map" style="width: 100%; height: auto;" />

---

## How to reproduce the figures

The bundled Python code can run with an offline sample:

```bash
cd code
pip install -r requirements.txt
python stg_citibike_live.py --offline-sample
```

To poll live data (internet required):

```bash
python stg_citibike_live.py --steps 12 --interval 10
```

---

## Notes

- The anomaly score here is **diagnostic** (simple residual), useful for visualization and sanity-checking STG assumptions.
- For stronger performance, the same STG representation can feed more advanced predictors (e.g., windowed models, learned adjacency, GNNs).
