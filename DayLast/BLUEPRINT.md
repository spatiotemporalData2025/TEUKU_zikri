# Blueprint 3 Minggu - Urban Activity Pulse Map

**Tujuan**: Menyelesaikan aplikasi Web GIS spatio-temporal dari 0 hingga presentasi dalam 3 minggu.

**Prinsip**: Incremental development, test early, document as you go.

---

## 🗓️ Minggu 1: Foundation & Core Features

### Target
✅ Setup project structure  
✅ Implement backend basic (Express server)  
✅ Implement frontend basic (Leaflet map + OSM tiles)  
✅ Demo data generation (deterministic)  
✅ Basic grid algorithm (no styling yet)  

### Day 1-2: Setup & Backend
- [x] Init project: `npm init`, install `express`
- [x] Create `server.js` dengan demo data generator (3000 points)
- [x] Endpoint `/api/points?hour=X` untuk filter by hour
- [x] Test: `curl http://localhost:8000/api/points?hour=12`

### Day 3-4: Frontend Basic
- [x] HTML structure: sidebar + map container
- [x] Leaflet integration: `L.map()`, OSM tiles
- [x] Fetch demo points dari backend
- [x] Display points as markers (basic)
- [x] Test: Buka browser, peta muncul dengan data

### Day 5-6: Grid Algorithm V1
- [x] Implement `renderGrid()`: binning lat/lon to grid cells
- [x] Count points per cell
- [x] Render rectangles dengan `L.rectangle()`
- [x] Opacity based on count (normalisasi)
- [x] Test: Grid muncul, adjust cell size manual di code

### Day 7: Polish & Test
- [x] Hour slider + label update
- [x] Cell size slider
- [x] Refresh button
- [x] Test semua fitur, fix bugs

**Deliverable Minggu 1**: Working demo dengan offline data, grid basic.

---

## 🗓️ Minggu 2: Overpass API & Advanced Features

### Target
✅ Integrate Overpass API  
✅ Caching & error handling  
✅ Top-5 hotspot feature  
✅ Dual data source (demo vs real POI)  
✅ Click-to-set location  

### Day 8-9: Overpass Integration
- [x] Install `axios`: `npm install axios`
- [x] Create endpoint `/api/poi` dengan Overpass query
- [x] Test query: convenience stores di Tokyo Station
- [x] Parse Overpass JSON response → array of POI
- [x] Test: `curl localhost:8000/api/poi?lat=35.681&lon=139.767&radius=3000&categories=convenience`

### Day 10-11: Caching & Error Handling
- [x] Implement in-memory cache (Map) dengan TTL 1 hour
- [x] Cache key: `"${lat},${lon},${radius},${categories}"`
- [x] Error handling: timeout, invalid response, rate limit
- [x] Status feedback di UI
- [x] Test: Fetch 2x, second call should be cached

### Day 12-13: UI Upgrade
- [x] Toggle radio: Demo vs Real POI
- [x] Show/hide Overpass controls based on toggle
- [x] Input fields: lat, lon, radius
- [x] Checkbox group: categories (convenience, cafe, restaurant, station)
- [x] Button: "Fetch POI from Overpass"
- [x] Status text: loading, success, error
- [x] Click map → set lat/lon automatically

### Day 14: Top-5 Hotspot
- [x] Sort cells by count descending
- [x] Take top 5
- [x] Render as ordered list
- [x] Click item → `map.setView()` to center
- [x] Test: Klik top-5, peta zoom ke lokasi

**Deliverable Minggu 2**: Full Overpass integration, dual data source, Top-5 feature.

---

## 🗓️ Minggu 3: Documentation, Testing & Presentation

### Target
✅ Comprehensive documentation (README, BLUEPRINT, QUERIES, CHECKLIST)  
✅ Screenshot & diagram  
✅ Final testing (demo + overpass mode)  
✅ Presentation slides/script  
✅ Rehearsal & refinement  

### Day 15-16: Documentation
- [ ] Write README.md:
  - Deskripsi sistem
  - Arsitektur diagram (ASCII atau PNG)
  - Cara menjalankan (step-by-step)
  - Algoritma grid (pseudocode + kompleksitas)
  - Overpass query examples
  - Screenshot placeholder
  - Troubleshooting section
- [ ] Write BLUEPRINT.md (file ini)
- [ ] Write OVERPASS_QUERIES.md (detail query + parameters)
- [ ] Write DELIVERABLES_CHECKLIST.md (penilaian checklist)

### Day 17: Screenshot & Illustration
- [ ] Screenshot demo mode:
  - Peta dengan grid (berbagai jam)
  - Top-5 hotspot
  - Cell size adjustment
- [ ] Screenshot Overpass mode:
  - UI controls (input fields, checkboxes)
  - Fetch POI (loading state)
  - Result (POI loaded, grid updated)
- [ ] Architecture diagram (draw.io, Excalidraw, atau ASCII art)
- [ ] Optional: animated GIF demo (ScreenToGif, Peek)

### Day 18: Final Testing
- [ ] Test demo mode:
  - Semua jam (0–23) → grid berubah
  - Cell size min/max → no crash
  - Top-5 klik → zoom benar
  - Zoom/pan → grid recalculate
