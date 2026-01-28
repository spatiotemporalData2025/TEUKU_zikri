# Checklist Deliverables - Penilaian Tugas Akhir Web GIS

Checklist lengkap untuk memastikan semua komponen tugas terpenuhi.

---

## ✅ 1. Source Code & Functionality

### Backend (`server.js`)
- [x] Express server setup (port 8000)
- [x] Endpoint `/api/points?hour=X` (demo data)
- [x] Endpoint `/api/poi?lat=...&lon=...&radius=...&categories=...` (Overpass API)
- [x] Endpoint `/api/health` (health check)
- [x] Endpoint `/api/grid` (compute density - optional, bisa di frontend)
- [x] Overpass API integration (axios)
- [x] In-memory caching (Map) dengan TTL 1 hour
- [x] Error handling (timeout, invalid input, API errors)
- [x] CORS enabled (jika perlu)
- [x] Logging (console.log untuk debug)

**Kriteria Sukses:**
- Server bisa dijalankan dengan `npm start`
- Semua endpoint return JSON yang benar
- Tidak crash saat error

---

### Frontend (HTML/CSS/JS)

#### `index.html`
- [x] Proper HTML5 structure (doctype, meta viewport)
- [x] Leaflet CDN link (CSS + JS)
- [x] Sidebar untuk kontrol (panel kiri)
- [x] Map container (main kanan)
- [x] Toggle radio: Demo vs Real POI
- [x] Input fields: lat, lon, radius
- [x] Checkbox group: categories (convenience, cafe, restaurant, station)
- [x] Slider: hour (0-23)
- [x] Slider: cell size
- [x] Buttons: Fetch POI, Refresh, Fit to Data
- [x] Display: Top-5 hotspot (ordered list)
- [x] Display: Stats (total points, cells, max count)
- [x] Display: POI status (loading, success, error)

#### `style.css`
- [x] Grid layout (sidebar + map)
- [x] Card design untuk setiap section
- [x] Button styling (hover, disabled state)
- [x] Input styling (number, range, checkbox, radio)
- [x] Responsive (optional, karena localhost)
- [x] Color scheme konsisten

#### `main.js`
- [x] Leaflet map initialization
- [x] OSM tile layer
- [x] Grid layer (L.layerGroup)
- [x] Fetch demo data (`/api/points`)
- [x] Fetch real POI (`/api/poi`)
- [x] Grid algorithm: binning lat/lon → count per cell
- [x] Render rectangles (L.rectangle) dengan color + opacity
- [x] Top-5 hotspot: sort cells by count, display as list
- [x] Click top-5 item → map.setView()
- [x] Hour slider → filter points, re-render grid
- [x] Cell size slider → adjust resolution, re-render
- [x] Map events: moveend, zoomend → re-render grid
- [x] Click map → set lat/lon input (Overpass mode)
- [x] Toggle data source → show/hide Overpass controls
- [x] Error handling (fetch fail, empty data)

**Kriteria Sukses:**
- Peta muncul dengan OSM tiles
- Grid berubah saat slider geser
- Top-5 klik berfungsi
- Overpass fetch berhasil (dengan internet)
- No console errors (kecuali API down)

---

### `package.json`
- [x] Name: "webgis-daylast"
- [x] Version: 1.0.0
- [x] Type: "module" (ES6 import)
- [x] Scripts: `"start": "node server.js"`
- [x] Dependencies: express, axios

**Kriteria Sukses:**
- `npm install` berhasil
- `npm start` menjalankan server

---

## ✅ 2. Fitur Wajib (Core Requirements)

- [x] **Peta Interaktif**: Leaflet + OpenStreetMap tiles
- [x] **Interaksi User**: Slider, button, click map
- [x] **Algoritma Spatio-Temporal**: Grid density dengan filter waktu (hour)
- [x] **Visualisasi Heatmap**: Grid cells dengan opacity + color berdasarkan count
- [x] **Top-5 Hotspot**: List area tertinggi, clickable
- [x] **Data Gratis**: Demo data (deterministik) + Overpass API (OSM)
- [x] **Localhost Ready**: Bisa run di WSL Ubuntu 24, buka dari Windows browser

