# A/B/C Experiment Protocol

## 1. Hypothesis
Grounding an LLM agent (`gpt-oss-20b`) in a precomputed, canonical geospatial entity layer (System C) improves end-to-end transportation-query reliability and factual correctness compared to querying heterogeneous transportation records dynamically via normalized spatial tools (System B) or raw provider tools (System A), specifically in cross-source and high-ambiguity topologies.

**Note:** A mixed result (e.g., C improves cross-source but not single-source) or a null result (B performs identically to C) is acceptable and will not result in hypothesis modification.

## 2. Systems
- **System A (Raw Provider):** `gpt-oss-20b` + Provider-specific APIs (e.g., FDOT REST, Gainesville Socrata). No canonical IDs or normalized spatial search.
- **System B (Normalized PostGIS):** `gpt-oss-20b` + Normalized spatial/textual search tools. Must dynamically reconcile overlapping records at query time. No precomputed canonical links.
- **System C (TransGIS Canonical):** `gpt-oss-20b` + Frozen ER Canonical Layer. Retrieves pre-associated multi-provider observations for canonical nodes/edges.

## 3. Metrics
- **Primary Metric:** **End-to-End Grounded Accuracy (%)**. A run is correct only if the location is correct, fact is accurate, unit is correct, provenance traces to real data, and no unsupported arithmetic occurred.
- **Secondary Metrics:**
  - Entity-selection accuracy (Did it find the right place?)
  - Factual answer accuracy (Is the number right?)
  - Correct-refusal / no-data rate
  - Hallucinated-number rate
  - Provenance correctness
  - Tool-selection / Argument accuracy
  - Latency (p50, p95)

## 4. Evaluation Procedure
- **Questions:** 80 independently verified, manually gold-labeled questions.
- **Repeated Runs:** 3 runs per question per system to account for non-deterministic generation (total 240 runs per system).
- **Verifiers:** Automated strict numeric and provenance verifiers.
- **Statistical Analysis:** Question-level aggregation. Paired comparison using McNemar's test (System C vs B, System C vs A) with $\alpha = 0.05$.
- **Failure Handling:** LLM timeouts or structural tool failures count as incorrect for that run.
