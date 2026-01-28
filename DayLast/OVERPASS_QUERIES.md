# Overpass API Queries - Lengkap & Praktis

Dokumentasi lengkap untuk query Overpass API dalam proyek **Urban Activity Pulse Map**.

---

## 📡 Overpass API Basics

### Endpoint
```
POST https://overpass-api.de/api/interpreter
Content-Type: text/plain
```

### Alternative Endpoints (Backup)
```
https://overpass.kumi.systems/api/interpreter
https://overpass.osm.ch/api/interpreter
https://z.overpass-api.de/api/interpreter
```

### Request Format
```http
POST /api/interpreter HTTP/1.1
Host: overpass-api.de
Content-Type: text/plain

[out:json][timeout:25];
(
  node["amenity"="cafe"](around:3000,35.681,139.767);
);
out body;
```

### Response Format (JSON)
```json
{
  "version": 0.6,
  "generator": "Overpass API",
  "elements": [
    {
      "type": "node",
      "id": 123456789,
      "lat": 35.6815,
      "lon": 139.7671,
      "tags": {
        "amenity": "cafe",
        "name": "Starbucks",
        "opening_hours": "Mo-Su 07:00-22:00"
      }
    }
  ]
}
```

---

## 🏪 Query Templates

### 1. Convenience Stores (Konbini)

**Query:**
```overpassql
[out:json][timeout:25];
(
  node["amenity"="convenience"](around:3000,35.681,139.767);
);
out body;
```

**Tags Included:**
- `amenity=convenience`
- Common names: 7-Eleven, FamilyMart, Lawson, Circle K, etc.

**Expected Count (Tokyo):** ~50-100 per 3km radius

---

### 2. Cafes

**Query:**
```overpassql
[out:json][timeout:25];
(
  node["amenity"="cafe"](around:3000,35.681,139.767);
);
out body;
```

**Tags Included:**
- `amenity=cafe`
- Includes: Starbucks, Tully's, Doutor, local cafes

**Expected Count (Tokyo):** ~30-80 per 3km radius

---

### 3. Restaurants

**Query:**
```overpassql
[out:json][timeout:25];
(
  node["amenity"="restaurant"](around:3000,35.681,139.767);
);
out body;
```

**Tags Included:**
- `amenity=restaurant`
- All cuisine types (Japanese, Italian, Chinese, etc.)

**Expected Count (Tokyo):** ~100-300 per 3km radius

---

### 4. Stations (Railway & Public Transport)

**Query:**
```overpassql
[out:json][timeout:25];
(
  node["railway"="station"](around:3000,35.681,139.767);
  node["public_transport"="station"](around:3000,35.681,139.767);
);
out body;
```

**Tags Included:**
- `railway=station` (train stations)
- `public_transport=station` (bus, tram, metro)

**Expected Count (Tokyo):** ~5-20 per 3km radius

---

### 5. Combined Query (All Categories)

**Query (Used in Our App):**
```overpassql
[out:json][timeout:25];
(
  node["amenity"="convenience"](around:3000,35.681,139.767);
  node["amenity"="cafe"](around:3000,35.681,139.767);
  node["amenity"="restaurant"](around:3000,35.681,139.767);
  node["railway"="station"](around:3000,35.681,139.767);
  node["public_transport"="station"](around:3000,35.681,139.767);
);
out body;
```

**Expected Total Count (Tokyo):** ~200-500 POI

---

## 📐 Query Parameters

### `around:RADIUS,LAT,LON`

Search within radius (meters) from a point.

**Example:**
```overpassql
node["amenity"="cafe"](around:5000,35.681,139.767);
```
- Radius: 5000m (5km)
- Center: Tokyo Station (35.681, 139.767)

**Recommended Radius:**
- Urban area: 1000-3000m
- Suburban: 3000-5000m
- Rural: 5000-10000m
- **Max safe**: <15000m (to avoid timeout)

---

### `bbox:SOUTH,WEST,NORTH,EAST`

Search within bounding box (rectangle).

**Example:**
```overpassql
node["amenity"="cafe"](35.67,139.75,35.69,139.78);
```
- South: 35.67
- West: 139.75
- North: 35.69
- East: 139.78

**Use Case:** When viewport bounds are known (Leaflet `map.getBounds()`).

---

### `[out:json]`