**Kriteria Sukses:**
- Semua fitur di atas berfungsi tanpa crash
- Demo bisa dilakukan dalam 3 menit

---

## ✅ 3. Dokumentasi

### `README.md`
- [x] **Header**: Nama, NIM, Tim, Judul Sistem, Tanggal
- [x] **Deskripsi Sistem**: 2-3 paragraf tentang apa yang dibuat
- [x] **Arsitektur**: Diagram (ASCII atau gambar)
- [x] **Cara Menjalankan**:
  - Prerequisites (Node.js, internet)
  - Step 1: Install dependencies
  - Step 2: Start server
  - Step 3: Buka browser
  - Step 4: Test demo mode
  - Step 5: Test Overpass mode
- [x] **Algoritma Grid**:
  - Pseudocode atau penjelasan step-by-step
  - Kompleksitas (time & space)
  - Normalisasi warna/opacity
- [x] **Overpass Query**: Contoh query dengan penjelasan
- [x] **Screenshot**: Placeholder atau link ke `illustrations/`
- [x] **Troubleshooting**: Common errors & solutions
- [x] **Referensi**: Link ke Leaflet, OSM, Overpass docs

**Kriteria Sukses:**
- Orang lain bisa clone repo, run, dan pakai sistem hanya dengan baca README
- Tidak ada step yang membingungkan

---

### `BLUEPRINT.md`
- [x] **Minggu 1**: Setup + Core features
- [x] **Minggu 2**: Overpass API + Advanced features
- [x] **Minggu 3**: Documentation + Testing + Presentation
- [x] **Milestone checkpoints**
- [x] **Risk mitigation**
- [x] **Time allocation**

**Kriteria Sukses:**
- Blueprint bisa dipake sebagai project plan untuk tugas serupa

---

### `OVERPASS_QUERIES.md`
- [x] **Endpoint & format request**
- [x] **Query templates** (convenience, cafe, restaurant, station)
- [x] **Parameters** (around, bbox, timeout, out)
- [x] **Advanced queries** (regex, filter by name)
- [x] **Sample locations** (Tokyo, NYC, London, etc.)
- [x] **Rate limiting & best practices**
- [x] **Common errors & solutions**
- [x] **curl test examples**

**Kriteria Sukses:**
- Developer baru bisa copy-paste query dan langsung pakai

---

### `DELIVERABLES_CHECKLIST.md`
- [x] **Source code checklist** (file ini)
- [x] **Fitur wajib checklist**
- [x] **Dokumentasi checklist**
- [x] **Testing checklist**
- [x] **Presentasi checklist**

**Kriteria Sukses:**
- Semua item checked = siap submit

---

## ✅ 4. Illustrations

### Folder `illustrations/`
- [ ] **screenshot-demo.png**:
  - Peta dengan grid density (jam 8 atau 18 - peak hour)
  - Sidebar dengan slider, Top-5 list
  - Stats di bawah
- [ ] **screenshot-overpass.png**:
  - UI Overpass controls (input fields, checkboxes)
  - Fetch button + status text
  - Grid dengan real POI
- [ ] **architecture-diagram.png** (atau ASCII di README):
  - Browser ↔ Express ↔ Overpass API
  - Cache layer
  - Endpoint list
- [ ] **demo-flow.gif** (optional):
  - Animated: slider geser → grid berubah
  - Tools: ScreenToGif (Windows), Peek (Linux)

**Kriteria Sukses:**
- Screenshot jelas, tidak blur
- Diagram mudah dipahami
- GIF <5MB (jika ada)

---

## ✅ 5. Testing

