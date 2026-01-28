# Urban Activity Pulse Map - Tugas Akhir Web GIS Spatio-Temporal

**Nama**: [Isi nama Anda]  
**NIM**: [Isi NIM Anda]  
**Tim**: Individual / [Nama anggota lain jika ada]  
**Mata Kuliah**: Algoritma dan Pemrograman (Web GIS - Spatio-Temporal)  
**Tanggal**: Januari 2026

---

## 📋 Deskripsi Sistem

**Urban Activity Pulse Map** adalah aplikasi Web GIS yang menampilkan visualisasi spatio-temporal dari aktivitas urban menggunakan:

- **Backend**: Node.js + Express
- **Frontend**: HTML/CSS/JavaScript + Leaflet + OpenStreetMap
- **Data**: Overpass API (OpenStreetMap) - 100% GRATIS
- **Platform**: Localhost (Ubuntu 24 WSL)

### Fitur Utama

1. **Peta Interaktif** dengan Leaflet + OSM tiles
2. **Slider Waktu (0–23 jam)** - mengubah visualisasi density secara real-time
3. **Activity Density Grid** - heatmap berbasis grid cell dengan normalisasi warna
4. **Top-5 Hotspot** - daftar area dengan aktivitas tertinggi, klik untuk zoom
5. **Dual Data Source**:
   - **Demo Data** (offline, deterministik) untuk testing cepat
   - **Real POI** (Overpass API) untuk data riil: convenience store, cafe, restaurant, station
6. **Click-to-fetch** - klik peta untuk set lokasi dan fetch POI dalam radius tertentu

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (Client)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Leaflet Map │  │ Time Slider  │  │  Top-5 List  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON
┌────────────────────────▼────────────────────────────────────┐
│             Express Server (Node.js)                        │
│  ┌──────────────────────────────────────────────────┐      │
│  │ Endpoints:                                       │      │
│  │  GET  /api/points?hour=...  (demo data)         │      │
│  │  GET  /api/poi?lat=...&lon=...&radius=...       │      │
│  │  POST /api/grid (compute density)               │      │
│  │  GET  /api/health                                │      │
│  └──────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │ In-Memory Cache (Map) + TTL 1 hour              │      │
│  └──────────────────────────────────────────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ Overpass QL
┌────────────────────────▼────────────────────────────────────┐
│         Overpass API (OpenStreetMap)                        │
│  https://overpass-api.de/api/interpreter                    │
│  Query POI: amenity=convenience|cafe|restaurant|station     │
└─────────────────────────────────────────────────────────────┘
```

### Folder Structure

```
DayLast/
├── README.md                    # Dokumentasi utama (file ini)
├── BLUEPRINT.md                 # Blueprint 3 minggu (milestone)
├── OVERPASS_QUERIES.md          # Query Overpass lengkap
├── DELIVERABLES_CHECKLIST.md   # Checklist untuk penilaian
├── illustrations/               # Screenshot, diagram
│   ├── screenshot-demo.png
│   ├── screenshot-overpass.png
│   ├── architecture-diagram.png
│   └── demo-flow.gif
└── webgis_daylast/              # Source code
    ├── package.json
    ├── server.js                # Express server
    └── public/
        ├── index.html           # UI
        ├── main.js              # Frontend logic
        └── style.css            # Styling
```

---

## 🚀 Cara Menjalankan (Ubuntu 24 WSL)

### Prerequisites

1. **Node.js** versi 18+ sudah terinstall
2. **Internet connection** (untuk fetch Overpass API dan OSM tiles)

### Step 1: Install Dependencies

```bash
cd ~/TEUKU_zikri/DayLast/webgis_daylast
npm install
```

Akan install:
- `express` (web server)
- `axios` (HTTP client untuk Overpass API)

### Step 2: Start Server

```bash
npm start
```

Output:
```
✅ Server running on http://localhost:8000
   (WSL) Open from Windows browser: http://localhost:8000