Output format. Options:
- `json` (default, recommended)
- `xml` (verbose)
- `csv` (limited fields)

---

### `[timeout:SECONDS]`

Max query execution time.

**Recommended:**
- Simple query: `[timeout:10]`
- Complex/large radius: `[timeout:25]`
- Very complex: `[timeout:60]` (but may hit server limit)

---

### `out body;`

Output detail level. Options:
- `out body;` (full tags, lat, lon) ← **recommended**
- `out center;` (geometry center only)
- `out ids;` (IDs only, no coordinates)
- `out meta;` (full + metadata: version, timestamp, user)

---

## 🔧 Advanced Queries

### Query by Multiple Tags (OR)

**Get all food places (cafe OR restaurant):**
```overpassql
[out:json][timeout:25];
(
  node["amenity"~"^(cafe|restaurant)$"](around:3000,35.681,139.767);
);
out body;
```

**Regex:** `~"^(cafe|restaurant)$"` matches "cafe" or "restaurant".

---

### Query with Name Filter

**Get Starbucks only:**
```overpassql
[out:json][timeout:25];
(
  node["amenity"="cafe"]["name"~"Starbucks"](around:3000,35.681,139.767);
);
out body;
```

---

### Query with Opening Hours

**Get 24-hour convenience stores:**
```overpassql
[out:json][timeout:25];
(
  node["amenity"="convenience"]["opening_hours"="24/7"](around:3000,35.681,139.767);
);
out body;
```

**Note:** Many POI don't have `opening_hours` tag, so this may return few results.

---

### Query by Area (Geocoded)

**Get all cafes in Tokyo (entire city):**
```overpassql
[out:json][timeout:60];
area["name"="東京都"]["admin_level"="4"];
(
  node["amenity"="cafe"](area);
);
out body;
```

**Warning:** Very large query, may timeout.

---

## 🌍 Sample Locations for Testing

### Tokyo Station (Japan)
```
Lat: 35.681236
Lon: 139.767125
Categories: convenience, cafe, restaurant, station
Radius: 3000m
Expected POI: ~300-500
```

### Times Square (New York, USA)
```
Lat: 40.758896
Lon: -73.985130
Categories: convenience, cafe, restaurant, station
Radius: 3000m
Expected POI: ~200-400
```

### Piccadilly Circus (London, UK)
```
Lat: 51.509980
Lon: -0.134270
Categories: cafe, restaurant, station
Radius: 3000m
Expected POI: ~150-300
```

### Monas (Jakarta, Indonesia)
```
Lat: -6.175110
Lon: 106.827153
Categories: convenience, cafe, restaurant
Radius: 3000m
Expected POI: ~50-150
```

### Shibuya Crossing (Tokyo, Japan)
```
Lat: 35.659515
Lon: 139.700464
Categories: convenience, cafe, restaurant, station
Radius: 2000m
Expected POI: ~400-600 (very dense!)
```

---

## 🚦 Rate Limiting & Best Practices

### Overpass API Rate Limits

**Official Limits:**
- Max 2 concurrent queries per IP
- Max query time: 180 seconds (server-side)
- Fair use policy (no hammer mode)

**Our Implementation:**
- Client-side: 1 query at a time
- Caching: 1 hour TTL (reduce API calls)
- Timeout: 30 seconds (axios config)

---

### Best Practices