### Demo Data Mode
- [ ] **Test 1**: Jam 0 → grid muncul (sedikit points)
- [ ] **Test 2**: Jam 8 → grid lebih padat (peak hour)
- [ ] **Test 3**: Jam 12 → grid medium
- [ ] **Test 4**: Jam 18 → grid padat (peak hour)
- [ ] **Test 5**: Jam 23 → grid sedikit
- [ ] **Test 6**: Cell size 0.004 (kecil) → banyak cells
- [ ] **Test 7**: Cell size 0.03 (besar) → sedikit cells
- [ ] **Test 8**: Zoom in → grid recalculate
- [ ] **Test 9**: Pan map → grid recalculate
- [ ] **Test 10**: Click Top-5 item 1 → zoom to location
- [ ] **Test 11**: Click Fit to Data → map fit bounds
- [ ] **Test 12**: Click Refresh → grid re-render

**Kriteria Sukses:**
- Semua test pass, tidak ada error console

---

### Overpass API Mode
- [ ] **Test 1**: Tokyo (35.681, 139.767) + convenience,cafe + 3000m → fetch berhasil
- [ ] **Test 2**: New York (40.758, -73.985) + restaurant,station + 3000m → fetch berhasil
- [ ] **Test 3**: London (51.510, -0.134) + cafe + 3000m → fetch berhasil
- [ ] **Test 4**: Invalid lat/lon (999, 999) → error message graceful
- [ ] **Test 5**: Radius 50000m → timeout (expected), error message clear
- [ ] **Test 6**: No category selected → error message "Please select category"
- [ ] **Test 7**: Fetch 2x same location → second cached (check console log)
- [ ] **Test 8**: Click map → lat/lon input update
- [ ] **Test 9**: Fetch POI → hour slider still works, grid update
- [ ] **Test 10**: Change hour after fetch → grid re-render with filtered POI

**Kriteria Sukses:**
- Semua test pass, error handled gracefully
- Cache berfungsi (log "Cache hit")

---

### Edge Cases
- [ ] **Test 1**: No POI in radius (e.g. middle of ocean) → "No data in current view"
- [ ] **Test 2**: Very small cell size (0.001) → banyak cells, performance ok?
- [ ] **Test 3**: Very large cell size (0.1) → 1-2 cells only, still render
- [ ] **Test 4**: Overpass API down → error message + fallback ke demo mode
- [ ] **Test 5**: No internet → demo mode masih works, Overpass fail gracefully

**Kriteria Sukses:**
- Tidak crash di semua edge case
- Error message informatif

---

## ✅ 6. Presentasi (3 Menit)

### Persiapan
- [ ] **Script** ditulis (3 menit exact):
  - 1 min: Intro + demo data mode
  - 1 min: Overpass mode + fetch POI
  - 1 min: Algoritma + Q&A prep
- [ ] **Rehearsal** dengan timer (minimal 2x)
- [ ] **Backup plan** jika Overpass down: pakai demo mode
- [ ] **Q&A answers** prepared:
  - Kenapa Overpass?
  - Bagaimana handle opening hours?
  - Kompleksitas algoritma?
  - Bisa deploy?

### Slide (Optional, jika diminta)
- [ ] Slide 1: Title (nama, NIM, judul sistem)
- [ ] Slide 2: Arsitektur diagram
- [ ] Slide 3: Demo screenshot
- [ ] Slide 4: Algoritma (pseudocode)
- [ ] Slide 5: Tech stack (Node, Express, Leaflet, Overpass)
- [ ] Slide 6: Thank you + link repo

**Kriteria Sukses:**
- Presentasi lancar, tidak melebihi 3 menit
- Demo tidak crash
- Q&A dijawab dengan confident

---

## ✅ 7. Submission

### Repo Structure
```
DayLast/
├── README.md                    ✅
├── BLUEPRINT.md                 ✅
├── OVERPASS_QUERIES.md          ✅
├── DELIVERABLES_CHECKLIST.md   ✅
├── illustrations/
│   ├── screenshot-demo.png      ⬜ (TODO)
│   ├── screenshot-overpass.png  ⬜ (TODO)
│   └── architecture-diagram.png ⬜ (TODO)
└── webgis_daylast/
    ├── package.json             ✅
    ├── server.js                ✅
    └── public/
        ├── index.html           ✅
        ├── main.js              ✅
        └── style.css            ✅
```

