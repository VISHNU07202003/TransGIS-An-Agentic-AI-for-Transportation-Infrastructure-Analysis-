# TransGIS: Final Project Report

## Executive Summary
I built TransGIS, a geospatial transportation-data platform that reconciles heterogeneous FDOT and City of Gainesville records into stable canonical network entities. I evaluated distance-only, deterministic, and learned entity-resolution methods; introduced constrained clustering to prevent transitive false merges; preserved source-level provenance; built crash-safe staged ingestion; and compared three LLM grounding architectures across 720 runs. 

The canonical architecture improved grounded answer accuracy from 65.4% to 86.7% over normalized spatial tools in a controlled experiment, with the largest gains on cross-source and ambiguous queries. I then productionized it with hard ambiguity, numeric-grounding, and provenance gates, reaching 94.5% on the v1.1 regression suite.

## The Core Concept
*The canonical layer did not make the LLM inherently smarter; it moved entity identity and measurement semantics from probabilistic runtime reasoning into an evaluated deterministic data layer.*

## Key Architectural Deliverables
1. **Entity Resolution (ER) Pipeline:** Engineered a multi-modal spatial/semantic feature pipeline evaluating distances in `EPSG:6440` (NAD83 2011 / FL North). Implemented a Logistic Regression matcher that seamlessly filters parallel road false-positives that distance-only heuristics miss.
2. **Constrained Clustering:** Solved the "transitive trap" (A ≈ B ≈ C → A = C) inherent to spatial mapping by enforcing same-source and spatial-diameter constraints during union-find operations.
3. **Hard Verification Gates:** Productionized LLM output safety by intercepting tool calls. Unverified arithmetic is blocked, and ambiguous location queries force the backend to return a `CLARIFICATION_REQUIRED` UI payload, dropping the LLM hallucination rate to nearly 0%.
4. **Crash-Safe Ingestion:** Created a staging-to-published workflow utilizing SQL views and atomic transactional updates to guarantee no partial data is exposed during worker crashes.

## Limitations and Future Work
- **Geographic Scope:** The ER models and rules were tuned entirely within Alachua County (Gainesville). While robust locally, scaling to Miami-Dade or rural panhandle regions may require refitting the LR model.
- **Finite Labeled Dataset:** The evaluation was performed on an 80-question benchmark and a 250-pair ER dataset. Expanding to a larger, nationally diverse labeled dataset would strengthen calibration.
- **Complex Multi-Edge Cases:** Extreme line-to-network topologies (like the Archer Rd / I-75 braided interchange) remain exceptionally difficult to cluster completely without introducing false splits.
- **Model Latency:** End-to-end response times hover around 2.8 - 3.5 seconds, bound heavily by the LLM token generation speed. Streaming intermediate tool outputs to the UI could improve perceived latency.
- **Benchmark Specificity:** The 21.25 pp improvement in System C applies to the specific question distribution evaluated here. Domains with strictly clean, single-provider data may not require such a heavy canonical layer.
