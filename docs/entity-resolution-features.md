# Entity Resolution Feature Specification

## 1. Overview
The entity resolution pipeline relies on engineered features that capture spatial, topological, and semantic relationships between source transportation observations and the canonical road network (OSM).

## 2. Point → Edge Features
Used to match point geometries (e.g., Gainesville Traffic Counts, signal assemblies) to canonical road segments.

### A. Spatial Features
- `perpendicular_distance_m`: The shortest 2D distance from the source point to the candidate LineString, projected into EPSG:6440 (meters).
- `source_point_to_edge_position`: A normalized float [0.0 - 1.0] indicating where along the edge the point projects (0 = start node, 1 = end node). Useful for detecting intersection-adjacent ambiguity.

### B. Semantic/Textual Features
- `normalized_name_similarity`: Jaro-Winkler string similarity between the normalized source road name and the canonical edge name [0.0 - 1.0].
- `road_name_token_jaccard`: Jaccard index of whitespace-tokenized name strings (e.g., "NW 13TH ST" vs "13TH ST").
- `route_reference_match`: Boolean (1.0 or 0.0). True if the source route alias (e.g., "SR 26") exists in the candidate's `route_refs` array.
- `directional_prefix_match`: Enum score. 1.0 if directional prefixes match ("W" vs "WEST"), 0.5 if one is missing, 0.0 if explicitly conflicting ("W" vs "EAST").

### C. Topological Features
- `highway_class_compatibility`: A lookup table score mapping the source data's implied hierarchy to OSM's `highway` tag (e.g., matching a high-volume AADT source to a `motorway` or `primary` rather than `residential`).

## 3. Line → Edge Features
Used to match linear geometries (e.g., FDOT AADT segments) to one or more canonical road segments.

### A. Spatial / Geometric
- `minimum_distance_m`: The shortest distance between the two lines.
- `mean_distance_m`: The average separation distance calculated by sampling points along the source line and projecting to the candidate edge.
- `hausdorff_distance`: The maximum of the shortest distances, identifying divergence.
- `overlap_length_m`: The length of the projection intersection along the canonical edge.
- `source_coverage_ratio`: `overlap_length_m` / `source_length_m`.
- `edge_coverage_ratio`: `overlap_length_m` / `candidate_length_m`.
- `orientation_difference`: The absolute angular difference [0-90 degrees] between the source segment bearing and candidate edge bearing.

### B. Semantic
- `normalized_name_similarity`: Same as Point→Edge.
- `route_reference_match`: Same as Point→Edge. Highly critical for state roadways.

### C. Topological
- `network_continuity`: Boolean. True if the candidate edge shares a node with another candidate edge already strongly matched to the same source LineString. Critical for multi-edge generation.
