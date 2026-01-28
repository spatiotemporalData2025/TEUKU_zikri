# Architecture Diagram - Urban Activity Pulse Map

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT SIDE (Browser)                       │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    index.html (UI Layer)                      │ │
│  │                                                               │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │ │
│  │  │  Data Source │  │  Time Slider │  │  Cell Size   │      │ │
│  │  │  Toggle      │  │   (0-23)     │  │  Slider      │      │ │
│  │  │ [Demo|Real]  │  │              │  │              │      │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │ │
│  │                                                               │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │  Overpass Controls (show/hide)                       │   │ │
│  │  │  - Lat/Lon input                                     │   │ │
│  │  │  - Radius input                                      │   │ │
│  │  │  - Category checkboxes (convenience,cafe,etc)        │   │ │
│  │  │  - Fetch POI button                                  │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │                                                               │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │  Top-5 Hotspot List (clickable)                      │   │ │
│  │  │  1. count=123 @ (35.681, 139.767)                    │   │ │
│  │  │  2. count=98  @ (35.685, 139.770)                    │   │ │
│  │  │  ...                                                  │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                     main.js (Logic Layer)                     │ │
│  │                                                               │ │
│  │  • Leaflet Map Initialization                                │ │
│  │  • Fetch Demo Data (/api/points?hour=X)                     │ │
│  │  • Fetch Real POI (/api/poi?lat=...&lon=...)                │ │
│  │  • Grid Algorithm (binning lat/lon → count per cell)         │ │
│  │  • Render Grid Rectangles (L.rectangle)                      │ │
│  │  • Compute Top-5 Hotspots (sort by count)                    │ │
│  │  • Event Handlers (slider, click, zoom, pan)                 │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                   Leaflet + OpenStreetMap                     │ │
│  │                                                               │ │
│  │  ┌─────────────────────────────────────────────────┐         │ │
│  │  │   Map View (Interactive)                        │         │ │
│  │  │   • Zoom/Pan controls                           │         │ │
│  │  │   • OSM Tiles (basemap)                         │         │ │
│  │  │   • Grid Layer (rectangles with color/opacity)  │         │ │
│  │  │   • Click event → set location                  │         │ │
│  │  └─────────────────────────────────────────────────┘         │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP/JSON (fetch)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE (Node.js + Express)                  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                      server.js (API Layer)                    │ │
│  │                                                               │ │
│  │  Endpoints:                                                   │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │  GET /api/health                                     │   │ │
│  │  │  → {ok: true, port: 8000}                            │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │                                                               │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │  GET /api/points?hour=X                              │   │ │
│  │  │  → {center: {lat,lon}, points: [...]}                │   │ │
│  │  │  (Demo data: 3000 points, deterministik)             │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │                                                               │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │  GET /api/poi?lat=...&lon=...&radius=...&categories= │   │ │
│  │  │  → {center, radius, categories, count, poi: [...]}   │   │ │
│  │  │  (Fetch dari Overpass API + caching)                 │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  │                                                               │ │
│  │  ┌──────────────────────────────────────────────────────┐   │ │
│  │  │  POST /api/grid (optional, bisa di frontend)         │   │ │
│  │  │  → {totalPoints, totalCells, maxCount, top5, cells}  │   │ │
│  │  └──────────────────────────────────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                  In-Memory Cache (Map)                        │ │
│  │                                                               │ │
│  │  Key: "${lat},${lon},${radius},${categories}"                │ │
│  │  Value: {data: {...}, timestamp: Date.now()}                 │ │
│  │  TTL: 3600000ms (1 hour)                                     │ │
│  │                                                               │ │
│  │  Cache Hit → return cached data                              │ │
│  │  Cache Miss → fetch Overpass → cache → return                │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ Overpass QL (HTTP POST)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Overpass API (OpenStreetMap Data)                     │
│                                                                     │
│  Endpoint: https://overpass-api.de/api/interpreter                 │
│                                                                     │
│  Query Format (Overpass QL):                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  [out:json][timeout:25];                                     │  │
│  │  (                                                            │  │
│  │    node["amenity"="convenience"](around:3000,35.681,139.767);│  │
│  │    node["amenity"="cafe"](around:3000,35.681,139.767);       │  │
│  │    node["amenity"="restaurant"](around:3000,35.681,139.767); │  │
│  │    node["railway"="station"](around:3000,35.681,139.767);    │  │
│  │  );                                                           │  │
│  │  out body;                                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Response (JSON):                                                   │
│  {                                                                  │
│    "elements": [                                                    │
│      {                                                              │
│        "type": "node",                                              │
│        "id": 123456789,                                             │
│        "lat": 35.681,                                               │
│        "lon": 139.767,                                              │
│        "tags": {                                                    │
│          "amenity": "cafe",                                         │
│          "name": "Starbucks",                                       │
│          "opening_hours": "Mo-Su 07:00-22:00"                       │
│        }                                                            │
│      },                                                             │
│      ...                                                            │
│    ]                                                                │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Flow 1: Demo Data Mode (Offline)

```
User selects hour (slider) 
    → main.js fetch /api/points?hour=X
    → server.js return filtered demo data (3000 points → ~125 per hour)
    → main.js receive points
    → Grid Algorithm: binning lat/lon → count per cell
    → Render rectangles with color/opacity
    → Sort cells by count → Top-5
    → Display on map + list
```

### Flow 2: Real POI Mode (Overpass API)

```
User selects "Real POI"
    → Overpass controls show
User inputs lat/lon (or click map)
User selects categories (checkboxes)
User clicks "Fetch POI"
    → main.js fetch /api/poi?lat=...&lon=...&radius=...&categories=...
    → server.js check cache
    → if cache hit: return cached data
    → if cache miss:
        → Build Overpass QL query dynamically
        → POST to Overpass API (axios)
        → Wait ~3-5 seconds
        → Parse JSON response (elements array)
        → Map to POI array: {id, lat, lon, category, name}
        → Store in cache (TTL 1 hour)
        → Return {center, radius, categories, count, poi}
    → main.js receive POI
    → Convert POI to points with synthetic hour distribution
    → currentPoints = poi.map(...) with hour 0-23
    → Render grid (same algorithm as demo)
    → Display on map + Top-5
    → Hour slider now works on real POI data
```

---

## Component Interaction

```
┌──────────────┐     events     ┌──────────────┐
│   UI Panel   │ ──────────────→ │   main.js    │
│ (HTML inputs)│ ←────────────── │ (Event       │
│              │   update labels │  Handlers)   │
└──────────────┘                 └──────┬───────┘
                                        │
                                        │ fetch()
                                        ▼
                                 ┌──────────────┐
                                 │  server.js   │
                                 │  (Express)   │
                                 └──────┬───────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
            ┌───────────────┐   ┌──────────────┐   ┌──────────────┐
            │ Demo Data     │   │ Cache (Map)  │   │ Overpass API │
            │ Generator     │   │ TTL: 1 hour  │   │ (External)   │
            │ (3000 points) │   │              │   │              │
            └───────────────┘   └──────────────┘   └──────────────┘
```

---

## Grid Algorithm Detail

```
Input:
  • points: [{id, lat, lon, hour, ...}]
  • bounds: {latMin, latMax, lonMin, lonMax}
  • cellSize: 0.01 (in degrees, ~1km)
  • hour: 0-23 (selected hour)

Step 1: Filter by hour
  filtered = points.filter(p => p.hour === hour)

Step 2: Binning (assign to grid cells)
  counts = Map<key, count>
  
  for each point p in filtered:
    if p not in bounds: skip
    
    i = floor((p.lat - bounds.latMin) / cellSize)
    j = floor((p.lon - bounds.lonMin) / cellSize)
    key = "${i},${j}"
    
    counts[key] = (counts[key] || 0) + 1

Step 3: Find max count (normalization)
  maxCount = max(counts.values())

Step 4: Render each cell
  for each [key, count] in counts:
    parse i, j from key
    
    south = bounds.latMin + i * cellSize
    north = south + cellSize
    west = bounds.lonMin + j * cellSize
    east = west + cellSize
    
    // Normalize opacity
    opacity = 0.10 + 0.70 * (count / maxCount)
    
    // Color by intensity
    if count/maxCount > 0.7:
      color = "red"    // hot (peak activity)
    else if count/maxCount > 0.4:
      color = "orange" // warm
    else if count/maxCount > 0.2:
      color = "yellow" // medium
    else:
      color = "blue"   // cool
    
    // Draw rectangle
    L.rectangle([[south,west],[north,east]], {
      color: color,
      fillColor: color,
      fillOpacity: opacity
    }).addTo(gridLayer)

Step 5: Top-5 Hotspots
  cells = []
  for each [key, count] in counts:
    centerLat = bounds.latMin + (i + 0.5) * cellSize
    centerLon = bounds.lonMin + (j + 0.5) * cellSize
    cells.push({key, count, centerLat, centerLon})
  
  cells.sort((a,b) => b.count - a.count) // descending
  top5 = cells.slice(0, 5)
  
  displayList(top5) // show in UI

Output:
  • Grid rectangles on map (color-coded)
  • Top-5 list in sidebar
  • Stats: totalPoints, inViewPoints, cellCount, maxCount
```

---

## Cache Strategy

```
┌─────────────────────────────────────────────────────────┐
│                   Cache Management                      │
│                                                         │
│  Request: /api/poi?lat=35.681&lon=139.767&...          │
│  Cache Key: "35.681,139.767,3000,cafe,convenience"     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  cache.get(key)                                 │   │
│  │    ↓                                            │   │
│  │  exists?                                        │   │
│  │    ↓                                            │   │
│  │  yes → check TTL                                │   │
│  │    ↓                                            │   │
│  │  if (now - timestamp) < 3600000ms (1 hour):    │   │
│  │    return cached.data + {cached: true}          │   │
│  │  else:                                          │   │
│  │    cache.delete(key) → fetch fresh              │   │
│  │                                                 │   │
│  │  no → fetch from Overpass                       │   │
│  │    ↓                                            │   │
│  │  cache.set(key, {data, timestamp: Date.now()}) │   │
│  │    ↓                                            │   │
│  │  return data + {cached: false}                  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Benefits:                                              │
│  • Reduce Overpass API calls (avoid rate limit)        │
│  • Faster response (instant vs 3-5 seconds)            │
│  • Offline mode support (if cached before)             │
│                                                         │
│  Limitations:                                           │
│  • In-memory only (lost on server restart)             │
│  • No persistence (no database)                        │
│  • Simple TTL (no smart invalidation)                  │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Client)                     │
├─────────────────────────────────────────────────────────┤
│  • HTML5 (structure)                                    │
│  • CSS3 (styling, grid layout)                          │
│  • JavaScript (ES6+, async/await)                       │
│  • Leaflet 1.9.4 (map library)                          │
│  • OpenStreetMap (free tile layer)                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Backend (Server)                      │
├─────────────────────────────────────────────────────────┤
│  • Node.js 18+ (runtime)                                │
│  • Express 4.x (web framework)                          │
│  • Axios 1.x (HTTP client for Overpass)                 │
│  • ES Modules (import/export)                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   External Services                     │
├─────────────────────────────────────────────────────────┤
│  • Overpass API (OpenStreetMap query service)           │
│  • OSM Tile Servers (map tiles)                         │
│  • Leaflet CDN (library delivery)                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Development Tools                     │
├─────────────────────────────────────────────────────────┤
│  • npm (package manager)                                │
│  • Git (version control)                                │
│  • VS Code (editor, optional)                           │
│  • curl (API testing)                                   │
│  • Browser DevTools (debugging)                         │
└─────────────────────────────────────────────────────────┘
```

---

## Deployment Options (Future)

```
Current: Localhost (WSL Ubuntu 24)
  → http://localhost:8000
  → Access from Windows browser
  → No deployment needed for assignment

Future Options (if want to deploy):

1. Vercel (Free)
   → Serverless Node.js
   → Auto-deploy from Git
   → HTTPS + custom domain
   → Limitation: Cold start, no persistent cache

2. Netlify (Free)
   → Similar to Vercel
   → Netlify Functions for API
   → HTTPS + custom domain

3. Heroku (Free tier discontinued, paid)
   → Classic PaaS
   → Persistent process
   → Good for caching

4. Railway (Free $5 credit/month)
   → Docker-based
   → Persistent storage
   → Good for long-running server

5. Self-hosted (VPS)
   → AWS EC2, DigitalOcean, Linode
   → Full control
   → Need to manage server

Note: For tugas akhir, localhost is sufficient.
```

---

**File**: ARCHITECTURE.md  
**Created**: 29 Januari 2026  
**Purpose**: Visual documentation of system architecture  
**For**: Urban Activity Pulse Map - Web GIS Tugas Akhir
