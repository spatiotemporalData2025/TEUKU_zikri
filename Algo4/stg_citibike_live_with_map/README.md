# STG Demo on Citi Bike (GBFS): Station-Availability Dynamics as a Spatio-Temporal Graph

This mini-project demonstrates how **Citi Bike's public GBFS feeds** can be represented as a **Spatio-Temporal Graph (STG)** and visualized with **Matplotlib (interactive windows)**.

## What this project does
- Downloads **station metadata** (location, capacity) from `station_information.json`
- Polls **live station status** (bikes/docks available) from `station_status.json` for several time steps
- Builds an **STG**:
  - **Spatial edges**: k-nearest-neighbor (kNN) connections between stations (based on lat/lon)
  - **Temporal edges**: each station connected to itself across time steps
- Computes a simple, interpretable **anomaly score**:
  - Predict next bikes-available from a mixture of **self** and **neighbor mean**
  - Anomaly = absolute residual (standardized per time step)
- Opens **Matplotlib windows** (no PNG export):
  - Map view (stations colored by anomaly at the latest time)
  - Heatmap (anomaly over time for the top-K most anomalous stations)
  - Time-series view (bikes available for the most anomalous station)

> Note: This is a representation + diagnostics demo, not a production forecasting model.

---

## Requirements
- Python 3.9+
- `numpy`, `matplotlib`, `requests`

Install:
```bash
pip install -r requirements.txt
```

---

## Run
```bash
python stg_citibike_live.py
```

Useful options:
```bash
python stg_citibike_live.py --steps 12 --interval 10 --k 5 --max-stations 250
python stg_citibike_live.py --bbox 40.70 40.83 -74.02 -73.93   # Manhattan-ish
python stg_citibike_live.py --offline-sample                   # no internet required
```

---

## STG definition used here (time-expanded view)
Each STG node is a pair `(station_id, t)`.

Edges:
- Spatial: `(i, t) <-> (j, t)` if `j` is in kNN of `i` (static spatial graph built once from coordinates)
- Temporal: `(i, t) -> (i, t+1)`

Node feature (per time):
- `bikes = num_bikes_available`
- `docks = num_docks_available`
- `util = bikes / max(capacity, 1)`

---

## Files
- `stg_citibike_live.py` : main script (fetch → STG → anomaly → plots)
- `stg_core.py` : helper functions (GBFS fetch, kNN, anomaly)
- `sample_data/` : small offline sample so the plots can run without network


---
## Optional: show a real map background (tiles)

By default, the “map” plot is a **longitude/latitude scatter** (no basemap tiles).

To add an OpenStreetMap tile background in the Matplotlib window, install:

```bash
pip install contextily xyzservices
```

Then run:
```bash
python stg_citibike_live.py --basemap
```

Notes:
- `--basemap` needs internet access to download map tiles.
- If `contextily` is not installed, the script falls back to the plain scatter plot.
