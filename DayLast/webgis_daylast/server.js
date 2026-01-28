import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import axios from "axios";

const app = express();
const PORT = process.env.PORT || 8000;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Serve static files
app.use(express.static(path.join(__dirname, "public")));

/**
 * Demo dataset generator:
 * - Generates points (lat, lon, hour) deterministically (seeded)
 * - Points scattered around center (default: Tokyo Station)
 * - Safe for offline demo (without Overpass / paid APIs)
 */

const CENTER = {
  lat: 35.681236,  // Tokyo Station
  lon: 139.767125
};

const TOTAL_POINTS = 3000;

// Simple deterministic RNG (LCG)
function makeLCG(seed = 123456789) {
  let s = seed >>> 0;
  return function rand() {
    s = (1664525 * s + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

const rand = makeLCG(20260130);

const ALL_POINTS = Array.from({ length: TOTAL_POINTS }, (_, i) => {
  // hour 0..23
  const hour = Math.floor(rand() * 24);

  // Simple gaussian-ish distribution (using sum-uniform)
  const r1 = (rand() + rand() + rand() + rand()) / 4; // ~0..1
  const r2 = (rand() + rand() + rand() + rand()) / 4;

  // Degree radius roughly (0.01 ~ 1km-ish), tweak according to zoom
  const spreadLat = 0.06;  // ~6-7km
  const spreadLon = 0.08;  // ~7-9km (depends on latitude)

  // Create clusters to make hotspots visible
  const clusterBias = (hour >= 8 && hour <= 10) || (hour >= 17 && hour <= 20) ? 1.6 : 1.0;

  const lat = CENTER.lat + (r1 - 0.5) * spreadLat * clusterBias;
  const lon = CENTER.lon + (r2 - 0.5) * spreadLon * clusterBias;

  return { id: i, lat, lon, hour };
});

// API: get points per hour (or all) - DEMO DATA
app.get("/api/points", (req, res) => {
  const hourParam = req.query.hour;
  if (hourParam === undefined) {
    return res.json({ center: CENTER, points: ALL_POINTS });
  }
  const hour = Number(hourParam);
  if (!Number.isInteger(hour) || hour < 0 || hour > 23) {
    return res.status(400).json({ error: "hour must be integer 0..23" });
  }
  const filtered = ALL_POINTS.filter(p => p.hour === hour);
  return res.json({ center: CENTER, points: filtered });
});

// ============================================================================
// OVERPASS API INTEGRATION (Real POI Data)
// ============================================================================

const OVERPASS_URL = "https://overpass-api.de/api/interpreter";
const cache = new Map(); // In-memory cache
const CACHE_TTL = 3600000; // 1 hour

/**
 * Fetch POI from Overpass API with specific categories
 * Categories: convenience, cafe, restaurant, station
 */
app.get("/api/poi", async (req, res) => {
  try {
    const { lat, lon, radius = 3000, categories = "convenience,cafe" } = req.query;

    if (!lat || !lon) {
      return res.status(400).json({ 
        error: "Parameters required: lat, lon",
        example: "/api/poi?lat=35.681&lon=139.767&radius=3000&categories=convenience,cafe"
      });
    }

    const cacheKey = `${lat},${lon},${radius},${categories}`;
    const cached = cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      console.log(`✓ Cache hit: ${cacheKey}`);
      return res.json({ ...cached.data, cached: true });
    }

    // Build Overpass QL query
    const cats = categories.split(",").map(c => c.trim());
    const queries = [];

    for (const cat of cats) {
      if (cat === "convenience") {
        queries.push(`node["amenity"="convenience"](around:${radius},${lat},${lon});`);
      } else if (cat === "cafe") {
        queries.push(`node["amenity"="cafe"](around:${radius},${lat},${lon});`);
      } else if (cat === "restaurant") {
        queries.push(`node["amenity"="restaurant"](around:${radius},${lat},${lon});`);
      } else if (cat === "station") {
        queries.push(`node["railway"="station"](around:${radius},${lat},${lon});`);
        queries.push(`node["public_transport"="station"](around:${radius},${lat},${lon});`);
      }
    }

    const overpassQuery = `
      [out:json][timeout:25];
      (
        ${queries.join("\n        ")}
      );
      out body;
    `;

    console.log(`→ Fetching Overpass: ${lat},${lon} r=${radius} cats=${categories}`);

    const response = await axios.post(OVERPASS_URL, overpassQuery, {
      headers: { "Content-Type": "text/plain" },
      timeout: 30000
    });

    const elements = response.data.elements || [];
    const poi = elements.map((el, idx) => ({
      id: el.id || idx,
      lat: el.lat,
      lon: el.lon,
      category: el.tags?.amenity || el.tags?.railway || el.tags?.public_transport || "unknown",
      name: el.tags?.name || "(unnamed)",
      opening_hours: el.tags?.opening_hours || null
    }));

    const result = {
      center: { lat: parseFloat(lat), lon: parseFloat(lon) },
      radius: parseInt(radius),
      categories: cats,
      count: poi.length,
      poi
    };

    // Cache result
    cache.set(cacheKey, { data: result, timestamp: Date.now() });
    console.log(`✓ Fetched ${poi.length} POI, cached.`);

    res.json(result);

  } catch (error) {
    console.error("Overpass API error:", error.message);
    res.status(500).json({ 
      error: "Failed to fetch POI from Overpass",
      message: error.message,
      hint: "Try smaller radius or check Overpass API status"
    });
  }
});

/**
 * Compute activity density grid + Top-5 hotspots
 * Input: array of points, viewport bounds, cell size
 */
app.post("/api/grid", express.json(), (req, res) => {
  try {
    const { points = [], bounds, cellSize = 0.01, hour } = req.body;

    if (!bounds || !bounds.latMin || !bounds.latMax || !bounds.lonMin || !bounds.lonMax) {
      return res.status(400).json({ error: "bounds required: latMin, latMax, lonMin, lonMax" });
    }

    const { latMin, latMax, lonMin, lonMax } = bounds;
    const cell = parseFloat(cellSize);

    // Filter points by hour if specified
    let filteredPoints = points;
    if (hour !== undefined && hour !== null) {
      filteredPoints = points.filter(p => p.hour === parseInt(hour));
    }

    // Count per grid cell
    const counts = {};
    for (const p of filteredPoints) {
      if (p.lat < latMin || p.lat > latMax || p.lon < lonMin || p.lon > lonMax) continue;

      const i = Math.floor((p.lat - latMin) / cell);
      const j = Math.floor((p.lon - lonMin) / cell);
      const key = `${i},${j}`;
      counts[key] = (counts[key] || 0) + 1;
    }

    // Build grid cells array
    const cells = Object.entries(counts).map(([key, count]) => {
      const [i, j] = key.split(",").map(Number);
      const south = latMin + i * cell;
      const north = south + cell;
      const west = lonMin + j * cell;
      const east = west + cell;
      const centerLat = (south + north) / 2;
      const centerLon = (west + east) / 2;

      return { key, count, bounds: { south, north, west, east }, center: { lat: centerLat, lon: centerLon } };
    });

    // Sort by count descending
    cells.sort((a, b) => b.count - a.count);

    const maxCount = cells[0]?.count || 0;
    const top5 = cells.slice(0, 5);

    res.json({
      totalPoints: filteredPoints.length,
      totalCells: cells.length,
      maxCount,
      top5,
      cells
    });

  } catch (error) {
    console.error("/api/grid error:", error.message);
    res.status(500).json({ error: "Failed to compute grid", message: error.message });
  }
});

// Health check
app.get("/api/health", (_req, res) => {
  res.json({ ok: true, port: PORT });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
  console.log(`   (WSL) Open from Windows browser: http://localhost:${PORT}`);
});
