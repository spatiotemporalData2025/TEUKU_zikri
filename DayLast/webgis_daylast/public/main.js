let map;
let gridLayer = L.layerGroup();
let userMarker = null; // Marker for user location

const hourSlider = document.getElementById("hourSlider");
const hourLabel  = document.getElementById("hourLabel");

const cellSlider = document.getElementById("cellSlider");
const cellLabel  = document.getElementById("cellLabel");

const top5El = document.getElementById("top5");
const statsEl = document.getElementById("stats");

const refreshBtn = document.getElementById("refreshBtn");
const fitBtn = document.getElementById("fitBtn");

// Data source controls
const dataSourceRadios = document.querySelectorAll('input[name="dataSource"]');
const overpassControls = document.getElementById("overpassControls");
const fetchPOIBtn = document.getElementById("fetchPOIBtn");
const poiStatus = document.getElementById("poiStatus");
const useMyLocationBtn = document.getElementById("useMyLocationBtn");
const locationStatus = document.getElementById("locationStatus");

let currentPoints = [];
let currentDataSource = "demo"; // "demo" or "overpass"
let center = { lat: 35.681236, lon: 139.767125 };

function fmt(n, d = 5) {
  return Number(n).toFixed(d);
}

// ============================================================================
// DATA FETCHING
// ============================================================================

