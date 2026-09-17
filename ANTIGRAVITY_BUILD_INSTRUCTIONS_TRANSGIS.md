# Antigravity Build Instructions — TransGIS

## Project Name
**TransGIS**

## Academic Title
**Exploration and Prototype Development of an Agentic AI System for Transportation Infrastructure Analysis**

## Your Role
You are the implementation agent for this project. Build the prototype end-to-end from the existing repository.

Treat this file as the primary build instruction. If the repository already contains working code, preserve and extend it rather than rewriting everything.

Do not expand the project beyond the defined MVP.

---

## 1. Project Goal

Build a working prototype where a user can:
1. Open an interactive map of Gainesville, Florida.
2. Search an address or click on the map.
3. Ask a natural-language transportation question.
4. Resolve the selected location to one or more nearby intersections.
5. Ask the user to choose when the location is ambiguous.
6. Use deterministic GIS operations to identify relevant transportation records.
7. Query authoritative FDOT and City of Gainesville data.
8. Validate the meaning of the returned measurement.
9. Return a natural-language answer with source/provenance.
10. Visualize the selected intersection, search area, and data site on the map.

**Primary example:**  
*"What was the traffic volume at this intersection between 5 PM and 6 PM?"*

If authoritative hourly data does not exist for that location/time, return:  
*"No authoritative data available for this request."*

**Never fabricate or estimate missing traffic measurements.**

---

## 2. Final Technology Stack

Use the following stack unless an existing repository implementation already uses an equivalent compatible choice:

### AI
- **Primary LLM:** `gpt-oss-20b`
- **Provider:** UF NaviGator Toolkit
- **Embeddings:** `nomic-embed-text-v1.5` *(Optional for documentation/metadata RAG only)*

### Backend
- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy / PostGIS engine

### Database
- PostgreSQL
- PostGIS (spatial geometry, ST_DWithin, ST_Distance, spherical spatial indexing)
- pgvector *(only if optional documentation RAG is implemented)*

### Frontend
- React 18
- TypeScript
- MapLibre GL JS
- Tailwind CSS v4

### Data Sources
Use only:
1. **Florida Department of Transportation (FDOT)**
2. **City of Gainesville official/open transportation data (dataGNV SODA)**

*Do not use random third-party traffic websites as authoritative sources.*

---

## 3. Non-Negotiable Rules

Follow these rules throughout implementation:
1. **The LLM does not perform GIS calculations.** GIS calculations belong in backend/PostGIS code.
2. **The LLM does not invent traffic values.**
3. **Do not convert AADT into hourly volume.**
4. **Do not sum nearby road counts** and call the result intersection traffic volume unless the source explicitly defines that interpretation.
5. **The nearest traffic site is not automatically the correct traffic site.**
6. **Preserve source/provenance** for every transportation result.
7. **If a requested measurement is unavailable, return `no_data`.**
8. **If multiple intersections are plausible, return a clarification request.**
9. **Use authoritative FDOT/Gainesville records only.**
10. **Do not create fake API endpoints, field names, or provider schemas.**
11. **Verify live data schemas** before coding tightly against them.
12. **Keep the prototype focused on Gainesville.**
13. **Do not add** traffic prediction, RL, V2X, digital twins, CV, IoT, or autonomous vehicles.
14. **Do not add unnecessary microservices.**

---

## 4. First Action: Inspect the Repository

Before writing code:
1. Read all relevant project files.
2. Identify:
   - existing backend
   - existing frontend
   - database code
   - environment/configuration files
   - tests
   - documentation
   - partially implemented features
3. Run all existing tests/build checks.
4. Produce a short status report in:  
   `docs/current_status.md`

The report must contain:
- Existing components
- Working components
- Broken components
- Missing components
- Technical risks
- Recommended next implementation step

*Do not start by rewriting the project from scratch.*

---

## 5. Phase 1 — Data Feasibility Spike

This is the most important first engineering task. Before building a polished UI, prove that the authoritative data path works.

