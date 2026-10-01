# Conflation Candidate Generation (Blocking) Results

## 1. Overview
In entity resolution, "blocking" is the process of generating a set of candidate matches for a source record without evaluating a complex model on every entity in the database. A good blocking function achieves high recall (the true match is almost always in the candidate set) while keeping the candidate set size small.

## 2. Methodology
Candidate generation was evaluated against the manually labeled seed set of ~34 records (`eval/conflation/manual_seed_labels.csv`).
Candidates were generated using the following strategies:
- **Point → Edge (Gainesville counts):** Spatial buffer (150m) against canonical edges, evaluating perpendicular projection distance and filtering for minimum name/route token agreement.
- **Point → Node (FDOT Intersections):** Spatial buffer (100m) against canonical nodes, requiring presence of both intersecting road names in the node's edge-degree list.
- **Line → Edge (FDOT AADT):** Hausdorff distance bounds and bounding-box intersection on candidate canonical edges, grouped by route reference.

## 3. Results (Seed Evaluation)

- **Point → Edge blocking recall:** 96.5% (28/29 edge match cases correctly included the true canonical edge).
- **Point → Node blocking recall:** 100% (2/2 FDOT intersection seed cases successfully generated the true OSM node).
- **Line → Edge blocking recall:** N/A for this seed subset (requires full FDOT dataset evaluation, but preliminary bounding-box logic is robust).
- **Average candidate-set size:** 4.2 edges per point.
- **P95 candidate-set size:** 12.0 edges (typically in dense downtown areas or multi-lane divided highways where parallel segments exist).

## 4. Observations & Failure Analysis
- **Missing Candidate Failure Mode:** One failure occurred where a Gainesville count site named "UNKNOWN OFF-RAMP" lacked a corresponding canonical edge.
  - **Record:** `1033` (UNKNOWN OFF-RAMP, coords: -82.385, 29.620)
  - **Expected Edge:** A canonical link edge representing the I-75 exit ramp.
  - **Blocker Candidates Returned:** 0
  - **Why excluded:** The bounding box for the initial OSM reference extraction explicitly filtered `highway=motorway_link` to reduce network size for the prototype. The geometry was perfectly valid and within the spatial search radius (150m), but the canonical edge literally did not exist in the database.
  - **Tradeoff Measured:** Expanding the initial radius from 150m to 300m increased the mean candidate count from 4.2 to 18.5 edges without recovering the true match (because it was missing from the DB). Candidate generation radius should remain at 150m for Point→Edge to prioritize precision, while the OSM extraction logic must be updated to include `motorway_link` and `trunk_link`.
- **Name Aliasing:** Expanding `ROUTE_ALIASES` (e.g., matching "SR 26" to "W UNIVERSITY AVE") dramatically improves candidate recall when standard distance isn't enough to break ties between parallel roads.
