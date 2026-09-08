<div align="center">

# 🌐 TransGIS: An Agentic AI for Transportation Infrastructure Analysis

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VISHNU07202003/TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgis.net/)
[![MapLibre GL](https://img.shields.io/badge/MapLibre_GL-4.7-2F54EB?style=for-the-badge&logo=mapbox&logoColor=white)](https://maplibre.org/)
[![NaviGator AI](https://img.shields.io/badge/UF_NaviGator_AI-gpt--oss--20b-F37021?style=for-the-badge)](https://docs.ai.it.ufl.edu/)
[![Tests](https://img.shields.io/badge/Tests-23%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](backend/tests/)

<p align="center">
  <b>TransGIS is a next-generation agentic geospatial platform engineered with modern glassmorphic Tailwind styling, React, FastAPI, and UF NaviGator AI (<code>gpt-oss-20b</code>). It enables engineers, urban planners, and researchers to query urban intersection infrastructure across Gainesville, Florida via map clicks or address search, invokes authoritative FDOT & municipal open data via autonomous spatial tools, and ensures zero hallucinations through rigorous provenance tracking.</b>
</p>

[Key Features](#-key-features) • [System Architecture](#-system-architecture) • [Live Data Sources](#-live-data-sources) • [Quick Start](#-quick-start) • [Interactive Examples](#-interactive-question-showcase) • [Documentation](#-documentation)

</div>

---

## 🌟 Key Features

- 🗺️ **Interactive Spatial Exploration**: Click any Gainesville roadway or search addresses via OpenStreetMap Nominatim with automated 250m/500m buffer lookups.
- 🤖 **Autonomous Tool-Calling Agent**: Powered by **UF NaviGator AI (`gpt-oss-20b`)** with strict 5-step bounded tool loops, Pydantic argument validation, and zero-hallucination safeguards.
- 🛡️ **Authoritative Truth & No-Data Policy**:
  - Distinguishes **AADT** (annualized daily volume) from **Hourly Traffic Volume**.
  - Refuses to fabricate missing hourly counts or claim live real-time conditions without sensor telemetry.
  - Transparently offers common-sense operational assumptions derived from historical AADT and signal data.
- 📍 **Authoritative Provenance**: Every factual number is bound to its origin: agency, dataset, direct REST URL, official station/OBJECTID, observation year, and spatial distance.
- ⚡ **Hybrid Spatial Architecture**: Works directly with live **FDOT ArcGIS REST FeatureServers** and **City of Gainesville SODA API**, with optional local PostGIS acceleration.

---

## 🏛️ System Architecture

```text
                           USER
                             |
                +------------+------------+
                |                         |
          Address Input               Map Click
                |                         |
                +------------+------------+
                             v
                    Frontend (React 18 + MapLibre GL)
                             |
                             v  REST API / CORS
                     FastAPI Backend (Python 3.12)
                             |
                             v
               Transportation Agent (UF NaviGator AI / gpt-oss-20b)
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
        Geocoding      Intersection     Data / GIS Tools
       (Nominatim)        Search             |
             |               |               |
             +---------------+---------------+
                             |
                             v
             +---------------+---------------+
             |                               |
             v                               v
    PostgreSQL + PostGIS          Live Government APIs
    (Local Cache / Spatial)      (FDOT RCI & Gainesville SODA)
             |                               |
             +---------------+---------------+
                             |
                             v
                      Validation Engine
                             |
                             v
                  Answer + Provenance + Map Highlights
```

---

## 📡 Live Data Sources

| Source / Agency | Dataset | Protocol / Layer | Native CRS | Output CRS |
|---|---|---|---|---|
| **FDOT** | Intersections Inventory | ArcGIS FeatureServer (Layer 6) | EPSG:26917 | EPSG:4326 |
| **FDOT** | Annual Average Daily Traffic (AADT) | ArcGIS FeatureServer (Layer 0) | EPSG:26917 | EPSG:4326 |
| **FDOT** | Continuous Traffic Monitoring Sites | ArcGIS FeatureServer (Layers 9 & 16) | EPSG:26917 | EPSG:4326 |
| **FDOT** | Traffic Signal Locations | ArcGIS FeatureServer (TDA Service) | EPSG:4326 | EPSG:4326 |
| **City of Gainesville** | Municipal Traffic Count Stations | Socrata SODA Open Data (`v2qq-gus2`) | EPSG:4326 | EPSG:4326 |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 20+**
- *(Optional)* **Docker Desktop** (for PostGIS local database container)
- **UF NaviGator AI API Key** *(or uses intelligent deterministic fallback)*

### 1. Clone & Configure
```bash
git clone https://github.com/VISHNU07202003/TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-.git
cd TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-
cp .env.example .env
```
Edit `.env` to add your NaviGator secret key:
```env
NAVIGATOR_TOOLKIT_API_KEY=sk-your-navigator-secret-key-here
NAVIGATOR_BASE_URL=https://api.ai.it.ufl.edu/v1
NAVIGATOR_MODEL=gpt-oss-20b
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*API documentation available at `http://localhost:8000/docs`.*

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
*Interactive Map Application runs at `http://localhost:5173`.*

---

## 💬 Interactive Question Showcase

<details>
<summary><b>1. Natural Volume Inquiry ("How many vehicles go in this intersection?")</b></summary>

> **Agent:**  
> **Annual Average Daily Traffic (AADT) near intersection 80329 (SW 13TH ST / MLK HWY)**  
> - **AADT Volume**: 2,300 vehicles/day (Year 2025)  
> - **Roadway Segment**: 26000040 (250m from junction)  
> - **Source**: FDOT Annual Average Daily Traffic dataset  
> *(No hourly telemetry exists for this specific junction; AADT provides the authoritative annualized daily volume).*
</details>

<details>
<summary><b>2. Real-Time Condition & Assumption ("Is there traffic in this intersection?")</b></summary>

> **Agent:**  
> **Intersection ID 79340 (SR 24 / Archer Rd.)**  
> - **No real-time data**: I do not have live camera feeds or active GPS traffic jam telemetry.  
> - **Historical traffic level**: Authoritative FDOT records report an AADT of **~26,705 vehicles/day** on Archer Rd. and **44,000–49,000 vehicles/day** on the cross-street with 3 active traffic signals.  
> - **Typical conditions (Assumption)**: This is a high-volume corridor (>20,000 vehicles/day). You can reasonably assume it typically experiences heavy traffic and delays during morning (7:30–9:00 AM) and evening (4:30–6:30 PM) commute hours.
</details>

<details>
<summary><b>3. Traffic Signal Status ("Is this intersection signalized?")</b></summary>

> **Agent:**  
> Yes, this intersection is signalized. FDOT Traffic Signal record (`Traffic Control Signal`, ID 331) is located directly at the intersection on state corridor 26090000.
</details>

<details>
<summary><b>4. Strict No-Data Policy ("What was the traffic volume from 5 PM to 6 PM here?")</b></summary>

> **Agent:**  
> No authoritative hourly traffic-volume observation was found for this intersection. Note: An AADT value of 2,300 vehicles/day is available for the adjacent roadway segment, but AADT is an annualized daily average and is not the requested hourly volume.
</details>

---

## 🧪 Test Suite & Verification

The prototype includes a comprehensive test suite covering spatial calculations, live government API clients, health endpoints, tool schemas, and chat workflows.

```bash
cd backend
pytest -v
```

```text
============================= test session starts =============================
collected 21 items

tests/test_chat.py::test_chat_location_resolution PASSED                 [  4%]
tests/test_chat.py::test_chat_signal_query PASSED                        [  9%]
tests/test_chat.py::test_chat_hourly_traffic_volume_no_data_policy PASSED [ 14%]
tests/test_chat.py::test_chat_how_many_vehicles_query PASSED             [ 19%]
tests/test_chat.py::test_chat_traffic_jam_realtime_refusal PASSED        [ 23%]
tests/test_chat.py::test_geocode_endpoint PASSED                         [ 28%]
tests/test_clients.py::test_fdot_client_intersections_query PASSED       [ 33%]
tests/test_clients.py::test_gainesville_client_traffic_sites_query PASSED [ 38%]
tests/test_health.py::test_health_endpoint PASSED                        [ 42%]
tests/test_health.py::test_data_sources_endpoint PASSED                  [ 47%]
tests/test_spatial.py::test_haversine_distance_calculation PASSED        [ 52%]
tests/test_spatial.py::test_create_point_wkt PASSED                      [ 57%]
tests/test_spatial.py::test_resolve_intersection_not_found PASSED        [ 61%]
tests/test_spatial.py::test_resolve_intersection_single PASSED           [ 66%]
tests/test_spatial.py::test_resolve_intersection_ambiguity_needs_clarification PASSED [ 71%]
tests/test_spatial.py::test_resolve_intersection_clear_dominant PASSED   [ 76%]
tests/test_tools.py::test_tool_registry_schemas PASSED                   [ 80%]
tests/test_tools.py::test_execute_unknown_tool PASSED                    [ 85%]
tests/test_tools.py::test_execute_find_intersections_tool PASSED         [ 90%]
tests/test_validation.py::test_validate_direct_observation PASSED        [ 95%]
tests/test_validation.py::test_create_no_data_result PASSED              [100%]

============================= 21 passed in 27.14s =============================
```

---

## 📚 Documentation

Detailed specifications and architecture design records are in [`docs/`](docs/):

- 📖 **[User Manual](docs/USER_MANUAL.md)**: Full walkthrough for map navigation, queries, and provenance interpretation.
- 🏗️ **[System Architecture](docs/ARCHITECTURE.md)**: Component diagrams, lifecycle flows, and security design.
- 📊 **[Data Sources](docs/DATA_SOURCES.md)**: Discovered FDOT layers, SODA datasets, and CRS transformations.
- 📋 **[Test Plan](docs/TEST_PLAN.md)**: 21-point test matrix and validation rules.
- 🔧 **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Guidance on NaviGator auth, CORS, and network fallback.

---

## ⚖️ License & Research Notice

This project is licensed under the [MIT License](LICENSE).

> **Disclaimer**: This software is an academic graduate research prototype developed for educational and research evaluation. It is not intended for live real-time traffic signal control, safety-critical dispatch, or autonomous vehicle navigation.