Select approximately 5–10 representative Gainesville intersections. For each test case, investigate:
$$\text{map coordinate} \to \text{nearby intersection} \to \text{confirmed intersection} \to \text{FDOT/Gainesville traffic site} \to \text{authoritative measurement} \to \text{semantic validation} \to \text{provenance}$$

Create:  
`docs/data_feasibility.md`

Document:
- exact FDOT endpoint/service/layer
- exact Gainesville endpoint/service/dataset
- endpoint URLs or service identifiers
- response format
- geometry fields
- traffic-site identifier fields
- measurement fields
- date/time fields
- hourly-data availability
- AADT availability
- rate limits if known
- authentication requirements if any
- pagination requirements
- provider limitations
- how sites can be defensibly associated with intersections
- examples of successful and unsuccessful locations

**Important:** Do not assume that because FDOT exposes an intersection layer, it also exposes historical hourly volume in the same service. If hourly data is only partially available, document that. The prototype should support an authoritative result when available OR a clear no-data response when unavailable.

---

## 6. Repository Structure

Use or adapt the repository toward this organization:

```text
transgis/
├── README.md
├── ANTIGRAVITY_BUILD_INSTRUCTIONS_TRANSGIS.md
├── HANDOVER.md
├── .env.example
├── docker-compose.yml
├── docs/
│   ├── current_status.md
│   ├── architecture.md
│   ├── data_feasibility.md
│   ├── data_dictionary.md
│   ├── api.md
│   ├── evaluation.md
│   └── user_manual.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   ├── agents/
│   │   ├── data/
│   │   ├── gis/
│   │   ├── services/
│   │   └── rag/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── types.ts
│   └── tests/
└── scripts/
```

*Do not create empty files just to match this structure. Create files only when they serve a real implementation purpose.*

---

## 7. Database Design

Create a PostGIS-backed normalized model.

### `intersections`
- `intersection_id`
- `road_1`
- `road_2`
- `latitude`
- `longitude`
- `geometry`
- `source`
- `source_feature_id`
- `source_url`
- `updated_at`

### `traffic_sites`
- `site_id`
- `road_name`
- `latitude`
- `longitude`
- `geometry`
- `source`
- `source_feature_id`
- `source_url`
- `site_metadata`
- `updated_at`

### `traffic_volume`
- `id`
- `site_id`
- `observation_date`
- `observation_hour`
- `volume`
- `measurement_type`
- `direction`
- `source`
- `source_record_id`
- `source_url`
- `retrieved_at`

### `roadways`
- `road_id`
- `road_name`
- `geometry`
- `aadt`
- `aadt_year`
- `source`
- `source_feature_id`
- `source_url`

### `signals`
- `signal_id`
- `signal_type`
- `latitude`
- `longitude`
- `geometry`
- `source`
- `source_feature_id`
- `source_url`

*Use the actual source fields discovered during the feasibility phase. Do not force provider data into incorrect meanings.*

---

## 8. Spatial Operations

Implement deterministic spatial logic in backend/PostGIS. Expected operations include:
- `ST_DWithin`
- `ST_Distance`
- `ST_Intersects`
- `ST_Buffer`
- Nearest-neighbor ordering
- Point-in-polygon
- CRS transformations (EPSG:26917 to EPSG:4326)

Default configurable search distances:
- **Intersection search radius:** 150 m (or 250 m buffer)
- **Traffic-site search radius:** 250 m (or 500 m corridor)

*These must be environment/configuration values, not scattered magic numbers.*

---

## 9. Data Source Adapters

Keep provider-specific code isolated:
- `backend/app/data/fdot_client.py`
- `backend/app/data/gainesville_client.py`

Each adapter should:
- Call the official provider;
- Handle provider-specific parameters;
- Handle pagination;
- Handle errors/timeouts;
- Normalize the response;
- Attach provenance;
- Never leak raw provider-specific structure into the frontend.

---

## 10. Agent Tools

The LLM must interact through narrow backend tools:

