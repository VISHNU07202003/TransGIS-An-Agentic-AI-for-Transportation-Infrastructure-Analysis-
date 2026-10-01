# Data Discovery Report

## 1. Overview
This report evaluates the viability of building an entity-resolution platform (TransGIS) based on the currently available transportation datasets from the Florida Department of Transportation (FDOT), the City of Gainesville, and OpenStreetMap (OSM) as a potential topology backbone. 

## 2. Investigated Datasets

### A. Florida Department of Transportation (FDOT)
- **Publisher:** FDOT
- **Official Service:** Roadway Characteristics Inventory (RCI)
- **Access Method:** ArcGIS REST API (FeatureServer)
- **Layers Evaluated:**
  - **RCI Intersections (Layer 6):** Point geometries (`EPSG:4326`). Stable identifier `OBJECTID`. Naming uses numerical `ROADWAY` identifiers (e.g., `26000000`) rather than human-readable street names. Statewide coverage. No measurements.
  - **AADT (Layer 0):** Line geometries representing roadway segments. Has `AADT` and `AADT_YEAR` fields.
  - **Traffic Signals TDA:** Point geometries indicating state-managed traffic signals.

### B. City of Gainesville
- **Publisher:** City of Gainesville Open Data (Socrata)
- **Datasets Evaluated:**
  - **TrafficData20140522 (`v2qq-gus2`):** Point geometries. Stable identifier `station`. Names use human-readable strings (`street`: "N MAIN ST", `block`: "900"). Contains `adt_2014`, `pkam_1314` (AM peak hourly), and `pkpm_1314` (PM peak hourly).
  - **Traffic Counts (`pfc3-w5ih`):** Similar schema to the above. Contains 463 records.
- **Coverage:** City of Gainesville only.

### C. OpenStreetMap (OSM)
- **Role:** Evaluated strictly as a topology/reference backbone.
- **Entity Type:** Network nodes (intersections) and ways (road segments).
- **Naming:** Highly detailed human-readable names ("West University Avenue").

## 3. Entity Resolution Viability

### Overlap Analysis: Traffic Monitoring Sites
- **FDOT AADT (Layer 0) vs. Gainesville TrafficData20140522:** 
  - **Observation:** Both FDOT and Gainesville measure traffic volume (AADT vs ADT/Peak counts) in Gainesville.
  - **Naming Discrepancy:** FDOT refers to "Main St" as `26000000` (Roadway ID). Gainesville refers to it as `street: "N MAIN ST", block: "900"`.
  - **Geometry Discrepancy:** FDOT places AADT on LineStrings (the roadway segment). Gainesville places counts on Points (the specific monitoring site).
  - **Conclusion:** There is significant conceptual overlap, but reconciling an FDOT line segment labeled `26000000` with a Gainesville point labeled `N MAIN ST` is a non-trivial entity-resolution problem requiring spatial snapping, blocking, and likely an OSM topological backbone to translate street names to state route numbers.

### Overlap Analysis: Intersections / Signals
- FDOT provides comprehensive state-managed intersections as Points. Gainesville does not expose a dedicated point-layer for purely *intersections*, but their traffic monitoring sites are geolocated at specific blocks/intersections.

## 4. GO / PIVOT / NO-GO Recommendation

**Recommendation: PIVOT**

**Reasoning:**
While there is valid overlap between FDOT and Gainesville traffic measurements, the schema mismatch is severe (Lines vs Points, State IDs vs Local Strings). Relying *only* on Gainesville Open Data and FDOT is insufficient to build a clean `intersection ↔ intersection` resolution pipeline without a third party.

**Pivot Strategy:**
We must incorporate OpenStreetMap (OSM) as the topology/reference backbone. By doing so, the entity-resolution pipeline becomes:
1. Extract canonical intersection nodes from OSM in Alachua County.
2. Snap FDOT RCI Points and Gainesville Traffic Count Points to the canonical OSM intersections.
3. Map FDOT's `ROADWAY` IDs to OSM's human-readable names using spatial overlay on OSM ways.

This creates a highly defensible and challenging entity-resolution problem suitable for the AI evaluation phase. Approximately 400+ Gainesville traffic sites can be spatially resolved against the FDOT network and OSM intersections.