async function fetchPointsByHour(hour) {
  const res = await fetch(`/api/points?hour=${hour}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Failed to fetch points");
  }
  const data = await res.json();
  currentPoints = data.points;
  return data;
}

async function fetchPOIFromOverpass() {
  const lat = document.getElementById("poiLat").value;
  const lon = document.getElementById("poiLon").value;
  const radius = document.getElementById("poiRadius").value;
  
  const categoryCheckboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
  const categories = Array.from(categoryCheckboxes).map(cb => cb.value).join(",");

  if (!categories) {
    poiStatus.textContent = "⚠️ Please select at least one category";
    return;
  }

  try {
    poiStatus.textContent = "⏳ Fetching from Overpass API...";
    fetchPOIBtn.disabled = true;

    const res = await fetch(`/api/poi?lat=${lat}&lon=${lon}&radius=${radius}&categories=${categories}`);
    
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || "Failed to fetch POI");
    }

    const data = await res.json();
    
    // Convert POI to points with synthetic hour distribution
    currentPoints = data.poi.map((poi, idx) => {
      // Synthetic hour distribution (weighted by typical activity patterns)
      // Peaks at 8-10 and 17-20
      const rand = (idx * 7919) % 100;
      let hour;
      if (rand < 15) hour = 8 + (rand % 3);       // 15% at 8-10
      else if (rand < 30) hour = 17 + (rand % 4); // 15% at 17-20
      else if (rand < 50) hour = 11 + (rand % 6); // 20% at 11-16
      else hour = rand % 24;                       // rest distributed

      return {
        id: poi.id,
        lat: poi.lat,
        lon: poi.lon,
        hour: hour,
        category: poi.category,
        name: poi.name
      };
    });

    center = data.center;
    map.setView([center.lat, center.lon], 13);

    poiStatus.textContent = `✓ Loaded ${data.count} POI (${data.cached ? 'cached' : 'fresh'})`;
    
    renderGrid();
    fitToData();

  } catch (error) {
    poiStatus.textContent = `❌ Error: ${error.message}`;
    console.error(error);
  } finally {
    fetchPOIBtn.disabled = false;
  }
}

// ============================================================================
// GEOLOCATION (Use My Location)
// ============================================================================

function useMyLocation() {
  if (!navigator.geolocation) {
    locationStatus.textContent = "❌ Geolocation not supported by browser";
    return;
  }

  locationStatus.textContent = "📡 Getting your location...";
  useMyLocationBtn.disabled = true;

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const accuracy = position.coords.accuracy;

      // Update input fields
      document.getElementById("poiLat").value = lat.toFixed(6);
      document.getElementById("poiLon").value = lon.toFixed(6);

      // Update map view
      map.setView([lat, lon], 14);

      // Add or update user marker
      if (userMarker) {
        userMarker.setLatLng([lat, lon]);
      } else {
        userMarker = L.marker([lat, lon], {
          icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
          })
        }).addTo(map);
        
        userMarker.bindPopup(`<b>Your Location</b><br>Accuracy: ±${Math.round(accuracy)}m`).openPopup();
      }

      locationStatus.textContent = `✓ Location found (±${Math.round(accuracy)}m)`;
      useMyLocationBtn.disabled = false;
    },
    (error) => {
      let message = "❌ ";
      switch (error.code) {
        case error.PERMISSION_DENIED:
          message += "Location permission denied. Please enable location access.";
          break;
        case error.POSITION_UNAVAILABLE:
          message += "Location unavailable. Try again.";
          break;
        case error.TIMEOUT:
          message += "Location request timeout. Try again.";
          break;
        default:
          message += "Unknown error: " + error.message;
      }
      locationStatus.textContent = message;
      useMyLocationBtn.disabled = false;
      console.error("Geolocation error:", error);
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  );
}

// ============================================================================
// MAP INITIALIZATION
// ============================================================================

function initMap() {
  map = L.map("map", { preferCanvas: true }).setView([center.lat, center.lon], 13);

  // OSM tile (gratis)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  gridLayer.addTo(map);

  // Re-render grid when user moves/zooms
  map.on("moveend zoomend", () => renderGrid());

  // Click to set location for POI fetch
  map.on("click", (e) => {
    if (currentDataSource === "overpass") {
      document.getElementById("poiLat").value = e.latlng.lat.toFixed(6);
      document.getElementById("poiLon").value = e.latlng.lng.toFixed(6);
      poiStatus.textContent = `📍 Location updated. Click "Fetch POI" to load data.`;
    }
  });
}

// ============================================================================
// GRID RENDERING & ACTIVITY DENSITY
// ============================================================================

function getCellSize() {
  return Number(cellSlider.value);
}

function renderGrid() {
  if (!map) return;

  const hour = Number(hourSlider.value);
  const bounds = map.getBounds();
  const latMin = bounds.getSouth();
  const latMax = bounds.getNorth();
  const lonMin = bounds.getWest();
  const lonMax = bounds.getEast();

  const cell = getCellSize();

  // Filter points by current hour
  const filteredPoints = currentPoints.filter(p => p.hour === hour);

  // Calculate count per cell
  const counts = new Map();

  let inView = 0;

  for (const p of filteredPoints) {
    if (p.lat < latMin || p.lat > latMax || p.lon < lonMin || p.lon > lonMax) continue;
    inView++;

    const i = Math.floor((p.lat - latMin) / cell);
    const j = Math.floor((p.lon - lonMin) / cell);
    const key = `${i},${j}`;
    counts.set(key, (counts.get(key) || 0) + 1);
  }

  // Find max for opacity normalization
  let maxCount = 0;
  for (const v of counts.values()) maxCount = Math.max(maxCount, v);

  // Clear old layer
  gridLayer.clearLayers();

  // Render rectangles per cell
  for (const [key, c] of counts.entries()) {
    const [iStr, jStr] = key.split(",");
    const i = Number(iStr);
    const j = Number(jStr);

    const south = latMin + i * cell;
    const north = south + cell;
    const west  = lonMin + j * cell;
    const east  = west + cell;

    const opacity = maxCount > 0 ? (0.10 + 0.70 * (c / maxCount)) : 0.2;

    // Color based on intensity (heatmap-like)
    let color = "#3388ff"; // blue
    if (c / maxCount > 0.7) color = "#ff4444"; // red (hot)
    else if (c / maxCount > 0.4) color = "#ff9944"; // orange (warm)
    else if (c / maxCount > 0.2) color = "#ffdd44"; // yellow (medium)

    const rect = L.rectangle([[south, west], [north, east]], {
      weight: 1,
      color: color,
      fill: true,
      fillColor: color,
      fillOpacity: opacity
    });

    rect.bindTooltip(`count: ${c}`, { sticky: true });
    rect.addTo(gridLayer);
  }

  updateTop5(counts, latMin, lonMin, cell);

  statsEl.textContent =
    `hour=${hour}, total=${currentPoints.length}, filtered=${filteredPoints.length}, inView=${inView}, cells=${counts.size}, max=${maxCount}`;
}

// ============================================================================
// TOP-5 HOTSPOT
// ============================================================================

function updateTop5(counts, latMin, lonMin, cell) {
  const arr = Array.from(counts.entries())
    .map(([key, c]) => {
      const [iStr, jStr] = key.split(",");
      const i = Number(iStr);
      const j = Number(jStr);
      const latC = latMin + (i + 0.5) * cell;
      const lonC = lonMin + (j + 0.5) * cell;
      return { key, c, latC, lonC };
    })
    .sort((a, b) => b.c - a.c)
    .slice(0, 5);

  top5El.innerHTML = "";
  
  if (arr.length === 0) {
    top5El.innerHTML = "<li class='muted'>No data in current view</li>";
    return;
  }

  for (const h of arr) {
    const li = document.createElement("li");
    li.innerHTML = `
      <button style="width:100%; text-align:left;">
        <strong>${h.c}</strong> activities @ (${fmt(h.latC, 5)}, ${fmt(h.lonC, 5)})
      </button>
    `;

    li.querySelector("button").addEventListener("click", () => {
      map.setView([h.latC, h.lonC], Math.max(map.getZoom(), 15));
    });

    top5El.appendChild(li);
  }
}

// ============================================================================
// UI EVENT HANDLERS
// ============================================================================

async function setHour(hour) {
  hourLabel.textContent = String(hour);

  if (currentDataSource === "demo") {
    const data = await fetchPointsByHour(hour);
    center = data.center || center;
  }

  renderGrid();
}

function fitToData() {
  if (!currentPoints.length) return;

  const latLngs = currentPoints.map(p => [p.lat, p.lon]);
  const b = L.latLngBounds(latLngs);
  map.fitBounds(b.pad(0.2));
}

function bindUI() {
  // Hour slider
  hourSlider.addEventListener("input", async (e) => {
    const hour = Number(e.target.value);
    await setHour(hour);
  });

  // Cell size slider
  cellSlider.addEventListener("input", () => {
    cellLabel.textContent = Number(cellSlider.value).toFixed(3);
    renderGrid();
  });

  // Buttons
  refreshBtn.addEventListener("click", () => renderGrid());
  fitBtn.addEventListener("click", () => fitToData());

  // Data source toggle
  dataSourceRadios.forEach(radio => {
    radio.addEventListener("change", (e) => {
      currentDataSource = e.target.value;
      overpassControls.style.display = currentDataSource === "overpass" ? "block" : "none";
      
      if (currentDataSource === "demo") {
        poiStatus.textContent = "";
      }
    });
  });

  // Fetch POI button
  fetchPOIBtn.addEventListener("click", () => {
    fetchPOIFromOverpass();
  });

  // Use My Location button
  useMyLocationBtn.addEventListener("click", () => {
    useMyLocation();
  });

  // Init labels
  hourLabel.textContent = hourSlider.value;
  cellLabel.textContent = Number(cellSlider.value).toFixed(3);
}

// ============================================================================
// MAIN INITIALIZATION
// ============================================================================

(async function main() {
  bindUI();

  // Load initial hour (demo data)
  const initHour = Number(hourSlider.value);
  await setHour(initHour);

  initMap();
  fitToData();
  renderGrid();
})().catch(err => {
  alert(err.message || String(err));
  console.error(err);
});
