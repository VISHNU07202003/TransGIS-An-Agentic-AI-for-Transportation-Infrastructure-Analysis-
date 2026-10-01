# OSM Reference Backbone

## 1. Overview
OpenStreetMap (OSM) serves as the topological backbone for the TransGIS canonical entity layer. Rather than treating FDOT or Gainesville as the topological baseline, TransGIS extracts intersection nodes and road edges from OSM, acting as a stable, high-fidelity spatial anchor.

## 2. Extraction Metadata
- **Extraction Date:** Seed extraction generated during Phase 2.
- **Geographic Bounding Region:** Alachua County, FL (focused primarily on Gainesville urban core for seed evaluation).
- **Bounding Box (approx):** West: -82.42, South: 29.58, East: -82.25, North: 29.72
- **OSM Snapshot:** Overpass API latest live data (as of extraction date).
- **Attribution & License:** © OpenStreetMap contributors, licensed under the Open Data Commons Open Database License (ODbL). 
- **Method:** Overpass API query fetching `highway=*`. To ensure all relevant transportation features are included while excluding unrelated topology (like indoor corridors or footways), the following tags are explicitly included:
  - `motorway`, `motorway_link` (Includes off-ramps like the missed seed case 1033)
  - `trunk`, `trunk_link`
  - `primary`, `primary_link`
  - `secondary`, `secondary_link`
  - `tertiary`, `tertiary_link`
  - `residential`
  - `unclassified`
  - `service` (where relevant for access roads that may have count stations)
  These are parsed into canonical network objects.

## 3. Data Model Mapping
- **OSM Node -> `canonical_node`:** Intersection nodes (nodes shared by >1 routable way).
- **OSM Way -> `canonical_edge`:** Road segments connecting two intersection nodes. Segments are split at intersections to form a clean graph.
- **Street Names:** `name`, `alt_name`, `ref` tags extracted and stored in `canonical_edge.normalized_name` and `route_refs`.

## 4. Stability and Provenance Rule
**Live OSM IDs are explicitly NOT used as TransGIS canonical IDs.**
OSM IDs change as users split, merge, or delete geometries. TransGIS generates its own stable IDs (e.g., `GNV-NODE-001`, `GNV-EDGE-010`) using a hash of the node coordinates and topological relationships, insulating the canonical layer from upstream OSM edits while maintaining spatial parity.

**However, OSM IDs are preserved for lineage.**
We do not discard OSM identifiers. The original `osm_node_id`, `osm_way_id`, version, extraction date, and raw tags are explicitly preserved inside the `source_features` layer. This ensures the canonical network can always be audited, traced, and rebuilt from the original source material.
