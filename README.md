<div align="center">

# ?? TransGIS: Grounded Agentic AI for Transportation Infrastructure Analysis

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VISHNU07202003/TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-)
[![CI Pipeline](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](.github/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.4-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgis.net/)
[![MapLibre GL](https://img.shields.io/badge/MapLibre_GL-4.7-2F54EB?style=for-the-badge&logo=mapbox&logoColor=white)](https://maplibre.org/)
[![NaviGator AI](https://img.shields.io/badge/UF_NaviGator_AI-gpt--oss--20b-F37021?style=for-the-badge)](https://docs.ai.it.ufl.edu/)
[![Tests](https://img.shields.io/badge/Behavioral_Coverage-23_Tests-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](backend/tests/)

<p align="center">
  <b>A grounded agent architecture that restricts factual transportation responses to validated authoritative records (FDOT & City of Gainesville open data), transparently binds outputs to data provenance, and explicitly refuses unsupported measurements through a deterministic no-data policy.</b>
</p>

[Key Architecture](#-key-architecture--engineering-guardrails) • [System Architecture](#-system-architecture) • [Live Data Sources](#-live-data-sources) • [Containerized Deployment](#-containerized-deployment-docker) • [Behavioral Test Matrix](#-behavioral-test-coverage) • [Interactive Showcase](#-interactive-question-showcase) • [Documentation](#-documentation)

</div>

---

## ?? Key Architecture & Engineering Guardrails

- ??? **Grounded Agent Architecture**: Translates user natural language into bounded spatial tool calls, restricting numerical metrics to validated records and eliminating unsupported fabrications.
- ?? **Metric Disambiguation & Strict No-Data Policy**:
  - Differentiates **AADT** (annualized daily average volume per roadway segment) from **Hourly Traffic Volume**.
  - Explicitly refuses to substitute daily averages for requested hourly bins; responds with a verified `UNAVAILABLE` payload when granular sensor telemetry is not recorded.
  - Transparently separates authoritative records from operational inferences (clearly labeling peak-hour assessments as historical estimations rather than real-time camera observations).
- ?? **End-to-End Data Provenance**: Binds every factual measurement to its origin: authoritative agency (FDOT / City of Gainesville), dataset name, direct REST API endpoint, official station/OBJECTID, observation year, and spatial proximity.
- ? **Resilient Hybrid Spatial Engine**: Queries local PostGIS spatial indexes first, with an automated fallback to live **FDOT ArcGIS REST FeatureServers** and **City of Gainesville SODA API** for zero-downtime availability.
- ??? **High-Density Dark Glassmorphic UI**: Interactive MapLibre GL frontend styled with **Tailwind CSS v4**, animated radar markers, Markdown table rendering, and an interactive audit trail drawer.

---

## ??? System Architecture

```text
                           USER INTERACTION
                                  |
                +-----------------+-----------------+
                |                                   |
          Address Geocoding                     Map Click
          (Nominatim Service)             (Coordinates lat/lon)
                |                                   |
                +-----------------+-----------------+
                                  v
                  Frontend (React 18 + MapLibre GL)
                                  |
                                  v  REST API (CORS / JSON)
                   FastAPI Backend (Python 3.12)
                                  |
                                  v
              Transportation Agent (UF NaviGator AI / gpt-oss-20b)
                                  |
       +--------------------------+--------------------------+
       |                          |                          |
       v                          v                          v
  Spatial Ambiguity         AADT / Signals           Traffic Monitoring
  Resolution Tool           Extraction Tool          Site Registry Tool
       |                          |                          |
       +--------------------------+--------------------------+
                                  |
                                  v
       +--------------------------+--------------------------+
       |                                                     |
       v                                                     v
  PostgreSQL / PostGIS                             Live Government APIs
  (Spatial Indexes / ST_DWithin)                (FDOT ArcGIS & Gainesville SODA)
       |                                                     |
       +--------------------------+--------------------------+
                                  |
                                  v
                   Validation & Provenance Engine
         (Strict metric matching, refusal logic & audit trace)
                                  |
                                  v
                Grounded Answer + Audit Metadata Card
```

---

## ?? Authoritative Data Sources

| Source / Agency | Dataset | Protocol / Layer | Native CRS | Output CRS |
|---|---|---|---|---|
| **FDOT** | Intersections Inventory | ArcGIS FeatureServer (Layer 6) | EPSG:26917 | EPSG:4326 |
| **FDOT** | Annual Average Daily Traffic (AADT) | ArcGIS FeatureServer (Layer 0) | EPSG:26917 | EPSG:4326 |
| **FDOT** | Continuous Traffic Monitoring Sites | ArcGIS FeatureServer (Layers 9 & 16) | EPSG:26917 | EPSG:4326 |
| **FDOT** | Traffic Signal Locations | ArcGIS FeatureServer (TDA Service) | EPSG:4326 | EPSG:4326 |
| **City of Gainesville** | Municipal Traffic Count Stations | Socrata SODA Open Data (`v2qq-gus2`) | EPSG:4326 | EPSG:4326 |

---

## ?? Containerized Deployment (Docker)

The repository provides a complete multi-container Docker Compose specification (`db`, `backend`, `frontend`) configured with network bridging, database healthchecks, and Nginx reverse proxying.

### One-Command Launch:
```bash
# Clone the repository
git clone https://github.com/VISHNU07202003/TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-.git
cd TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-

# Configure environment variables
cp .env.example .env

# Launch entire stack (PostGIS + FastAPI + Nginx/React)
docker compose up --build -d
```
- **Web Interface**: `http://localhost:5173`
- **FastAPI OpenAPI Documentation**: `http://localhost:8000/docs`
- **PostGIS Spatial Database**: `localhost:5432`

---

## ?? Local Developer Quick Start

### 1. Backend Service
```bash
cd backend
python -m venv .venv
# Windows: .\.venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Application
```bash
cd frontend
npm install
npm run dev
```

---

## ?? Behavioral Test Coverage

Rather than tracking raw test counts, the test suite verifies **system behavior across critical edge cases, spatial ambiguity, external API failures, and hallucination guardrails**:

| Behavioral Dimension | Test Module | Verification Scope |
|---|---|---|
| **Ambiguity Resolution** | `test_spatial.py`, `test_chat.py` | Detects multiple intersections within search radius; returns `needs_clarification` or ranks dominant intersection by distance. |
| **Spatial Distance Integrity** | `test_spatial.py` | Verifies Haversine geodesic calculations against PostGIS `ST_Distance` spherical projections. |
| **No-Data Policy Enforcement** | `test_chat.py`, `test_validation.py` | Guarantees system returns explicit `UNAVAILABLE` payload when hourly volume is queried, refusing to substitute AADT or invent numbers. |
| **Quantitative Volume Queries** | `test_chat.py` | Confirms direct roadway AADT breakdowns are returned without unsolicited conversational essays. |
| **Real-Time Refusal Guardrail** | `test_chat.py` | Validates clear refusal when real-time traffic jams or camera feeds are requested, falling back to historical AADT operational inferences. |
| **External API Resilience** | `test_clients.py` | Mocks FDOT ArcGIS FeatureServer & Gainesville SODA endpoints; verifies response parsing and fallback logic. |
| **Tool Argument Contracts** | `test_tools.py` | Validates Pydantic schemas, type coercions, and error handling for unknown tool invocations. |

### Run Test Suite:
```bash
cd backend
pytest -v
```

```text
============================= test session starts =============================
collected 23 items

backend/tests/test_chat.py::test_chat_location_resolution PASSED                 [  4%]
backend/tests/test_chat.py::test_chat_signal_query PASSED                        [  8%]
backend/tests/test_chat.py::test_chat_hourly_traffic_volume_no_data_policy PASSED [ 13%]
backend/tests/test_chat.py::test_chat_how_many_vehicles_query PASSED             [ 17%]
backend/tests/test_chat.py::test_chat_traffic_jam_realtime_refusal PASSED        [ 21%]
backend/tests/test_chat.py::test_geocode_endpoint PASSED                         [ 26%]
backend/tests/test_clients.py::test_fdot_client_intersections_query PASSED       [ 30%]
backend/tests/test_clients.py::test_gainesville_client_traffic_sites_query PASSED [ 34%]
backend/tests/test_health.py::test_health_endpoint PASSED                        [ 39%]
backend/tests/test_health.py::test_data_sources_endpoint PASSED                  [ 43%]
backend/tests/test_spatial.py::test_haversine_distance_calculation PASSED        [ 47%]
backend/tests/test_spatial.py::test_create_point_wkt PASSED                      [ 52%]
backend/tests/test_spatial.py::test_resolve_intersection_not_found PASSED        [ 56%]
backend/tests/test_spatial.py::test_resolve_intersection_single PASSED           [ 60%]
backend/tests/test_spatial.py::test_resolve_intersection_ambiguity_needs_clarification PASSED [ 65%]
backend/tests/test_spatial.py::test_resolve_intersection_clear_dominant PASSED   [ 69%]
backend/tests/test_tools.py::test_tool_registry_schemas PASSED                   [ 73%]
backend/tests/test_tools.py::test_execute_unknown_tool PASSED                    [ 78%]
backend/tests/test_tools.py::test_execute_find_intersections_tool PASSED         [ 82%]
backend/tests/test_validation.py::test_validate_direct_observation PASSED        [ 86%]
backend/tests/test_validation.py::test_create_no_data_result PASSED              [ 91%]
backend/tests/test_validation.py::test_validate_hourly_volume_unavailable PASSED [ 95%]
backend/tests/test_validation.py::test_validate_aadt_format PASSED               [100%]

============================= 23 passed in 49.44s =============================
```

---

## ?? Interactive Question Showcase

<details>
<summary><b>1. Quantitative Volume Inquiry ("How many vehicles go in this intersection?")</b></summary>

> **Agent Response:**  
> **Annual Average Daily Traffic (AADT) near intersection 80329 (SW 13TH ST / MLK HWY)**  
> Approximately **2,300 vehicles per day (AADT)** travel along the connecting corridor (Year 2025 counts).  
> *Note: FDOT records volume by roadway segment (AADT = vehicles/day on each street) rather than a combined intersection turning-movement total.*
</details>

<details>
<summary><b>2. Qualitative Condition Query ("Is there traffic in this intersection?")</b></summary>

> **Agent Response:**  
> No, I do not have live or real-time traffic camera/sensor data for intersection 79340.  
> However, authoritative FDOT records report an AADT of **~26,705 vehicles/day** on Archer Rd. and **44,000–49,000 vehicles/day** on the cross-street.  
> *Assessment (Inference)*: This is a high-volume corridor (>20,000 vehicles/day), typically experiencing noticeable peak-hour slowdowns during morning (7:30–9:00 AM) and evening (4:30–6:30 PM) commute hours.
</details>

<details>
<summary><b>3. Traffic Signal Status ("Is this intersection signalized?")</b></summary>

> **Agent Response:**  
> Yes, this intersection is signalized. FDOT Traffic Signal record (`Traffic Control Signal`, ID 331) is located directly at the intersection on state corridor 26090000.
</details>

<details>
<summary><b>4. Strict No-Data Policy ("What was the traffic volume from 5 PM to 6 PM here?")</b></summary>

> **Agent Response:**  
> No authoritative hourly traffic-volume observation was found for this location.  
> *Note: An AADT value of 2,300 vehicles/day is available for the adjacent roadway segment, but AADT represents an annualized daily average and cannot be substituted for hourly volume.*
</details>

---

## ?? Documentation

Detailed specifications and architecture design records are in [`docs/`](docs/):

- ?? **[User Manual](docs/USER_MANUAL.md)**: Full walkthrough for map navigation, queries, and provenance interpretation.
- ??? **[System Architecture](docs/ARCHITECTURE.md)**: Component diagrams, lifecycle flows, and security design.
- ?? **[Data Sources](docs/DATA_SOURCES.md)**: Discovered FDOT layers, SODA datasets, and CRS transformations.
- ?? **[Test Plan](docs/TEST_PLAN.md)**: Behavioral test matrix and validation rules.
- ?? **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Guidance on NaviGator auth, CORS, and network fallback.

---

## ?? License & Research Notice

This project is licensed under the [MIT License](LICENSE).

> **Disclaimer**: This software is an academic graduate research prototype developed for educational and research evaluation. It is not intended for live real-time traffic signal control, safety-critical dispatch, or autonomous vehicle navigation.

