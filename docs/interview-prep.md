# SDE Interview Preparation Guide

When discussing TransGIS in a software engineering interview, focus on the **architectural decisions**, **data engineering**, and **rigorous evaluation**, rather than just the LLM prompt.

## 1. Entity-Resolution Design
**The Problem:** FDOT represents roads as linear strings (lines) representing bidirectional traffic. The City of Gainesville represents intersections as points. OpenStreetMap is a topological graph of nodes and one-way edges.
**The Solution:** I built an ER layer to map these onto the OSM backbone.
- *Point-to-Edge/Node:* Handled using perpendicular distance, Jaro-Winkler name similarity, and route alias matching.
- *Line-to-Edge:* Handled using Fréchet/Hausdorff distance bounds, overlap coverage ratios, and bearing orientations.
- *One-to-Many Schema:* Divided highways in OSM are two edges, but FDOT represents them as one. I designed `feature_association_groups` to map one FDOT record to $N$ canonical edges to prevent double-counting observation totals.

## 2. Constrained Clustering
**The Problem:** Naive Union-Find algorithms suffer from transitive false merges (e.g., A overlaps B, B overlaps C, so A merges with C, eventually collapsing parallel streets together).
**The Solution:** I implemented constrained clustering. Before a merge is accepted, the system validates constraints:
1. *Cannot-link:* Explicit geographic conflicts.
2. *Same-source conflict:* Two distinct FDOT segments cannot merge into the same canonical entity, preventing identical-source duplication.
- *Impact:* Dropped false merges from 12 to 0 on the evaluation set.

## 3. Database & Concurrency (Crash-Safe Ingestion)
**The Problem:** Updating spatial data across hundreds of thousands of rows risks leaving the production system with partial/corrupted data if the worker crashes.
**The Solution:** Implemented atomic data publishing.
- Ingested records go into a `datasets` table flagged as `STAGING`.
- The live agent queries a `live_source_records` SQL View filtered by `status = 'PUBLISHED'`.
- When ingestion finishes, a transaction demotes the old dataset to `ARCHIVED` and promotes the new one to `PUBLISHED`.
- *Result:* Idempotent retries, zero downtime, and no duplicate geometries.

## 4. The A/B/C Experiment
**The Narrative:** "I didn't just assume my architecture was better; I proved it by letting it lose."
- I built three systems: Raw APIs (A), Normalized PostGIS (B), and Canonical ER (C).
- *Result:* System C improved grounded answer accuracy by 21.25 percentage points over System B (p=0.0006). 
- *Nuance:* System B was highly competitive on single-source queries. The real value of the canonical layer was revealed during cross-source reconciliation and topological ambiguity (jumping from 33% to 92% accuracy).

**Core Takeaway Sentence:**
> *The canonical layer did not make the LLM inherently smarter; it moved entity identity and measurement semantics from probabilistic runtime reasoning into an evaluated deterministic data layer.*
