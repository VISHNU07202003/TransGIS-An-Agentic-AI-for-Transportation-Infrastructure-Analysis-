# Current System Audit

## Existing Architecture
The current TransGIS prototype relies on a standard three-tier architecture:
1. **Frontend**: React + MapLibre GL UI that captures user locations, renders map pins, and provides an interactive chat interface.
2. **Backend**: FastAPI (Python) serving REST endpoints for map interactions, data retrieval, and agent chat proxying.
3. **Database**: PostgreSQL with PostGIS handling spatial data.
4. **Agent Orchestration**: A `TransportationAgent` that interfaces with the UF NaviGator toolkit (`gpt-oss-20b`) to translate user queries into server-side tool executions against raw GIS layers. 

In this model, the agent relies entirely on retrieving localized raw source records (like FDOT signals and AADT) and passing them through a Python `validation_service.py` to build answers. There is no precomputed canonical "intersection" or "road segment" entity—queries hit raw provider records directly.

## Existing Frontend
- **Framework:** React 18, TypeScript, Vite.
- **Key Components:**
  - `MapView.tsx`: MapLibre GL integration handling the base map, user clicks, and rendering candidate intersections.
  - `ChatPanel.tsx`: Floating chat interface allowing conversational queries.
  - `SearchBar.tsx`: Geocoding (via Photon/Nominatim) with Gainesville bounding bias.
  - `ResultCard.tsx` / `AnalysisResults.tsx` / `ProvenancePanel.tsx`: Displays provenance, data sources, and the selected intersection context.
- **State/Hooks:** `useChat.ts` (manages conversation and API calls), `useMapSelection.ts` (manages selected point and intersections), `usePlaceLabel.ts`.
- **Status:** Builds cleanly. Fully functional.

## Existing Backend
- **Framework:** FastAPI (Python 3.12).
- **Key Modules:**
  - `app/main.py`: App configuration, CORS, endpoint routing.
  - `app/api/`: REST endpoints for chat, health, locations, places, data.
  - `app/agents/agent.py`: Contains the `TransportationAgent` that runs a 5-step loop calling tools.
  - `app/services/validation_service.py`: Enforces data provenance and verifies measurement units.
- **Status:** Starts cleanly, serves API endpoints.

## Existing Database Schema
- **File:** `database/init/002_schema.sql`
- **Tables:**
  - `data_sources`: Registry of raw data providers (FDOT, Gainesville).
  - `intersections`: Raw intersections tied to a `source_id`.
  - `traffic_sites` & `traffic_observations`: Raw site and volume data.
  - `traffic_signals`: Raw traffic signal locations.
  - `roadway_segments`: Line strings representing road segments with AADT.
- **Evaluation:** The schema stores raw provider records with geometries (`GEOMETRY(Point, 4326)`). It lacks any concept of canonical entities (e.g., `GNV-INT-00452`) or entity lifecycles (splits/merges).

## Existing GIS Functionality
- **File:** `app/gis/spatial.py`
- **Capabilities:**
  - WGS84 ellipsoidal shortest surface distance calculations (`geodesic_distance_m`).
  - Distance calculations to lines and complex geometries (`geometry_distance_m`).
  - PostGIS radial search operations (`ST_DWithin`, `ST_Distance`, `ST_ClosestPoint`).
  - Spatial bounding and GeoJSON creation.
- **Status:** Works well but operates strictly on raw records.

## Existing Data Integrations
- **Providers:** FDOT (Florida Department of Transportation) and City of Gainesville.
- **Datasets:** RCI Intersections, Traffic Signal Locations TDA, Annual Average Daily Traffic (AADT).
- **Files:** `app/data/source_registry.py`, `scripts/load_reference_data.py`.
- **Status:** Integrations retrieve external datasets correctly, mapping into `EPSG:4326`.

## Existing NaviGator / AI Integration
- **Files:** `app/agents/navigator_client.py`, `app/agents/agent.py`
- **Implementation:** Wraps the standard OpenAI Python client pointed to UF's NaviGator endpoint (`gpt-oss-20b`). Provides chat completion with JSON-schema tools.
- **Features:** If the API key is missing or an error occurs, it drops into a deterministic Python fallback `_fallback_process` which uses keyword matching.
- **Status:** Functional but highly reliant on hardcoded fallback logic for standard queries. 

## Existing Tests
- **Framework:** Pytest, AnyIO.
- **Coverage:** Tests for chat endpoints, GIS distances, external API clients, validation logic.
- **Status:** 42 total tests. 36 pass, 3 are skipped, 3 fail, 1 errors out.
  - **Failures:** 
    1. `test_live_congestion_query_does_not_infer_peak_delays_from_aadt`: The deterministic fallback *does* make an estimated assumption about congestion, violating the test's constraint.
    2. `test_no_location_invites_florida_selection`: The bot says "Gainesville" instead of "Florida".
    3. `test_fdot_intersections_use_meter_radius_and_wgs84`: The returned geometry includes the `spatialReference` dictionary, failing a strict dict equality check.
  - **Errors:** 
    1. `test_liveness_never_probes_external_services`: Fails an assertion tracking unmocked network accesses (the app swallowed an unmocked DB or HTTP request during test teardown).

