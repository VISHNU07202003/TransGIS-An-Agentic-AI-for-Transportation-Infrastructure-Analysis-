# CRS Strategy

## 1. Overview
A Coordinate Reference System (CRS) mismatch during spatial conflation introduces hidden geometric offsets. TransGIS explicitly manages CRS boundaries to ensure that entity resolution processes rely on accurate, metric-based spatial operations while supporting standard web-mapping outputs.

## 2. Policy Definitions

### A. Source CRS
- **OpenStreetMap (OSM):** `EPSG:4326` (WGS 84)
- **FDOT RCI APIs:** Requested and retrieved in `EPSG:4326` (via `outSR=4326` parameter).
- **Gainesville Open Data:** `EPSG:4326`.
- **Policy:** All incoming data must explicitly declare its CRS. During ingestion, it is validated. If the source CRS is not `EPSG:4326`, it is transformed immediately.

### B. Canonical Storage CRS
- **PostGIS Storage:** `EPSG:4326` (WGS 84) using PostGIS `geometry(Geometry, 4326)` or `geography` columns.
- **Why:** Universally compatible with GeoJSON, standard map engines (MapLibre), and native Web GIS stacks. Ensures the primary datastore is portable.

### C. Metric-Computation CRS (Entity Resolution)
- **Problem:** `EPSG:4326` units are in degrees. Conflation algorithms (e.g., perpendicular edge distance, spatial blocking, snapping) require precise metric distances (meters). Using unprojected degrees for geometric operations introduces severe distortion.
- **Datum Investigation & Correction:** 
  - FDOT data is typically maintained in NAD83. The Florida State Plane coordinate system is broken into zones; Alachua County (Gainesville) is in the **Florida North** zone.
  - Previous assumptions about EPSG codes were corrected against the EPSG registry:
    - **`EPSG:6439`** = NAD83(2011) / Florida GDL Albers (Statewide, not Florida North).
    - **`EPSG:6440`** = NAD83(2011) / Florida North (units: metres).
    - **`EPSG:2779`** = NAD83(HARN) / Florida North (units: metres).
    - **`EPSG:2778`** = NAD83(HARN) / Florida West (Incorrect zone for Gainesville).
  - **Selected CRS Pipeline:** 
    1. Identify native source CRS (e.g., `EPSG:4326` for Socrata GeoJSON, or `EPSG:4269` NAD83 for raw FDOT shapefiles).
    2. Identify the specific datum.
    3. Transform to the appropriate metric CRS for calculations:
       - Default/Current Data (NAD83 2011): Use **`EPSG:6440`**.
       - Legacy Data (NAD83 HARN): Use **`EPSG:2779`**.
    4. We explicitly mandate the use of the **metre** variants (as opposed to US Survey Feet variants) to prevent unit mismatches.
- **Usage:**
  - Python conflation modules will use `pyproj.Transformer` to project geometries from `4326` to `6440` (or `2779`) before distance checks.
  - Database-level operations will use `ST_Transform(geom, 6440)`.

### D. API and Map CRS
- **Frontend / API:** All API endpoints must return GeoJSON in `EPSG:4326`. 
- **MapLibre GL:** Naturally handles `EPSG:4326` coordinates projected to Web Mercator (`EPSG:3857`) for rendering.

## 3. Transformation Testing
Unit tests in `tests/test_crs.py` will enforce projection accuracy by asserting that known control points in Gainesville transform correctly between `EPSG:4326` and `EPSG:2778` within a sub-millimeter tolerance, and that geodesic distance vs projected distance calculations align safely.
