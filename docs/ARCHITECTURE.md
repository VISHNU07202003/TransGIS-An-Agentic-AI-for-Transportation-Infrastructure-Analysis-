# System Architecture

## 1. Architectural Overview

The Agentic AI System for Transportation Infrastructure Analysis is structured around a strict separation of concerns:

> **The LLM interprets and orchestrates. GIS/database tools calculate and retrieve. FDOT/Gainesville provide the authoritative facts.**

```text
                         USER
                           |
              +------------+------------+
              |                         |
        Address Input               Map Click
              |                         |
              +------------+------------+
                           v
                    Frontend / Map UI (React + MapLibre GL)
                           |
                           v
                     FastAPI Backend (REST API / Async Engine)
                           |
                           v
                      LLM Agent (UF NaviGator AI Toolkit / gpt-oss-20b)
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
      Geocoding      Intersection      Data/GIS Tools
      (Nominatim)        Search              |
           |               |                |
           +---------------+----------------+
                           |
                           v
              Hybrid Spatial Access Layer
                    +------+------+
                    |             |
                    v             v
             PostgreSQL/PostGIS  Direct ArcGIS REST & Socrata SODA
                    |             |
                    +------+------+
                           |
                           v
                      Validation Layer (Pydantic / Provenance Engine)
                           |
                           v
                         Answer + Provenance + Map Highlights
```

---

## 2. Component Responsibilities

| Component | Technology | Responsibility |
|---|---|---|
| **Frontend UI** | React 18, TypeScript, Vite, MapLibre GL | Address search, map click, candidate list selection, chat panel, result card with provenance display. |
| **Backend API** | FastAPI, Python 3.12, Uvicorn, httpx | Application entrypoint, CORS configuration, typing and validation, endpoint routing. |
| **Agent Layer** | UF NaviGator AI Toolkit, `gpt-oss-20b` | Intent extraction, tool call planning, ambiguity clarification, synthesis of verified facts. |
| **Spatial Engine** | PostGIS & Python Haversine/GeoJSON | Meter-based geodesic distance calculations, radial buffer generation, spatial intersection matching. |
| **Data Adapters** | Async `FDOTClient` & `GainesvilleClient` | Querying FDOT FeatureServers and Gainesville Socrata SODA API; mapping CRS from EPSG:26917 to EPSG:4326. |
| **Validation Layer** | `validation_service.py` | Enforcing strict data truth rules: direct vs nearby classification, metric mismatch warnings, no-data enforcement. |

---

## 3. Data Flow & Lifecycles

### Location & Intersection Resolution Flow
1. User clicks the map at coordinate `(lat, lon)` or submits an address.
2. If address: geocoded via Nominatim with Gainesville bounding bias.
3. Coordinates sent to `GET /api/intersections/nearby?lat=...&lon=...`.
4. The system searches within 250 meters for intersections. If 0 found, automatically expands to 500 meters.
5. `resolve_intersection()` checks candidate distribution:
   - If 0 candidates: returns `status: "not_found"`.
   - If 1 candidate or 1 clearly dominant candidate (<50m away while 2nd candidate >120m away): returns `status: "resolved"`.
   - If multiple plausible candidates remain: returns `status: "needs_clarification"` with candidate list.
6. The user selects a single intersection to bind the spatial search area.

### Question Answering & Verification Flow
1. User asks a natural language question (e.g., *"Is this intersection signalized?"*).
2. The agent analyzes the question context (selected intersection ID + coordinates).
3. The agent triggers server-side registered tools:
   - `get_signal_information(intersection_id)`
   - `get_aadt_near_intersection(intersection_id)`
   - `get_hourly_traffic_volume(site_id, ...)`
   - `find_nearby_traffic_sites(intersection_id, ...)`
4. The tool executes against authoritative services, returning structured data.
5. The validation service verifies:
   - Is the value direct or nearby (>250m)?
   - Does the retrieved metric match the requested metric?
   - If hourly volume is missing, do NOT replace with AADT without explicit labeling.
6. Provenance metadata (agency, dataset, URL, record ID, timestamp, distance) is attached.
7. The response is presented to the user with map feature highlights.

---

## 4. Security & Safety Architecture

- **No Arbitrary SQL Generation**: The LLM agent has no direct database connection, credentials, or arbitrary SQL execution capabilities. It interacts exclusively via typed, server-side validated Python functions.
- **Environment Isolation**: API keys and database credentials reside exclusively in server-side environment variables and are never exposed to frontend bundles or client logs.
- **Controlled External Input**: All coordinates, radiuses, and identifiers are bounded and typed using Pydantic schemas.