## What Currently Works
- React/MapLibre map rendering and interaction.
- Address search (Photon/Nominatim).
- Backend spatial distance utilities (WGS84 ellipsoidal geodesics).
- Basic tool calling loop in `TransportationAgent`.
- Provenance validation framework (`validation_service.py`).
- PostgreSQL/PostGIS database initialization.

## What Is Broken or Incomplete
- **Test Suite:** Contains 4 failing/erroring tests due to strict assertions and unmocked network calls.
- **Deterministic Agent Fallback:** Highly brittle, relying on keyword searches (e.g., `"signal" in msg_lower`).
- **Entity Resolution:** Currently non-existent. Queries rely entirely on raw `source_object_id` references rather than deduplicated canonical entities.

## Reusable Components
- **Frontend UI:** The React components, MapLibre config, and Chat interfaces are excellent and should be preserved entirely.
- **GIS Core:** `app/gis/spatial.py` contains robust geographic math (Geodesic WGS84) that we will need.
- **Validation/Provenance:** The strict separation of measurements and the `create_no_data_result` paradigm perfectly align with the goal of reducing hallucinations.
- **NaviGator Client:** The OpenAI wrapper is standard and reusable.

## Components Requiring Refactoring
- **Database Schema (`002_schema.sql`):** Needs to be augmented with canonical tables (`canonical_intersections`, `canonical_roadways`) and mapping tables that link raw `traffic_sites` to canonical IDs.
- **Agent Logic (`agent.py`):** Must be rewritten to use canonical entity lookup tools rather than directly querying raw FDOT intersections. The brittle deterministic fallback should eventually be replaced or simplified.
- **Spatial Queries:** `find_nearby_intersections` needs to query the canonical entity layer, not raw source data.

## Components That May Be Removed
- **Brittle Fallback Chat Rules:** Extensive hardcoded string matching in `agent.py`'s `_fallback_process` can be reduced once the LLM orchestration is fully tested.

## New Architecture Gaps
- **Entity Resolution Pipeline:** No code exists to normalize street names, calculate string distance, perform blocking, or cluster raw records into stable entities.
- **Canonical ID Lifecycle:** No tombstoning, split/merge tracking, or history for stable IDs (e.g. `GNV-INT-00452`).
- **Evaluation Framework:** We need the capability to toggle the agent between System A (Raw), System B (Normalized), and System C (Canonical TransGIS) to conduct the final fair experiments.

## Technical Risks
- **Data Heterogeneity:** Gainesville and FDOT likely use different schemas, naming conventions, and spatial precisions. Reconciling them will be challenging.
- **LLM Tool Reliance:** Ensuring `gpt-oss-20b` can effectively utilize the new canonical entity lookup tools without hallucinating spatial queries.

## Recommended Migration Plan

### KEEP
- **Frontend React App:** Retain entirely.
- **PostGIS database:** Retain the engine and existing raw data tables as the ingestion layer.
- **Spatial math (`spatial.py`):** Keep WGS84 geodesic algorithms.
- **Validation / Provenance services:** Keep and adapt to point to canonical entities.
- **NaviGator Integration:** Keep the existing OpenAI integration.

### REFACTOR
- **Agent Orchestration:** Shift tools to operate on canonical entities rather than raw tables.
- **Database Schema:** Introduce `canonical_entities` and join tables to `data_sources`. 
- **Failing Tests:** Update assertions to match the current application state (e.g., Gainesville instead of Florida, removing strict spatialReference dict checks).

### REMOVE
- **Brittle Hardcoded Keyword Responses:** Remove massive nested `if/elif` blocks in the agent fallback once the LLM is proven stable.

### ADD LATER
- **Entity Resolution Pipeline:** Normalization, spatial blocking, pair scoring, and constrained clustering logic.
- **Canonical ID Lifecycle:** Tombstoning and merge/split tracking.
- **Evaluation Harness:** Tools to test System A, B, and C baselines side-by-side.

---

### First 3-5 Technical Changes
1. **Fix Failing Tests:** Resolve the 4 broken/erroring tests in `pytest` to establish a stable, green CI baseline before any refactoring.
2. **Schema Augmentation:** Add `canonical_intersections` and `canonical_roadways` tables to the PostGIS schema alongside migration scripts.
3. **Data Discovery Scripts:** Write ingestion scripts to sample FDOT and Gainesville datasets specifically to measure coordinate drift and street-name discrepancies (preparing for entity resolution).
4. **Draft Entity Resolution Logic:** Implement basic text normalization (standardizing "Ave", "Avenue", "NW") and spatial clustering algorithms in a new module (without replacing the live endpoints yet).
