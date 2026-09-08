# Agentic AI System for Transportation Infrastructure Analysis

> **A Gainesville-focused agentic AI prototype that lets users ask natural-language questions about urban intersections through an address or map click, uses controlled GIS/database tools to identify and query relevant FDOT and City of Gainesville transportation data, validates the result, and presents the answer with spatial context and source provenance.**

## Architecture

```text
                         USER
                           |
              +------------+------------+
              |                         |
        Address Input               Map Click
              |                         |
              +------------+------------+
                           v
                    Frontend / Map UI
                           |
                           v
                     FastAPI Backend
                           |
                           v
                      LLM Agent
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
      Geocoding      Intersection      Data/GIS Tools
                         Search              |
           |               |                |
           +---------------+----------------+
                           |
                           v
                    PostgreSQL + PostGIS
                           |
                +----------+----------+
                |                     |
                v                     v
              FDOT               Gainesville
          official GIS/API      official open data
                |                     |
                +----------+----------+
                           |
                           v
                      Validation
                           |
                           v
                         LLM
                           |
                           v
                 Answer + Provenance
                           |
                           v
                     Interactive Map
```

> **FDOT/Gainesville → FastAPI → PostgreSQL/PostGIS → Agentic LLM → Map + Verified Answer**

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + MapLibre GL JS |
| Backend | Python + FastAPI |
| AI | UF NaviGator AI Toolkit (OpenAI-compatible API + function/tool calling) |
| Database | PostgreSQL + PostGIS |
| Spatial | PostGIS spatial indexes, buffer/distance queries, GeoJSON |
| HTTP Client | httpx (async) |
| Geocoding | Nominatim (OpenStreetMap) |
| Optional | pgvector for documentation/metadata semantic retrieval |

## Data Sources

| Source | Type | URL |
|---|---|---|
| FDOT RCI Intersections | ArcGIS FeatureServer | https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer |
| FDOT AADT | ArcGIS FeatureServer | (same as above, specific layer) |
| FDOT Traffic Monitoring | ArcGIS FeatureServer | (same as above, specific layer) |
| FDOT Traffic Signals | ArcGIS FeatureServer | https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/Traffic_Signal_Locations_TDA/FeatureServer |
| City of Gainesville Traffic Counts | Socrata Open Data | https://data.cityofgainesville.org/Community-Model/Traffic-Counts/pfc3-w5ih |

## Prerequisites

- **Docker Desktop** — for PostgreSQL/PostGIS container
- **Python 3.11+** — backend runtime
- **Node.js 20+** — frontend build
- **UF NaviGator API key** — for LLM agent functionality

## Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in your NaviGator API key and any other required values.
3. **Never commit `.env`** — it is gitignored.

## NaviGator Setup

1. Sign in at https://api.ai.it.ufl.edu/ui using UF credentials.
2. Create a personal API key with a clear name (e.g., `agentic-transportation-prototype`).
3. Select a model that supports function/tool calling.
4. Add the key to your `.env` file as `NAVIGATOR_TOOLKIT_API_KEY`.

See: https://docs.ai.it.ufl.edu/docs/navigator_toolkit/getting_started/quickstart/

## Database Setup

```bash
# Start PostGIS container
docker compose up -d db

# Verify PostGIS is running
docker exec -it transportation-postgis psql -U transportation_app -d transportation -c "SELECT PostGIS_Full_Version();"
```

The database schema and seed data are automatically applied on first start via init scripts in `database/init/`.

## Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at http://localhost:5173 and proxies API requests to `http://localhost:8000`.

## Run Commands Summary

| Command | Description |
|---|---|
| `docker compose up -d db` | Start database |
| `cd backend && uvicorn app.main:app --reload` | Start backend |
| `cd frontend && npm run dev` | Start frontend |
| `cd backend && pytest -v` | Run tests |
| `python scripts/discover_fdot_layers.py` | Discover FDOT layer IDs |
| `python scripts/inspect_gainesville_dataset.py` | Inspect Gainesville dataset |

## Test Commands

```bash
cd backend
pytest -v
pytest tests/test_health.py -v
pytest tests/test_spatial.py -v
```

## Example User Questions

- "What was the traffic volume from 5 PM to 6 PM here?"
- "What is the traffic volume at this intersection?"
- "What is the AADT on the nearby roadway?"
- "Is this intersection signalized?"
- "What transportation information is available here?"

## Limitations

This is a graduate research prototype. The following are **explicitly out of scope**:

- Traffic prediction or forecasting
- Traffic-signal optimization or control
- Reinforcement learning
- V2X communication
- Autonomous vehicle integration
- Digital twin simulation
- IoT sensor deployment
- Computer vision analysis
- Truck-specific volume analysis
- Real-time traffic control
- Broad statewide multi-agency integration

The application should not be treated as a live traffic-control system or an authoritative substitute for agency engineering analysis.

## Source Links

- **NaviGator AI Toolkit**: https://docs.ai.it.ufl.edu/docs/navigator_toolkit/intro/
- **FDOT GIS Traffic Data**: https://www.fdot.gov/statistics/gis/default.shtm
- **FDOT RCI FeatureServer**: https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer
- **Gainesville Traffic Counts**: https://data.cityofgainesville.org/Community-Model/Traffic-Counts/pfc3-w5ih
- **PostGIS Documentation**: https://postgis.net/docs/

## License

MIT