1. **Always cache results** (avoid repeated same query)
2. **Use reasonable radius** (<5000m for urban)
3. **Filter categories** (don't query all at once if not needed)
4. **Handle errors gracefully** (timeout, server down, rate limit)
5. **Respect server load** (avoid query during peak hours if possible)
6. **Use backup endpoints** (if main endpoint down)

---

## 📊 Query Performance

| Radius | Categories | Expected POI | Query Time | Cache? |
|--------|-----------|--------------|------------|--------|
| 1000m  | 2         | ~50-100      | 1-2s       | ✅     |
| 3000m  | 4         | ~200-500     | 3-5s       | ✅     |
| 5000m  | 4         | ~500-1000    | 5-10s      | ✅     |
| 10000m | 4         | ~1000-2000   | 10-20s     | ✅     |
| 15000m | 4         | ~2000+       | 20-30s     | ⚠️     |

**Recommendation:** Use 3000m radius (good balance).

---

## 🐛 Common Errors & Solutions

### Error: `Timeout`
**Cause:** Query too complex or server overloaded.
**Solution:**
- Reduce radius
- Reduce categories
- Try alternative endpoint
- Wait & retry (exponential backoff)

### Error: `429 Too Many Requests`
**Cause:** Rate limit exceeded.
**Solution:**
- Wait 60 seconds
- Check cache (should prevent this)
- Reduce query frequency

### Error: `Empty elements array`
**Cause:** No POI in the specified area.
**Solution:**
- Try larger radius
- Try different categories
- Check if location is in water/remote area

### Error: `Invalid QL syntax`
**Cause:** Malformed Overpass QL query.
**Solution:**
- Validate query at https://overpass-turbo.eu/
- Check brackets `()` and semicolons `;`
- Ensure proper tag format `["key"="value"]`

---

## 🔗 Useful Resources

- **Overpass API Home**: https://overpass-api.de/
- **Overpass Turbo (Query Builder)**: https://overpass-turbo.eu/
- **Overpass QL Guide**: https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL
- **OSM Tag Info**: https://taginfo.openstreetmap.org/
- **OSM Wiki (Tags)**: https://wiki.openstreetmap.org/wiki/Map_Features

---

## 🧪 Testing Queries (curl)

### Test 1: Convenience Stores in Tokyo
```bash
curl -X POST "https://overpass-api.de/api/interpreter" \
  -H "Content-Type: text/plain" \
  -d '[out:json][timeout:25];
(
  node["amenity"="convenience"](around:3000,35.681,139.767);
);
out body;'
```

### Test 2: All Categories in New York
```bash
curl -X POST "https://overpass-api.de/api/interpreter" \
  -H "Content-Type: text/plain" \
  -d '[out:json][timeout:25];
(
  node["amenity"="convenience"](around:3000,40.758,-73.985);
  node["amenity"="cafe"](around:3000,40.758,-73.985);
  node["amenity"="restaurant"](around:3000,40.758,-73.985);
  node["railway"="station"](around:3000,40.758,-73.985);
);
out body;' | jq '.elements | length'
```

**Expected Output:** Number of POI found.

---

## 🎯 Integration with Our App

### Backend (`server.js`)

```javascript
const OVERPASS_URL = "https://overpass-api.de/api/interpreter";

app.get("/api/poi", async (req, res) => {
  const { lat, lon, radius = 3000, categories = "convenience,cafe" } = req.query;
  
  // Build query dynamically
  const cats = categories.split(",");
  const queries = [];
  
  for (const cat of cats) {
    if (cat === "convenience") {
      queries.push(`node["amenity"="convenience"](around:${radius},${lat},${lon});`);
    } else if (cat === "cafe") {
      queries.push(`node["amenity"="cafe"](around:${radius},${lat},${lon});`);
    }
    // ... etc
  }
  
  const overpassQuery = `
    [out:json][timeout:25];
    (
      ${queries.join("\\n")}
    );
    out body;
  `;
  
  const response = await axios.post(OVERPASS_URL, overpassQuery, {
    headers: { "Content-Type": "text/plain" },
    timeout: 30000
  });
  
  const poi = response.data.elements.map(el => ({
    id: el.id,
    lat: el.lat,
    lon: el.lon,
    category: el.tags?.amenity || el.tags?.railway || "unknown",
    name: el.tags?.name || "(unnamed)"
  }));
  
  res.json({ count: poi.length, poi });
});
```

### Frontend (`main.js`)

```javascript
async function fetchPOIFromOverpass() {
  const lat = document.getElementById("poiLat").value;
  const lon = document.getElementById("poiLon").value;
  const radius = document.getElementById("poiRadius").value;
  const categories = getSelectedCategories(); // "convenience,cafe"
  
  const res = await fetch(`/api/poi?lat=${lat}&lon=${lon}&radius=${radius}&categories=${categories}`);
  const data = await res.json();
  
  // Convert POI to points with synthetic hours
  currentPoints = data.poi.map(poi => ({
    id: poi.id,
    lat: poi.lat,
    lon: poi.lon,
    hour: generateSyntheticHour(), // 0-23
    category: poi.category,
    name: poi.name
  }));
  
  renderGrid();
}
```

---

**Terakhir diperbarui**: 29 Januari 2026