1. `find_location`: Convert address to coordinates.
2. `find_nearby_intersections`: Return candidate intersections sorted by defensible proximity. If multiple are plausible, return all candidates (do not silently choose).
3. `get_intersection_details`: Road names, coordinates, geometry, source, source ID.
4. `find_nearby_traffic_sites`: Candidate traffic sites with distance, source, road association, and metadata.
5. `get_available_data`: Return which authoritative measurements are available (hourly_volume, AADT, signals, etc.).
6. `get_traffic_volume`: Return status (`ok | no_data | ambiguous | unsupported`), measurement payload, provenance, and warnings.

---

## 11. Validation Layer

Implement a dedicated validation service (`validation_service.py`). Before returning a measurement verify:
- Provider is approved;
- Record is non-null;
- Units are known;
- Measurement type matches the user's request;
- Date/time matches the user's request;
- Location/site association is defensible;
- Year is known where required;
- Provenance exists.

Use typed statuses:
- `ok`
- `no_data`
- `ambiguous_location`
- `ambiguous_site`
- `unsupported_measurement`
- `invalid_time`
- `provider_error`
- `validation_failed`

---

## 12. NaviGator LLM Integration

- **Model:** `gpt-oss-20b`
- Read model and base URL from environment variables:
  ```env
  NAVIGATOR_TOOLKIT_API_KEY=sk-...
  NAVIGATOR_BASE_URL=https://api.ai.it.ufl.edu/v1
  NAVIGATOR_MODEL=gpt-oss-20b
  ```
- **Agent Behavior:** The LLM understands user intent, extracts parameters, uses map context, calls backend tools, asks clarification if needed, and interprets validated results.
- **Strict Guardrail:** The LLM never answers numeric transportation facts from model memory. The backend is the authority.

---

## 13. Agent System Prompt

Implement a system prompt with behavior equivalent to:

> *"You are the TransGIS transportation infrastructure analysis agent.*  
> *You may only answer transportation measurement questions using results returned by approved TransGIS tools.*  
> *Never fabricate transportation values.*  
> *Never infer hourly traffic from AADT.*  
> *Never treat a nearby traffic site's value as an intersection total unless the tool result explicitly confirms that interpretation.*  
> *Use tools for geometry, location, intersection resolution, traffic-site selection, data retrieval, and validation.*  
> *If multiple intersections or sites are plausible, request clarification.*  
> *If authoritative data is not available, clearly say so.*  
> *Always preserve and communicate the data source."*

---

## 14. Backend API

Implement at minimum:
- `GET /health`
- `POST /api/chat` (or `/api/query`)
- `GET /api/geocode`
- `GET /api/intersections/nearby`
- `GET /api/intersections/{id}`
- `GET /api/data/sources`

Use Pydantic request/response schemas.

---

## 15. Frontend

Required UI:
- Gainesville map
- Address search
- Map click
- Selected coordinate marker
- Natural-language input
- Submit button
- Loading state
- Candidate intersection picker
- Selected intersection visualization
- Traffic-site marker
- Result panel
- Source/provenance panel
- No-data state
- Provider-error state

---

## 16. Map Actions

The backend may return map actions such as:
```json
[
  {
    "type": "highlight_intersection",
    "geometry": {}
  },
  {
    "type": "show_search_area",
    "geometry": {}
  },
  {
    "type": "show_traffic_site",
    "latitude": 0.0,
    "longitude": 0.0
  }
]
```

---

## 17. Optional RAG

- Only for documentation, data dictionaries, metadata, field definitions, and source descriptions.
- Use `nomic-embed-text-v1.5` + `pgvector`.
- **Never use RAG output as authoritative traffic measurement data.**

---

## 18. Environment File

Maintain `.env.example` with clear documentation of required variables:
```env
DATABASE_URL=postgresql://transportation_app:change_me@localhost:5432/transportation
NAVIGATOR_TOOLKIT_API_KEY=your_key_here
NAVIGATOR_BASE_URL=https://api.ai.it.ufl.edu/v1
NAVIGATOR_MODEL=gpt-oss-20b
DEFAULT_INTERSECTION_RADIUS_M=150
DEFAULT_TRAFFIC_SITE_RADIUS_M=250
FRONTEND_ORIGIN=http://localhost:5173
```