### Submission Checklist
- [ ] **Git commit** semua file
- [ ] **Git push** ke repo (GitHub/GitLab)
- [ ] **ZIP file** (jika submit via upload)
  - Include: source code + documentation
  - Exclude: `node_modules/` (taruh di `.gitignore`)
- [ ] **Link repo** di submission form
- [ ] **README** tested: clone repo baru, run, works

**Kriteria Sukses:**
- Repo bisa di-clone oleh orang lain
- `npm install && npm start` langsung jalan

---

## 📊 Scoring Rubric (Self-Assessment)

| Kategori                  | Max | Self | Notes                       |
|---------------------------|-----|------|-----------------------------|
| **Source Code (30%)**     | 30  | __   |                             |
| - Backend (Express)       | 10  | __   | Endpoints, caching, errors  |
| - Frontend (Leaflet)      | 10  | __   | Map, grid, UI               |
| - Integration (Overpass)  | 10  | __   | Fetch, parse, display       |
|                           |     |      |                             |
| **Fitur (30%)**           | 30  | __   |                             |
| - Peta interaktif         | 5   | __   | Leaflet + OSM               |
| - Slider waktu            | 5   | __   | Hour 0-23, filter           |
| - Density grid            | 10  | __   | Algorithm, visualization    |
| - Top-5 hotspot           | 5   | __   | Sort, display, click        |
| - Data gratis             | 5   | __   | Demo + Overpass             |
|                           |     |      |                             |
| **Dokumentasi (20%)**     | 20  | __   |                             |
| - README lengkap          | 10  | __   | Cara run, algoritma, etc.   |
| - Blueprint & queries     | 5   | __   | Planning & reference        |
| - Screenshot              | 5   | __   | Visual proof                |
|                           |     |      |                             |
| **Algoritma (10%)**       | 10  | __   |                             |
| - Correctness             | 5   | __   | Grid binning benar          |
| - Complexity analysis     | 5   | __   | O(n + k log k) explained    |
|                           |     |      |                             |
| **Presentasi (10%)**      | 10  | __   |                             |
| - Demo lancar             | 5   | __   | No crash, clear             |
| - Q&A                     | 5   | __   | Confident answers           |
|                           |     |      |                             |
| **TOTAL**                 | 100 | __   |                             |

**Target:**
- ≥90: Excellent (A)
- 80-89: Good (B+)
- 70-79: Pass (B)

---

## 🎯 Final Checklist (Day Before Submission)

- [ ] All code files committed & pushed
- [ ] README.md complete (can run by following steps)
- [ ] Screenshot folder populated
- [ ] `npm install && npm start` tested on fresh clone
- [ ] Demo mode tested (all hours)
- [ ] Overpass mode tested (at least 3 locations)
- [ ] Presentation script ready (3 min exact)
- [ ] Q&A answers prepared
- [ ] Backup plan if internet down (demo mode)
- [ ] Sleep well 😴

**Kriteria Sukses:**
- Check semua ✅ → READY TO SUBMIT & PRESENT! 🚀

---

## 📝 Notes

**Apa yang sudah dilakukan:**
- ✅ Backend: Express server + Overpass API + caching
- ✅ Frontend: Leaflet map + dual data source + Top-5 hotspot
- ✅ Documentation: README, BLUEPRINT, QUERIES, CHECKLIST (file ini)

**Apa yang masih harus dilakukan:**
- ⬜ Screenshots (3-4 images)
- ⬜ Final testing (semua test case di atas)
- ⬜ Presentation rehearsal (2x dengan timer)

**Estimasi waktu tersisa:**
- Screenshots: 30 menit
- Testing: 1-2 jam
- Rehearsal: 1 jam
- **Total**: ~3-4 jam → bisa selesai dalam 1 hari

---

**Status**: 🟡 Almost ready (90% complete)

**Next action**: 
1. Take screenshots → save to `illustrations/`
2. Run all test cases → document any bugs
3. Rehearse presentation → refine script
4. Final commit & push → DONE!

---

**Terakhir diperbarui**: 29 Januari 2026