```

### Step 3: Buka di Browser

Dari **Windows browser** (Chrome/Firefox/Edge), buka:

```
http://localhost:8000
```

### Step 4: Test Demo Data (Offline)

1. **Default mode**: "Demo Data" sudah aktif
2. **Geser slider jam** (0–23) → heatmap berubah
3. **Zoom/pan peta** → grid dihitung ulang untuk viewport
4. **Klik item Top-5** → peta zoom ke hotspot
5. **Adjust cell size** → ubah resolusi grid

### Step 5: Test Real POI (Overpass API)

1. **Pilih "Real POI (Overpass API)"**
2. **Atur lokasi**:
   - Input manual: masukkan lat/lon (contoh: Tokyo Station 35.681 / 139.767)
   - Click map: klik peta untuk set lokasi otomatis
3. **Pilih kategori**: Convenience, Cafe, Restaurant, Station
4. **Set radius**: default 3000m (3km)
5. **Klik "Fetch POI from Overpass"**
6. **Wait**: akan ada loading indicator
7. **Result**: POI muncul di peta, slider jam aktif

---

## 🧮 Algoritma: Activity Density Grid

### Input
- Array of points: `[{lat, lon, hour, ...}]`
- Viewport bounds: `{latMin, latMax, lonMin, lonMax}`
- Cell size: `cellSize` (dalam derajat, default 0.01 ≈ 1km)
- Selected hour: `hour` (0–23)

### Algorithm

```javascript
function computeActivityGrid(points, bounds, cellSize, hour) {
  // 1. Filter points by hour
  let filtered = points.filter(p => p.hour === hour);
  
  // 2. Count points per grid cell
  let counts = {};
  for (let p of filtered) {
    if (!inBounds(p, bounds)) continue;
    
    // Grid index
    let i = floor((p.lat - bounds.latMin) / cellSize);
    let j = floor((p.lon - bounds.lonMin) / cellSize);
    let key = `${i},${j}`;
    
    counts[key] = (counts[key] || 0) + 1;
  }
  
  // 3. Build cell array with bounds & center
  let cells = [];
  for (let [key, count] of Object.entries(counts)) {
    let [i, j] = key.split(',').map(Number);
    let south = bounds.latMin + i * cellSize;
    let north = south + cellSize;
    let west = bounds.lonMin + j * cellSize;
    let east = west + cellSize;
    
    cells.push({
      key, count,
      bounds: {south, north, west, east},
      center: {lat: (south+north)/2, lon: (west+east)/2}
    });
  }
  
  // 4. Sort by count descending → Top-5
  cells.sort((a, b) => b.count - a.count);
  let top5 = cells.slice(0, 5);
  
  return { cells, top5, maxCount: cells[0]?.count || 0 };
}
```

### Kompleksitas
- **Time**: O(n + k log k)
  - n = jumlah points (filter + count)
  - k = jumlah cells (sort)
- **Space**: O(k)
  - k cells dalam viewport

### Normalisasi Warna (Heatmap)
```javascript
opacity = 0.10 + 0.70 * (count / maxCount)

if (count/maxCount > 0.7) color = "red"    // hot
else if (count/maxCount > 0.4) color = "orange"  // warm
else if (count/maxCount > 0.2) color = "yellow"  // medium
else color = "blue"  // cool
```

---

## 🗺️ Overpass API: Query POI

### Endpoint
```
POST https://overpass-api.de/api/interpreter
Content-Type: text/plain
```

### Query Format (Overpass QL)

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

### Parameters
- `around:RADIUS,LAT,LON` - radius dalam meter
- `node["key"="value"]` - filter by tag
- `out body` - return full node data (lat, lon, tags)

### Response (JSON)
```json
{
  "elements": [
    {
      "type": "node",
      "id": 123456,
      "lat": 35.681,
      "lon": 139.767,
      "tags": {
        "amenity": "cafe",
        "name": "Cafe Example",
        "opening_hours": "Mo-Fr 08:00-20:00"
      }
    },
    ...
  ]
}
```

### Caching Strategy
- **In-memory Map**: `cache.set(key, {data, timestamp})`
- **TTL**: 1 hour (3600000ms)
- **Cache key**: `"${lat},${lon},${radius},${categories}"`
- **Hit**: return cached data + `cached: true`
- **Miss**: fetch Overpass → cache → return

---

## 📊 Aspek Spatio-Temporal

### Spatio (Space)
- **Grid cells** dengan lat/lon bounds
- **Distance-based query**: radius dari titik pusat
- **Viewport filtering**: hanya render data in-view
- **Zoom-adaptive**: grid resolution bisa diubah

### Temporal (Time)
- **Hour slider (0–23)**: simulasi time-of-day
- **Dynamic filtering**: filter points by selected hour
- **Activity patterns**:
  - Peak hours: 8–10 (pagi), 17–20 (sore)
  - Off-peak: 0–6 (malam), 22–23 (larut)
- **Real-time update**: grid re-render saat slider berubah

### Synthetic Hour Distribution (untuk POI)
Karena Overpass API tidak return "jam buka real-time", kita gunakan **synthetic distribution**:

```javascript
// Weighted distribution
if (rand < 15%) hour = 8-10   // morning peak
else if (rand < 30%) hour = 17-20  // evening peak
else if (rand < 50%) hour = 11-16  // midday
else hour = random 0-23  // rest distributed
```

---

## 📸 Screenshot & Demo

Lihat folder `illustrations/`:
- `screenshot-demo.png` - Demo data mode
- `screenshot-overpass.png` - Real POI mode
- `architecture-diagram.png` - System architecture
- `demo-flow.gif` - Animated demo (opsional)

---

## 🎯 Deliverables Checklist

✅ **Source Code**
- `server.js` dengan Overpass integration + caching
- `index.html`, `main.js`, `style.css` dengan UI lengkap
- `package.json` dengan dependencies

✅ **Dokumentasi**
- README.md (file ini) dengan penjelasan lengkap
- Blueprint 3 minggu (BLUEPRINT.md)
- Overpass queries (OVERPASS_QUERIES.md)
- Checklist deliverables (DELIVERABLES_CHECKLIST.md)

✅ **Fitur Wajib**
- [x] Peta interaktif (Leaflet + OSM)
- [x] Slider waktu (0–23 jam)
- [x] Activity density grid (heatmap)
- [x] Top-5 hotspot (clickable)
- [x] Data gratis (Overpass API)
- [x] Spatio-temporal algorithm

✅ **Bonus**
- [x] Dual data source (demo + real)
- [x] Click-to-set location
- [x] Category selection (multiple)
- [x] Caching (performance)
- [x] Error handling
- [x] Responsive UI

---

## 🎤 Presentasi (3 Menit Demo)

### Script Demo

**Menit 1: Intro + Demo Data**
```
"Selamat pagi/siang. Saya [nama], NIM [nim].
Ini adalah Urban Activity Pulse Map, aplikasi Web GIS untuk
visualisasi spatio-temporal aktivitas urban.

