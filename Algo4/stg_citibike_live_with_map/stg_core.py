"""Core utilities for building a simple STG from Citi Bike GBFS feeds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import time
import math
import json
import pathlib

import numpy as np
import requests

GBFS_STATION_INFORMATION = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
GBFS_STATION_STATUS = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"

@dataclass
class Station:
    station_id: str
    name: str
    lat: float
    lon: float
    capacity: int

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = p2 - p1
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlon/2)**2
    return 2*r*math.asin(math.sqrt(a))

def build_knn_edges(latlon: np.ndarray, k: int) -> List[Tuple[int, int]]:
    n = latlon.shape[0]
    d = np.zeros((n, n), dtype=np.float32)
    for i in range(n):
        for j in range(i+1, n):
            dist = haversine_km(float(latlon[i,0]), float(latlon[i,1]),
                                float(latlon[j,0]), float(latlon[j,1]))
            d[i, j] = dist
            d[j, i] = dist
    edges = set()
    for i in range(n):
        nn = np.argsort(d[i])[1:k+1]
        for j in nn:
            u, v = (i, int(j)) if i < int(j) else (int(j), i)
            edges.add((u, v))
    return sorted(edges)

def fetch_json(url: str, timeout_s: int = 20) -> dict:
    headers = {"User-Agent": "stg-citibike-demo/1.0 (educational)"}
    r = requests.get(url, headers=headers, timeout=timeout_s)
    r.raise_for_status()
    return r.json()

def parse_station_information(payload: dict) -> List[Station]:
    out: List[Station] = []
    for s in payload["data"]["stations"]:
        out.append(Station(
            station_id=str(s["station_id"]),
            name=str(s.get("name", "")),
            lat=float(s["lat"]),
            lon=float(s["lon"]),
            capacity=int(s.get("capacity", 0) or 0),
        ))
    return out

def parse_station_status(payload: dict) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for s in payload["data"]["stations"]:
        sid = str(s["station_id"])
        out[sid] = {
            "bikes": float(s.get("num_bikes_available", np.nan)),
            "docks": float(s.get("num_docks_available", np.nan)),
        }
    return out

def filter_stations(
    stations: List[Station],
    bbox: Optional[Tuple[float, float, float, float]] = None,
    max_stations: int = 300,
) -> List[Station]:
    if bbox is not None:
        min_lat, max_lat, min_lon, max_lon = bbox
        stations = [s for s in stations if (min_lat <= s.lat <= max_lat) and (min_lon <= s.lon <= max_lon)]
    stations = sorted(stations, key=lambda s: s.capacity, reverse=True)
    return stations[:max_stations]

def collect_status_series(
    stations: List[Station],
    steps: int,
    interval_s: float,
    station_status_url: str = GBFS_STATION_STATUS,
) -> Tuple[np.ndarray, np.ndarray]:
    id_list = [s.station_id for s in stations]
    n = len(id_list)
    bikes = np.full((steps, n), np.nan, dtype=np.float32)
    docks = np.full((steps, n), np.nan, dtype=np.float32)
    for t in range(steps):
        payload = fetch_json(station_status_url)
        m = parse_station_status(payload)
        for i, sid in enumerate(id_list):
            rec = m.get(sid)
            if rec is None:
                continue
            bikes[t, i] = rec["bikes"]
            docks[t, i] = rec["docks"]
        if t != steps - 1:
            time.sleep(interval_s)
    return bikes, docks

def load_offline_sample(sample_dir: pathlib.Path) -> Tuple[List[Station], np.ndarray, np.ndarray]:
    info = json.loads((sample_dir/"sample_station_information.json").read_text(encoding="utf-8"))
    stations = parse_station_information(info)
    status_files = sorted(sample_dir.glob("sample_station_status_*.json"))
    steps = len(status_files)
    id_list = [s.station_id for s in stations]
    n = len(id_list)
    bikes = np.full((steps, n), np.nan, dtype=np.float32)
    docks = np.full((steps, n), np.nan, dtype=np.float32)
    for t, fp in enumerate(status_files):
        payload = json.loads(fp.read_text(encoding="utf-8"))
        m = parse_station_status(payload)
        for i, sid in enumerate(id_list):
            rec = m.get(sid)
            if rec is None:
                continue
            bikes[t, i] = rec["bikes"]
            docks[t, i] = rec["docks"]
    return stations, bikes, docks

def anomaly_score_simple(
    bikes: np.ndarray,
    edges: List[Tuple[int, int]],
    alpha_self: float = 0.7,
    eps: float = 1e-6,
) -> np.ndarray:
    T, N = bikes.shape
    neigh = [[] for _ in range(N)]
    for u, v in edges:
        neigh[u].append(v)
        neigh[v].append(u)

    anomaly = np.zeros((T, N), dtype=np.float32)
    for t in range(1, T):
        prev = bikes[t-1]
        nm = np.zeros(N, dtype=np.float32)
        for i in range(N):
            if len(neigh[i]) == 0:
                nm[i] = prev[i]
            else:
                vals = [prev[j] for j in neigh[i] if not np.isnan(prev[j])]
                nm[i] = float(np.mean(vals)) if len(vals) else prev[i]
        pred = alpha_self * prev + (1.0 - alpha_self) * nm
        anomaly[t] = np.abs(bikes[t] - pred)
        anomaly[t] = np.nan_to_num(anomaly[t], nan=0.0, posinf=0.0, neginf=0.0)

    for t in range(T):
        mu = float(np.mean(anomaly[t]))
        sig = float(np.std(anomaly[t])) + eps
        anomaly[t] = (anomaly[t] - mu) / sig
        anomaly[t] = np.clip(anomaly[t], -3.0, 6.0)

    return anomaly
