---
theme: seriph
background: https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072
title: Urban Activity Pulse Map
class: text-center
---

# Urban Activity Pulse Map

Web GIS Spatio-Temporal Visualization

Final Project - Algorithms and Programming

---

# Project Overview

A real-time Web GIS application for visualizing urban activity patterns

**Technologies:**
- Node.js + Express + Leaflet
- OpenStreetMap + Overpass API  
- 100% FREE - no billing

**Main Features:**
- Interactive map visualization
- Temporal analysis (0-23 hours)
- Spatial density grid (heatmap)
- Top-5 hotspots detection
- Real-time POI data integration

---

# System Architecture

```mermaid
graph LR
    A[Browser Client] -->|HTTP/JSON| B[Express Server]
    B -->|Overpass Query| C[OpenStreetMap API]
    C -->|POI Data| B
    B -->|JSON Response| A
    
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#f3e5f5
```

**Components:**
- **Browser**: Leaflet Map + Time Slider + Top-5 List
- **Backend**: Express API + Cache (TTL 1h)
- **External**: OpenStreetMap + Overpass API

---

# Research Method

**Problem Statement:**  
How to visualize urban activity patterns in spatio-temporal context using free, open-source data?

**Approach:**

1. Data Collection: OpenStreetMap via Overpass API
2. Spatial Analysis: Grid-based binning for density
3. Temporal Analysis: Time-based filtering (0-23h)
4. Visualization: Interactive heatmap
5. Performance: Caching strategy

---

# Data Collection

**Overpass API Integration**

Query example:

```sql
[out:json][timeout:25];
(
  node["amenity"="cafe"](around:3000,35.681,139.767);
  node["amenity"="restaurant"](around:3000,35.681,139.767);
);
out body;
```

Parameters:
- Radius-based search (meters)
- Tag-based filtering
- Timeout control (25 seconds)

---

# Spatial Analysis

**Grid-Based Binning Algorithm**

Concept: Divide map into uniform grid cells and count points per cell

Steps:
1. Define grid cell size (0.01° ≈ 1km)
2. Calculate grid indices for each point
3. Count points in each cell
4. Identify cells with highest activity

Advantages:
- Fast computation O(n)
- Scalable for large datasets
- Easy to visualize

---

# Algorithm: Activity Density

**Complexity: O(n + k log k)**

```js
function computeActivityGrid(points, bounds, cellSize, hour) {
  // Step 1: Filter by hour → O(n)
  let filtered = points.filter(p => p.hour === hour);
  
  // Step 2: Binning → O(n)
  let counts = {};
  for (let p of filtered) {
    let i = Math.floor((p.lat - bounds.latMin) / cellSize);
    let j = Math.floor((p.lon - bounds.lonMin) / cellSize);
    let key = i + ',' + j;
    counts[key] = (counts[key] || 0) + 1;
  }
  
  // Step 3: Sort for Top-5 → O(k log k)
  let cells = Object.entries(counts).sort((a,b) => b[1] - a[1]);
  return cells.slice(0, 5);
}
```

---

# Temporal Analysis

**Time-Based Pattern Detection**

Approach:
- Assign activity hour to each POI
- Filter data by selected hour (0-23)
- Detect peak/off-peak patterns
- Dynamic visualization update

Activity Distribution:
- Morning peak: 8-10 (15%)
- Evening peak: 17-20 (15%)
- Midday: 11-16 (20%)
- Other hours: distributed (50%)

---

# Visualization

**Color Normalization Strategy**

```js
opacity = 0.10 + 0.70 * (count / maxCount);

if (count/maxCount > 0.7)      color = "red";     // Very high
else if (count/maxCount > 0.4) color = "orange";  // High
else if (count/maxCount > 0.2) color = "yellow";  // Medium
else                            color = "blue";    // Low
```

Characteristics:
- Relative to viewport (not absolute)
- Adapts dynamically to zoom level
- Highlights hotspot areas

---

# Performance Optimization

**Caching Strategy**

Problem:
- Overpass API has rate limits
- Network latency affects UX

Solution:
- In-memory cache (Map structure)
- Time-To-Live (TTL) = 1 hour
- Cache key = location + radius + categories

Results:
- Reduced API calls by ~80%
- Instant response for repeated queries

---

# Spatio-Temporal Integration

**Spatial Dimension:**
- Grid cells with lat/lon bounds
- Distance-based queries (radius)
- Viewport filtering
- Hotspot detection (Top-5)

**Temporal Dimension:**
- Hour slider (0-23)
- Dynamic filtering by hour
- Pattern recognition (peak/off-peak)
- Real-time updates

**Integration** = Grid density changes dynamically based on selected time

---

# System Capabilities

**Tested Locations:**

| City | Coordinates | POI Count |
|------|-------------|-----------|
| Tokyo Station | 35.681, 139.767 | 1000+ |
| NYC Times Square | 40.758, -73.985 | 800+ |
| London Piccadilly | 51.510, -0.134 | 600+ |

**Key Metrics:**
- Response time: < 2 seconds for 3km radius
- Cache hit rate: ~80% for repeated queries
- Scalability: Handles 3000+ points smoothly

---

# Demo Workflow

**Demo Data Mode:**
1. Load 3000 synthetic points
2. Slide time (0-23 hours)
3. Observe density changes
4. Zoom/pan map
5. Click Top-5 hotspots

**Real POI Mode:**
1. Set location (click/input)
2. Select categories
3. Set radius (default 3km)
4. Fetch from Overpass
5. Apply time filter
6. Analyze patterns

---

# Advantages

**1. Free & Accessible**
- No API keys or billing
- Open-source data (OpenStreetMap)
- Runs on localhost

**2. Performance**
- O(n + k log k) algorithm efficiency
- Caching reduces API load
- Viewport-only rendering

**3. Flexibility**
- Dual data sources (demo/real)
- Multiple POI categories
- Adjustable parameters

---

# Limitations & Future Work

**Current Limitations:**
- Synthetic time distribution (not real opening hours)
- In-memory cache (lost on restart)
- Single user (no multi-tenancy)

**Proposed Improvements:**
- Parse actual opening_hours from OSM tags
- Persistent cache (Redis/Database)
- Historical data tracking
- Mobile-responsive UI
- Export to GeoJSON/CSV

---

# Key Contributions

**Methodological:**
- Grid-based binning for spatial analysis
- Time-based filtering for temporal patterns
- Color normalization for visualization
- Caching strategy for performance

**Practical:**
- Free solution using OpenStreetMap
- Real-time integration with Overpass API
- Interactive visualization with Leaflet
- Educational framework for GIS learning

---
layout: center
class: text-center
---

# Thank You

## Questions?

**Urban Activity Pulse Map**  
Web GIS Spatio-Temporal Visualization

Algorithms and Programming - Final Project  
January 2026

---
layout: end
---

# End of Presentation