- [ ] Test Overpass mode:
  - Tokyo (35.681, 139.767) → should work
  - New York (40.748, -73.986) → should work
  - London (51.509, -0.126) → should work
  - Jakarta (-6.200, 106.816) → should work
  - Error case: invalid lat/lon → handle gracefully
  - Error case: radius too large (50000m) → timeout expected
  - Cache test: fetch 2x same location → second cached
- [ ] Test edge cases:
  - No POI in radius → "No data in current view"
  - Hour dengan 0 points → empty grid
  - Very small cell size → banyak cells, performance?
  - Very large cell size → 1-2 cells only

### Day 19: Presentation Prep
- [ ] Write presentation script (3 menit):
  - 1 menit: intro + demo data mode
  - 1 menit: Overpass mode + fetch POI
  - 1 menit: algoritma + Q&A prep
- [ ] Practice demo:
  - Timing: 3 menit exact
  - Flow smooth (no stuttering)
  - Backup plan jika Overpass down (use demo mode)
- [ ] Prepare Q&A answers:
  - Kenapa pilih Overpass?
  - Bagaimana handle opening hours?
  - Kompleksitas algoritma?
  - Bisa deploy ke cloud?
  - Data accuracy?

### Day 20: Rehearsal & Buffer
- [ ] Full rehearsal dengan timer
- [ ] Feedback dari teman/dosen (optional)
- [ ] Fix last-minute bugs
- [ ] Backup slides (PDF) jika diminta
- [ ] Print README (optional, jika presentasi hybrid)

### Day 21: Presentasi & Submission
- [ ] Submit repo link (atau ZIP) sesuai deadline
- [ ] Presentasi di kelas (3 menit demo + Q&A)
- [ ] Celebrate! 🎉

**Deliverable Minggu 3**: Complete project + documentation + presentation.

---

## 🎯 Milestone Checkpoints

### Checkpoint 1 (End of Week 1)
**Demo to yourself:**
- Buka browser → peta muncul
- Slider jam → grid berubah
- Cell size slider → grid resolution berubah
- No errors di console

**Pass criteria**: ✅ All above works with demo data.

### Checkpoint 2 (End of Week 2)
**Demo to friend:**
- Toggle Demo → Real POI
- Input Tokyo coordinates → Fetch POI
- POI muncul → grid updated
- Top-5 hotspot → klik zoom

**Pass criteria**: ✅ Overpass integration works, no crashes.

### Checkpoint 3 (End of Week 3)
**Final readiness:**
- README complete (copy-paste run steps → works)
- Screenshot in `illustrations/`
- Presentation script rehearsed (3 min exact)
- Backup plan (if Overpass down → use demo)

**Pass criteria**: ✅ Ready to submit & present.

---

## ⚠️ Risk Mitigation

### Risk 1: Overpass API Down/Slow
**Mitigation**: 
- Use demo mode as fallback
- Implement caching (already done)
- Test backup Overpass endpoints:
  - `https://overpass.kumi.systems/api/interpreter`
  - `https://overpass.osm.ch/api/interpreter`

### Risk 2: Kompleksitas Grid Terlalu Tinggi
**Mitigation**:
- Limit cell count (max 1000 cells)
- Use `preferCanvas` di Leaflet (faster rendering)
- Debounce re-render (wait 100ms after zoom/pan)

### Risk 3: Presentasi Melebihi 3 Menit
**Mitigation**:
- Rehearse dengan timer
- Skip detail teknis jika over time
- Prepare "elevator pitch" (1 menit version)

### Risk 4: Data POI Tidak Ada di Lokasi Tertentu
**Mitigation**:
- Provide "recommended locations" di UI (Tokyo, NYC, London)
- Show error message gracefully: "No POI found, try larger radius"
- Demo mode always works (offline)

---

## 📊 Time Allocation

| Week | Backend | Frontend | Documentation | Testing | Presentation |
|------|---------|----------|---------------|---------|--------------|
| 1    | 40%     | 40%      | 10%           | 10%     | 0%           |
| 2    | 30%     | 40%      | 10%           | 20%     | 0%           |
| 3    | 5%      | 10%      | 40%           | 25%     | 20%          |

**Total**: ~60 hours (3 minggu × 20 jam/minggu)

---

## 🏆 Success Criteria

**Minimum (Pass)**:
- [x] Aplikasi bisa dijalankan di localhost
- [x] Peta muncul dengan grid density
- [x] Slider waktu mengubah visualisasi
- [x] Ada algoritma spatio-temporal yang jelas
- [x] README dengan cara run yang jelas

**Target (Good)**:
- [x] Overpass API integration (real data)
- [x] Caching & error handling
- [x] Top-5 hotspot feature
- [x] Comprehensive documentation
- [x] Screenshot & diagram

**Stretch (Excellent)**:
- [x] Dual data source (demo + real)
- [x] Click-to-set location
- [x] Multiple POI categories
- [x] Professional UI/UX
- [ ] Animated demo GIF (optional)

---

**Status Saat Ini**: ✅ Week 3, Day 15 - Documentation in progress

**Next Action**: 
1. Finish README.md → DONE ✅
2. Create OVERPASS_QUERIES.md
3. Create DELIVERABLES_CHECKLIST.md
4. Take screenshots
5. Final testing
