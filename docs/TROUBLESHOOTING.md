# Troubleshooting Guide

## 1. NaviGator AI Toolkit Authentication Issues

### Symptoms
- Chat returns: *"NaviGator API is not configured properly"* or status shows `navigator: "unconfigured"`.
- Error logs indicate HTTP 401 Unauthorized or 403 Forbidden.

### Solutions
1. Open `.env` in the repository root.
2. Ensure `NAVIGATOR_TOOLKIT_API_KEY` is populated with your personal secret key from `https://api.ai.it.ufl.edu/ui` (do not use the key ID).
3. Ensure `NAVIGATOR_BASE_URL` is set to `https://api.ai.it.ufl.edu/v1`.
4. Ensure `NAVIGATOR_MODEL` is set to a valid model that supports function/tool calling (e.g., `gpt-oss-20b`).
5. Restart the backend server so the new environment variables take effect.

---

## 2. Database & PostGIS Connection

### Symptoms
- `/health` reports `database: "offline"`.
- `docker: The term 'docker' is not recognized`.

### Explanation & Workaround
- If Docker Desktop is not installed or running, the backend seamlessly falls back to querying the official FDOT and City of Gainesville APIs directly live! All intersection lookups, signal queries, and AADT statistics function properly via live REST APIs.
- To enable local database caching with PostGIS:
  1. Install Docker Desktop for Windows.
  2. Run `docker compose up -d db`.
  3. The init scripts in `database/init/` will automatically execute, create the spatial schema, and build GiST spatial indexes.
  4. Once running, `/health` will report `database: "ok"`.

---

## 3. FDOT ArcGIS REST Service Issues

### Symptoms
- Nearby intersections return empty lists.
- Error logs show `httpx.HTTPError` querying `gis.fdot.gov`.

### Solutions
1. Verify internet connectivity and confirm `https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer?f=json` is accessible in your browser.
2. Check if FDOT has updated their layer indices by running:
   ```bash
   python scripts/discover_fdot_layers.py
   ```
   This will inspect the live service and refresh `backend/app/data/fdot_layer_config.json`.
3. If FDOT is experiencing temporary downtime, the system logs the incident and returns a user-friendly source-unavailable message without crashing.

---

## 4. City of Gainesville Open Data (Socrata) Issues

### Symptoms
- Traffic monitoring sites return empty lists.
- HTTP 404 or 400 when querying Socrata endpoints.

### Solutions
1. Confirm the underlying dataset ID is `v2qq-gus2` (note: `pfc3-w5ih` is a map canvas visualization that returns empty rows via the standard SODA API, while `v2qq-gus2` contains the actual tabular count data).
2. Verify connectivity to `https://data.cityofgainesville.org/resource/v2qq-gus2.json?$limit=1`.
3. Re-run `python scripts/inspect_gainesville_dataset.py` if dataset attributes need verification.

---

## 5. Geocoding / Address Search Issues

### Symptoms
- Entering an address fails to center the map or returns fallback coordinates.

### Solutions
1. OpenStreetMap Nominatim has a usage policy requiring an identifiable User-Agent header. This is pre-configured in `routes_locations.py`.
2. Ensure queries do not exceed rate limits (1 request per second is standard for Nominatim).
3. If an address is vague, Nominatim may fail to resolve; try including street cross-streets (e.g., `University Ave & NW 13th St`).

---

## 6. Frontend / Backend CORS & Port Issues

### Symptoms
- Browser console displays: *"Cross-Origin Request Blocked (CORS)"*.
- API requests fail with Network Error.

### Solutions
1. The backend is pre-configured to allow CORS from `http://localhost:5173`.
2. Ensure the backend is running on `http://localhost:8000`.
3. If accessing from another host or port, update `allow_origins` in `backend/app/main.py`.
4. In `frontend/vite.config.ts`, the development server proxies `/api` and `/health` requests to `http://localhost:8000`.