[Show browser] Di sini ada peta dengan density grid.
[Geser slider jam] Ketika saya geser slider waktu,
grid berubah sesuai distribusi aktivitas per jam.

[Zoom/pan] Grid dihitung real-time sesuai viewport.
[Klik Top-5] Top-5 hotspot di sini, klik untuk zoom ke area."
```

**Menit 2: Overpass API**
```
"Sekarang mode Real POI. [Toggle radio]
Saya pilih lokasi [klik peta atau input manual],
set radius 3km, pilih kategori Cafe dan Convenience.

[Klik Fetch POI] Sistem fetch dari Overpass API...
[Wait] Loading... [Result muncul]
Done! Sekarang ada [X] POI dari OpenStreetMap.

Data ini gratis 100%, tanpa billing, langsung dari
OpenStreetMap via Overpass API."
```

**Menit 3: Algoritma + Q&A**
```
"Algoritma density grid:
1. Filter points by hour
2. Count per grid cell (binning)
3. Normalisasi warna (heatmap)
4. Sort untuk Top-5

Kompleksitas O(n + k log k).

Backend: Node.js + Express dengan caching 1 jam.
Frontend: Leaflet untuk peta, Vanilla JS.

Semua source code ada di repo. Terima kasih!"
```

### Q&A Anticipation

**Q: Kenapa pakai Overpass API?**
A: Gratis, no billing, data OpenStreetMap lengkap, cocok untuk tugas akademik.

**Q: Bagaimana handle jam buka POI?**
A: Tag `opening_hours` ada, tapi kita gunakan synthetic distribution untuk demo spatio-temporal.

**Q: Kenapa ada mode demo?**
A: Untuk testing offline dan demo cepat tanpa wait Overpass fetch.

**Q: Cell size optimal?**
A: Tergantung zoom level. Default 0.01° (~1km) bagus untuk urban scale.

**Q: Bisa deploy ke cloud?**
A: Bisa, tapi tugas ini cukup localhost. Tinggal deploy ke Vercel/Netlify (gratis).

---

## 🛠️ Troubleshooting

### Error: `Cannot find module 'axios'`
```bash
npm install
```

### Error: Overpass API timeout
- **Cause**: Query terlalu kompleks atau radius terlalu besar
- **Fix**: Kurangi radius (<5000m) atau pilih lebih sedikit kategori

### Error: CORS (jika buka file:///)
- **Cause**: Buka HTML langsung, bukan via server
- **Fix**: Harus pakai `npm start` dan buka `http://localhost:8000`

### Peta tidak muncul
- **Check**: Console error? Leaflet CDN loaded?
- **Fix**: Pastikan internet aktif untuk load Leaflet + OSM tiles

### Cache tidak clear
- **Restart server**: Cache in-memory, hilang saat restart

---

## 📚 Referensi

- **Leaflet**: https://leafletjs.com/
- **OpenStreetMap**: https://www.openstreetmap.org/
- **Overpass API**: https://overpass-api.de/
- **Overpass QL Docs**: https://wiki.openstreetmap.org/wiki/Overpass_API
- **Express.js**: https://expressjs.com/

---

## 📝 Catatan Pengembangan

**Apa yang sudah dicapai:**
- ✅ Full Overpass integration dengan caching
- ✅ Dual data source (demo + real)
- ✅ Activity density algorithm dengan normalisasi warna
- ✅ Top-5 hotspot interactive
- ✅ Click-to-set location
- ✅ Comprehensive documentation

**Potensi improvement (future work):**
- [ ] Real opening_hours parsing (jika tag tersedia)
- [ ] Save/load favorite locations
- [ ] Export data to GeoJSON/CSV
- [ ] Heatmap.js plugin untuk alternative visualization
- [ ] Animation slider (auto-play 0→23)

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik (tugas akhir).
Semua data dari OpenStreetMap (ODbL license).

**Author**: [Nama Anda]  
**Date**: Januari 2026  
**Course**: Algoritma & Pemrograman (Web GIS)

---

**Terakhir diperbarui**: 29 Januari 2026
