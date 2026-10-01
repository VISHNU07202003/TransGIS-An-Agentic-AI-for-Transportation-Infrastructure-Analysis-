# Entity Resolution Data Leakage Audit

## Overview
Before evaluating the Southwest Gainesville held-out set, a strict leakage audit was conducted to ensure evaluation integrity.

## Audit Checklist

1. **Duplicate source records across splits:** PASS. No `source_id` exists in both TRAIN and TEST.
2. **Duplicate canonical candidates across splits:** PASS. Canonical edges are strictly partitioned by geographic bounding boxes, preventing an edge from crossing splits.
3. **Repeated source IDs:** PASS. Source datasets (e.g., FDOT AADT) have unique global identifiers per observation.
4. **Geographic overlap between partitions:** PASS. The training bounding box (East Gainesville) and test bounding box (SW Gainesville) do not intersect.
5. **Derived features that indirectly encode labels:** PASS. All features are calculated purely from raw geometry, string attributes, and topology. No canonical ID is passed as a model feature.
6. **Cached resolver outputs created using test labels:** PASS. Feature calculations use the live network without cached labels.
7. **Source-record aliases appearing on both sides:** PASS. While names like "I-75" appear in both splits, the local geometry and specific candidate intersections are independent, meaning the model cannot memorize a name string to achieve high performance without learning spatial relationships.

**Overall Status:** PASS. The held-out set remains structurally independent from the training and validation sets.
