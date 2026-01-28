# Placeholder for Screenshots

## How to Take Screenshots

### 1. screenshot-demo.png
**Capture:**
- Demo Data mode selected
- Hour slider at 8 or 18 (peak hour)
- Grid visible on map
- Top-5 list populated
- Stats showing

**Tools:** 
- Windows: Snipping Tool, Win+Shift+S
- Linux: Flameshot, gnome-screenshot
- Mac: Cmd+Shift+4

**Size:** ~1920x1080 or browser window

---

### 2. screenshot-overpass.png
**Capture:**
- Real POI mode selected
- Overpass controls visible (lat/lon inputs, checkboxes)
- POI status showing success message
- Grid updated with real data
- Different color/density than demo

**Same tools as above**

---

### 3. architecture-diagram.png
**Create:**
Use draw.io, Excalidraw, or ASCII art

**Elements:**
```
┌────────────┐
│  Browser   │
│ (Leaflet)  │
└─────┬──────┘
      │ HTTP/JSON
┌─────▼──────┐
│  Express   │
│  Server    │
│  (Cache)   │
└─────┬──────┘
      │ Overpass QL
┌─────▼──────┐
│ Overpass   │
│    API     │
└────────────┘
```

**Tools:**
- draw.io (diagrams.net)
- Excalidraw
- Figma
- Or just use ASCII in README

---

### 4. demo-flow.gif (optional)
**Record:**
- Open browser
- Slide hour slider 0 → 23
- Watch grid change color/density
- Click Top-5 item
- Zoom to location

**Tools:**
- Windows: ScreenToGif
- Linux: Peek
- Mac: Kap

**Duration:** 5-10 seconds
**Size:** Keep under 5MB

---

## After Taking Screenshots

Save files here:
```
illustrations/
├── screenshot-demo.png
├── screenshot-overpass.png
├── architecture-diagram.png
└── demo-flow.gif (optional)
```

Then update README.md to reference these images:
```markdown
![Demo Mode](illustrations/screenshot-demo.png)
![Overpass Mode](illustrations/screenshot-overpass.png)
```
