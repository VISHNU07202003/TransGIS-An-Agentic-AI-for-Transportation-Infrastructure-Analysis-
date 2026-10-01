# Divided Highway Semantics in Conflation

## 1. The Core Problem
OpenStreetMap (the topological backbone for TransGIS) frequently models divided highways (e.g., SW 34th St, US 441, I-75) as dual-carriageways: two parallel one-way `canonical_edges` separated by a median.
Conversely, FDOT AADT and many Gainesville historical traffic counts often treat the divided highway as a **single logical facility**, providing a single bidirectional measurement (e.g., AADT = 35,000 for both directions combined), mapped to a single centerline LineString or Point.

## 2. Geometric Snapping Failure
If a naive nearest-neighbor algorithm snaps an FDOT centerline (or a slightly offset Gainesville point) to the canonical network, it will arbitrarily snap to *one* of the two carriageways (e.g., the Northbound lanes). If the observation is then attached to that single edge, the system will incorrectly report that the Northbound lanes carry 35,000 vehicles, while the Southbound lanes have no data.

## 3. Data Dictionary Semantics
- **FDOT AADT (Layer 0):** FDOT's RCI documentation specifies that the `AADT` field represents the **two-way total volume** for the roadway segment. Directional splits are sometimes provided in the `DIR_AADT` (Directional AADT) or `K_FACTOR` fields, but the primary metric is bidirectional. Therefore, a single LineString with `AADT=35000` on US 441 applies to the entire facility.
- **Gainesville TrafficData20140522:** Contains explicit directional splits (`amd1_1314` and `amd2_1314` for AM Peak direction 1 and 2), but the `adt_2014` column represents the bi-directional total.
- **Rule:** Never infer traffic semantics from OSM geometry. The source field definition (e.g. `AADT` vs `DIR_AADT`) strictly dictates whether an observation is mapped to a bidirectional `feature_association_group` or a unidirectional single edge.

## 4. Resolution Strategy: One-to-Many Association
TransGIS solves this using the `feature_association_groups` schema:
1. **Spatial Candidate Grouping:** The candidate generator identifies parallel one-way edges that share the same `normalized_name` / `route_refs` and flow in opposite directions within a tight buffer of the source geometry.
2. **Multi-Edge Match:** The ER matcher creates an `association_group` and links *both* canonical edges to the single source feature.
3. **Observation Attachment:** The `observations` table links the AADT value to the `association_group_id`, *not* to the individual edges.
4. **Agent Resolution:** When the LLM agent asks "What is the AADT on the Northbound edge?", the data layer can look up the association group, see it represents a bidirectional observation, and return: "The combined two-way AADT for this highway is 35,000." This prevents double-counting or misleading the user.
