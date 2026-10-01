# Conflation Labeling Guide

## Overview
This guide defines the standard operating procedure for a human reviewer manually assessing candidate matches between source transportation records (FDOT, City of Gainesville) and the canonical TransGIS/OSM topological backbone.

## Classification Categories

### 1. MATCH (or EDGE_MATCH / NODE_MATCH)
- **Definition:** The source record unambiguously refers to the canonical entity.
- **Criteria for Edge:** A traffic count or AADT segment physically aligns with the OSM roadway, and the street names / route aliases conceptually match the same facility.
- **Criteria for Node:** An intersection record (or traffic signal) physically aligns with an OSM node connecting the correctly named crossing streets.

### 2. MULTI_EDGE_MATCH
- **Definition:** A single source record (e.g., an FDOT AADT LineString or a point on a divided highway) legitimately corresponds to multiple topological edges in the canonical network.
- **Criteria:** The source line spans across an intersection (thus covering two canonical edges), or the roadway is mapped as a dual-carriageway (divided highway) in OSM, and the source record explicitly represents both directions combined.

### 3. AMBIGUOUS
- **Definition:** The source record could plausibly map to multiple distinct facilities, or the names contradict the spatial geometry.
- **Criteria:** Example: A Gainesville point labeled "NW 13TH ST" that physically falls exactly on "NW 6TH ST" with no clear way to resolve the discrepancy without external context.
- **Action:** Mark as AMBIGUOUS and include notes. Do not force a match.

### 4. NO_MATCH (NON_MATCH)
- **Definition:** The source entity is missing from the canonical topology.
- **Criteria:** Off-ramps, unmapped private roads, or newly constructed roads not yet present in the OSM snapshot. Also applies to hard negatives (e.g., candidate is parallel street but not the requested street).

## Procedure
1. Verify the `source_geometry` against the candidate's canonical geometry on a map.
2. Verify the `raw_source_name` against the candidate's `normalized_name` or `route_refs`.
3. Account for divided highway semantics: if the source data dictionary implies a bidirectional count, and OSM has two one-way edges, use `MULTI_EDGE_MATCH`.
4. Enter the final classification and evidence notes.
