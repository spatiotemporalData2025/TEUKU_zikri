"""Citi Bike (GBFS) -> STG demo with Matplotlib windows."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from stg_core import (
    GBFS_STATION_INFORMATION,
    GBFS_STATION_STATUS,
    fetch_json,
    parse_station_information,
    filter_stations,
    build_knn_edges,
    collect_status_series,
    load_offline_sample,
    anomaly_score_simple,
)

def _wgs84_to_web_mercator(lat: np.ndarray, lon: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert WGS84 degrees to Web Mercator meters (EPSG:3857).
    Implemented here to avoid heavy GIS dependencies.
    """
    R = 6378137.0
    x = R * np.deg2rad(lon)
    # clamp latitude to avoid infinity near poles
    lat_clamped = np.clip(lat, -85.05112878, 85.05112878)
    y = R * np.log(np.tan(np.pi / 4.0 + np.deg2rad(lat_clamped) / 2.0))
    return x, y


def plot_map(stations, edges, values, title: str, basemap: bool = False):
    """
    Plot stations and kNN edges. If basemap=True and contextily is available,
    overlay OpenStreetMap tiles behind the plot.
    """
    lat = np.array([s.lat for s in stations], dtype=np.float32)
    lon = np.array([s.lon for s in stations], dtype=np.float32)

    if basemap:
        x, y = _wgs84_to_web_mercator(lat, lon)
    else:
        x, y = lon, lat

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel("X (meters, Web Mercator)" if basemap else "Longitude")
    ax.set_ylabel("Y (meters, Web Mercator)" if basemap else "Latitude")

    for u, v in edges:
        ax.plot([x[u], x[v]], [y[u], y[v]], linewidth=0.6, alpha=0.18)

    sc = ax.scatter(x, y, c=values, s=22, alpha=0.9)
    cb = plt.colorbar(sc, ax=ax)
    cb.set_label("Anomaly (z-score, clipped)")
    ax.grid(True, alpha=0.25)

    if basemap:
        try:
            import contextily as ctx
            # Use OSM tiles; requires internet for tile download.
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs="EPSG:3857", attribution_size=6)
        except Exception as e:
            # If contextily isn't installed or tiles fail, keep the plot as-is.
            ax.text(0.01, 0.01, f"Basemap unavailable ({type(e).__name__}).\nInstall: pip install contextily xyzservices",
                    transform=ax.transAxes, fontsize=8, va="bottom")

    return fig

def plot_heatmap(anom, stations, top_k=25):
    latest = anom[-1]
    idx = np.argsort(latest)[::-1][:top_k]
    data = anom[:, idx].T

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(f"Anomaly heatmap (top {top_k} stations by latest anomaly)")
    ax.set_xlabel("Time step")
    ax.set_ylabel("Station (top-K)")
    im = ax.imshow(data, aspect="auto", interpolation="nearest")
    cb = plt.colorbar(im, ax=ax)
    cb.set_label("Anomaly (z-score, clipped)")

    labels = [stations[i].name for i in idx]
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    return fig, idx

def plot_timeseries(bikes, anom, stations, edges, focus_idx: int):
    T, N = bikes.shape
    neigh = [[] for _ in range(N)]
    for u, v in edges:
        neigh[u].append(v)
        neigh[v].append(u)
    nm = np.zeros(T, dtype=np.float32)
    for t in range(T):
        ns = neigh[focus_idx]
        nm[t] = float(np.mean([bikes[t, j] for j in ns])) if ns else bikes[t, focus_idx]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(f"Station time series: {stations[focus_idx].name} (id={stations[focus_idx].station_id})")
    ax.set_xlabel("Time step")
    ax.set_ylabel("Bikes available")

    ax.plot(range(T), bikes[:, focus_idx], marker="o", linewidth=1.5, label="bikes (station)")
    ax.plot(range(T), nm, marker="x", linewidth=1.0, label="bikes (neighbor mean)")
    ax2 = ax.twinx()
    ax2.plot(range(T), anom[:, focus_idx], linestyle="--", linewidth=1.0, label="anomaly (z)", alpha=0.8)
    ax2.set_ylabel("Anomaly z-score")

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    ax.grid(True, alpha=0.25)
    return fig

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--interval", type=float, default=10.0)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--max-stations", type=int, default=250)
    ap.add_argument("--bbox", nargs=4, type=float, default=None, metavar=("MIN_LAT","MAX_LAT","MIN_LON","MAX_LON"))
    ap.add_argument("--offline-sample", action="store_true")
    ap.add_argument("--alpha", type=float, default=0.7)
    ap.add_argument("--basemap", action="store_true", help="overlay OpenStreetMap tiles (requires contextily + internet)")
    args = ap.parse_args()

    if args.offline_sample:
        stations, bikes, docks = load_offline_sample(Path(__file__).parent/"sample_data")
    else:
        info = fetch_json(GBFS_STATION_INFORMATION)
        stations = parse_station_information(info)
        bbox = tuple(args.bbox) if args.bbox else None
        stations = filter_stations(stations, bbox=bbox, max_stations=args.max_stations)
        bikes, docks = collect_status_series(stations, steps=args.steps, interval_s=args.interval, station_status_url=GBFS_STATION_STATUS)

    latlon = np.array([[s.lat, s.lon] for s in stations], dtype=np.float32)
    edges = build_knn_edges(latlon, k=args.k)
    anom = anomaly_score_simple(bikes, edges, alpha_self=args.alpha)

    plot_map(stations, edges, anom[-1], title="Citi Bike STG: latest anomaly over stations (kNN graph)", basemap=args.basemap)
    _, top_idx = plot_heatmap(anom, stations, top_k=min(25, len(stations)))
    focus = int(top_idx[0]) if len(top_idx) else 0
    plot_timeseries(bikes, anom, stations, edges, focus_idx=focus)
    plt.show()

if __name__ == "__main__":
    main()
