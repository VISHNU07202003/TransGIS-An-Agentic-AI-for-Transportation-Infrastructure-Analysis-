# Entity Resolution Error Analysis

## 1. Overview
This document analyzes the primary error categories discovered during Phase 4 matching evaluation across baselines (Distance, Rules) and the Logistic Regression (LR) model.

## 2. Point → Edge Errors
### A. Route Alias Failure
- **Description:** A local traffic point (e.g., "SW 13TH ST") matches a canonical edge labeled solely with a state route ID ("US 441") or vice versa.
- **Impact:** Distance-only succeeds if close, but rule-based and LR models strongly penalize the name mismatch.
- **Resolution:** Adding `ROUTE_ALIASES` normalizer improved LR recall, but highly obscure local aliases still fail.

### B. Geometry Offset (Intersection Ambiguity)
- **Description:** A point is placed 5 meters from an intersection. The distance feature is nearly identical for the true edge and the cross-street edge.
- **Impact:** LR struggles to separate if name agreement is weak on both.
- **Resolution:** Introducing the `source_point_to_edge_position` feature helped the model learn that points snapped exactly to `0.0` or `1.0` position are highly ambiguous without strong name evidence.

### C. Missing OSM Feature (Hard Negatives)
- **Description:** Unmapped service roads or new developments. The algorithm finds the *next closest* road, which is physically wrong.
- **Impact:** False positives if distance threshold is too loose.
- **Resolution:** LR learned to confidently reject matches when distance > 15m AND name agreement < 0.3.

## 3. Line → Edge Errors
### A. Divided Roadway Alignment
- **Description:** FDOT line drawn directly down the median. Both northbound and southbound OSM carriageways overlap equally.
- **Impact:** A simple `argmax` matcher picks only one side, failing complete-segment accuracy.
- **Resolution:** Transitioning to the `feature_association_group` 1-to-N architecture correctly captures both carriageways.

### B. Segment Fragmentation
- **Description:** One FDOT segment overlaps 6 tiny OSM edges (due to cross-streets splitting the OSM ways).
- **Impact:** Network continuity errors if a gap occurs.
- **Resolution:** Enforcing `network_continuity` features allows the cluster to chain the overlapping edges confidently.

## 4. Most Important Remaining Risk
**Ambiguous Topology:** High-density downtown areas where overlapping route designations and service roads crowd the 10-meter search radius, making the spatial signal incredibly noisy. The ambiguity policy (margin < 0.2) correctly traps most of these, but they require manual review.
