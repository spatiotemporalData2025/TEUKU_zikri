let map;
let gridLayer = L.layerGroup();
let userMarker = null; // Marker for user location

const hourStart = document.getElementById("hourStart");
const hourEnd = document.getElementById("hourEnd");
const hourLabel  = document.getElementById("hourLabel");

const epsSlider = document.getElementById("epsSlider");
const epsLabel  = document.getElementById("epsLabel");

const minPtsSlider = document.getElementById("minPtsSlider");
const minPtsLabel  = document.getElementById("minPtsLabel");

const hotspotSlider = document.getElementById("hotspotSlider");
const hotspotLabel = document.getElementById("hotspotLabel");

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
let currentDataSource = "overpass"; // "overpass" only
let center = { lat: 35.681236, lon: 139.767125 };
const openingHoursCache = new Map();

function fmt(n, d = 5) {
  return Number(n).toFixed(d);
}


// ============================================================================
// DATA FETCHING
// ============================================================================


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
    
    // Convert POI to points (keep opening_hours for temporal filtering)
    currentPoints = data.poi.map((poi) => {
      return {
        id: poi.id,
        lat: poi.lat,
        lon: poi.lon,
        hour: null,
        category: poi.category,
        name: poi.name,
        opening_hours: poi.opening_hours || null
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

function getEpsilon() {
  return Number(epsSlider.value);
}

function getMinPts() {
  return Number(minPtsSlider.value);
}

function dbscan(points, eps, minPts) {
  const n = points.length;
  const labels = new Array(n).fill(0); // 0 = unvisited, -1 = noise, >0 = cluster id
  let clusterId = 0;

  const neighborsCache = new Map();

  function regionQuery(i) {
    if (neighborsCache.has(i)) return neighborsCache.get(i);
    const neighbors = [];
    const p = points[i].__proj;
    for (let j = 0; j < n; j++) {
      const q = points[j].__proj;
      const dx = p.x - q.x;
      const dy = p.y - q.y;
      if (dx * dx + dy * dy <= eps * eps) neighbors.push(j);
    }
    neighborsCache.set(i, neighbors);
    return neighbors;
  }

  for (let i = 0; i < n; i++) {
    if (labels[i] !== 0) continue;
    const neighbors = regionQuery(i);
    if (neighbors.length < minPts) {
      labels[i] = -1;
      continue;
    }

    clusterId++;
    labels[i] = clusterId;

    const seeds = neighbors.slice();
    for (let k = 0; k < seeds.length; k++) {
      const j = seeds[k];
      if (labels[j] === -1) labels[j] = clusterId;
      if (labels[j] !== 0) continue;
      labels[j] = clusterId;
      const n2 = regionQuery(j);
      if (n2.length >= minPts) {
        seeds.push(...n2);
      }
    }
  }

  const clusters = new Map();
  const noise = [];
  for (let i = 0; i < n; i++) {
    const label = labels[i];
    if (label === -1) {
      noise.push(points[i]);
    } else if (label > 0) {
      if (!clusters.has(label)) clusters.set(label, []);
      clusters.get(label).push(points[i]);
    }
  }

  return { clusters: Array.from(clusters.values()), noise };
}

function convexHull(points) {
  if (points.length < 3) return points.slice();

  const pts = points
    .map(p => ({ lat: p.lat, lon: p.lon }))
    .sort((a, b) => (a.lon === b.lon ? a.lat - b.lat : a.lon - b.lon));

  const cross = (o, a, b) => (a.lon - o.lon) * (b.lat - o.lat) - (a.lat - o.lat) * (b.lon - o.lon);

  const lower = [];
  for (const p of pts) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
      lower.pop();
    }
    lower.push(p);
  }

  const upper = [];
  for (let i = pts.length - 1; i >= 0; i--) {
    const p = pts[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
      upper.pop();
    }
    upper.push(p);
  }

  upper.pop();
  lower.pop();
  return lower.concat(upper);
}

function renderGrid() {
  if (!map) return;

  const startHour = Number(hourStart.value);
  const endHour = Number(hourEnd.value);
  const bounds = map.getBounds();
  const eps = getEpsilon();
  const minPts = getMinPts();

  // Filter points by hour range (use full dataset for stable clustering)
  const filteredPoints = currentPoints.filter(p => isPointActiveInRange(p, startHour, endHour));

  // Project points once for DBSCAN
  const points = filteredPoints.map(p => ({
    ...p,
    __proj: L.CRS.EPSG3857.project(L.latLng(p.lat, p.lon))
  }));

  const { clusters, noise } = dbscan(points, eps, minPts);

  // Clear old layer
  gridLayer.clearLayers();

  // Cluster rendering (convex hull only)
  let maxSize = 0;
  for (const c of clusters) maxSize = Math.max(maxSize, c.length);

  for (const c of clusters) {
    if (c.length < 3) continue;

    const ratio = maxSize > 0 ? c.length / maxSize : 0;
    let color = "#3388ff";
    if (ratio > 0.7) color = "#ff4444";
    else if (ratio > 0.4) color = "#ff9944";
    else if (ratio > 0.2) color = "#ffdd44";

    const hull = convexHull(c).map(p => [p.lat, p.lon]);
    const polygon = L.polygon(hull, {
      color,
      fillColor: color,
      fillOpacity: 0.18,
      weight: 2
    });
    polygon.bindTooltip(`convex hull size: ${c.length}`, { sticky: true });
    polygon.addTo(gridLayer);
  }

  // Noise points (optional small dots)
  for (const p of noise) {
    if (!bounds.contains([p.lat, p.lon])) continue;
    const dot = L.circleMarker([p.lat, p.lon], {
      radius: 2,
      color: "#999",
      weight: 1,
      opacity: 0.8,
      fillOpacity: 0.4
    });
    dot.addTo(gridLayer);
  }

  updateTopHotspots(clusters);

  statsEl.textContent =
    `hour=${startHour}-${endHour}, total=${currentPoints.length}, filtered=${filteredPoints.length}, clusters=${clusters.length}, noise=${noise.length}`;
}

// ============================================================================
// TOP-5 HOTSPOT
// ============================================================================

function getHotspotCount() {
  return Number(hotspotSlider?.value || 5);
}

function parseOpeningHours(value) {
  if (!value || typeof window.opening_hours !== "function") return null;
  if (openingHoursCache.has(value)) return openingHoursCache.get(value);
  try {
    const oh = new window.opening_hours(value);
    openingHoursCache.set(value, oh);
    return oh;
  } catch {
    openingHoursCache.set(value, null);
    return null;
  }
}

function isPointActiveInRange(point, startHour, endHour) {
  const oh = parseOpeningHours(point.opening_hours);
  if (!oh) {
    // If no opening_hours available, include by default
    return true;
  }

  const now = new Date();
  for (let h = startHour; h <= endHour; h++) {
    const d = new Date(now);
    d.setHours(h, 0, 0, 0);
    if (oh.getState(d)) return true;
  }
  return false;
}

function updateTopHotspots(clusters) {
  const limit = getHotspotCount();
  const arr = clusters
    .map((c, idx) => {
      const latC = c.reduce((s, p) => s + p.lat, 0) / c.length;
      const lonC = c.reduce((s, p) => s + p.lon, 0) / c.length;
      return { key: idx, c: c.length, latC, lonC };
    })
    .sort((a, b) => b.c - a.c)
    .slice(0, limit);

  top5El.innerHTML = "";
  
  if (arr.length === 0) {
    top5El.innerHTML = "<li class='muted'>No data in current view</li>";
    return;
  }

  for (const h of arr) {
    const li = document.createElement("li");
    li.innerHTML = `
      <button style="width:100%; text-align:left;">
        <strong>${h.c}</strong> points @ (${fmt(h.latC, 5)}, ${fmt(h.lonC, 5)})
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

async function setHourRange() {
  const startHour = Number(hourStart.value);
  const endHour = Number(hourEnd.value);
  hourLabel.textContent = `${startHour}–${endHour}`;

  renderGrid();
}

function fitToData() {
  if (!currentPoints.length) return;

  const latLngs = currentPoints.map(p => [p.lat, p.lon]);
  const b = L.latLngBounds(latLngs);
  map.fitBounds(b.pad(0.2));
}

function bindUI() {
  // Ensure Overpass controls visible
  overpassControls.style.display = "block";

  // Hour range sliders
  hourStart.addEventListener("input", async () => {
    if (Number(hourStart.value) > Number(hourEnd.value)) {
      hourEnd.value = hourStart.value;
    }
    await setHourRange();
  });

  hourEnd.addEventListener("input", async () => {
    if (Number(hourEnd.value) < Number(hourStart.value)) {
      hourStart.value = hourEnd.value;
    }
    await setHourRange();
  });

  // Cell size slider
  epsSlider.addEventListener("input", () => {
    epsLabel.textContent = epsSlider.value;
    renderGrid();
  });

  minPtsSlider.addEventListener("input", () => {
    minPtsLabel.textContent = minPtsSlider.value;
    renderGrid();
  });

  // Hotspot count slider
  hotspotSlider.addEventListener("input", () => {
    hotspotLabel.textContent = hotspotSlider.value;
    renderGrid();
  });

  // Buttons
  refreshBtn.addEventListener("click", () => renderGrid());
  fitBtn.addEventListener("click", () => fitToData());

  // Data source toggle (overpass only)
  dataSourceRadios.forEach(radio => {
    radio.addEventListener("change", (e) => {
      currentDataSource = e.target.value;
      overpassControls.style.display = "block";
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
  hourLabel.textContent = `${hourStart.value}–${hourEnd.value}`;
  epsLabel.textContent = epsSlider.value;
  minPtsLabel.textContent = minPtsSlider.value;
  hotspotLabel.textContent = hotspotSlider.value;
}

// ============================================================================
// MAIN INITIALIZATION
// ============================================================================

(async function main() {
  bindUI();

  // Load initial hour
  await setHourRange();

  initMap();
  fitToData();
  renderGrid();
})().catch(err => {
  alert(err.message || String(err));
  console.error(err);
});