---

## 19. Docker

Provide Docker Compose configuration for:
1. `db`: PostGIS (`postgis/postgis:16-3.4`)
2. `backend`: FastAPI Python 3.12 slim
3. `frontend`: Node 20 build + Nginx reverse proxy

---

## 20. Testing & Behavioral Scenarios

Required test scenarios:
1. Exactly one nearby intersection.
2. Multiple nearby intersections (ambiguity).
3. No nearby intersection.
4. Valid authoritative traffic record.
5. No hourly record exists.
6. AADT exists but hourly volume requested.
7. Nearby traffic site exists but relationship cannot be validated.
8. Provider unavailable (resilience/fallback).
9. Invalid time request.
10. Missing location.
11. Successful provenance display.
12. Natural-language agent selects the correct backend tool.

---

## 21. Evaluation

Create `docs/evaluation.md` evaluating:
- Intersection identification correctness
- Ambiguity handling
- Tool selection
- Authoritative-source adherence
- Measurement semantic correctness
- No-data correctness
- Provenance completeness
- End-to-end task success
- Latency

---

## 22. Implementation Order

- **Stage A — Inspect**: Inspect repository, run tests, write `docs/current_status.md`.
- **Stage B — Data Feasibility**: Verify FDOT/Gainesville live sources, test 5–10 intersections, write `docs/data_feasibility.md`.
- **Stage C — Database**: PostgreSQL/PostGIS schemas, ingest/cache spatial data, spatial queries.
- **Stage D — Data Providers**: FDOT adapter, Gainesville adapter, normalization, provenance.
- **Stage E — Deterministic Tools**: Location, intersection search, intersection details, traffic sites, available data, traffic query, validation.
- **Stage F — Minimum Vertical Slice**: Build coordinate -> intersection -> data -> validation -> provenance before LLM.
- **Stage G — Agent**: Connect `gpt-oss-20b`, define tool schemas, ambiguity/no-data handling.
- **Stage H — Frontend**: Map, address/click, query, clarification, result, provenance.
- **Stage I — Optional RAG**: Documentation search only if needed.
- **Stage J — Final Evaluation**: Execute fixed test set, document limitations.
- **Stage K — Documentation**: README, architecture, API docs, data dictionary, user manual.

---

## 23. Definition of Done

The project is complete when:
- Application starts from documented instructions;
- PostGIS database works;
- User can click map or search location;
- Nearby intersection can be identified;
- Ambiguity is handled;
- Authoritative FDOT/Gainesville data can be queried;
- Measurement semantics are validated;
- No-data is handled correctly;
- `gpt-oss-20b` can orchestrate tools;
- Source/provenance is displayed;
- Map shows relevant geometry/site;
- Representative tests pass;
- Evaluation results are documented;
- README and user manual are complete;
- No unsupported traffic value is fabricated.

---

## 24. Primary Demo

**Location:** Gainesville intersection with known authoritative coverage.  
**Prompt:** *"What was the traffic volume at this intersection between 5 PM and 6 PM?"*  
**Expected Behavior:**  
Selected coordinate -> nearby intersections -> clarification if needed -> confirmed intersection -> candidate traffic sites -> validate association -> retrieve temporal measurement -> validate semantics -> return value + source -> show map result.  
*If no hourly record exists:* Return clean no-data message explaining that no authoritative hourly traffic volume was found for the requested time. That is a successful, honest response.

---

## 25. Success Principle

$$\text{Data correctness} > \text{Provenance} > \text{Deterministic GIS behavior} > \text{Agent reliability} > \text{UI polish}$$

A visually impressive prototype that invents traffic data is a failed project.  
A simple prototype that correctly finds, validates, cites, and explains authoritative transportation data—or correctly reports that no data exists—is a successful project.
