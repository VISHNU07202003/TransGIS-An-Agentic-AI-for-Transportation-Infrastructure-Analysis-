# Agent Error Analysis

## 1. Overview
This document analyzes the primary error categories discovered across the A/B/C agent experiment runs (720 total runs).

## 2. Failure Taxonomy

### A. Wrong Source (Most Common System A Failure)
- **Description:** System A relies on raw provider APIs. It frequently retrieved an intersection from the City of Gainesville when asked about a State Route, failing to query the FDOT dataset because it lacked cross-provider normalized search tools. 
- **Impact:** Failed entity grounding and provenance.

### B. Wrong Measurement Semantics (Most Common System B Failure)
- **Description:** System B has powerful spatial search tools and successfully retrieved both FDOT and Gainesville records near a location. However, it dynamically added the FDOT bidirectional AADT to the Gainesville one-way AM-peak count, inventing a statistically invalid number.
- **Impact:** Strict numeric-grounding violation. System B failed to correctly reconcile divided highway semantics on the fly.

### C. Missed Clarification (Most Common System C Failure)
- **Description:** System C queried the canonical layer and encountered a node with an `AMBIGUOUS` flag (due to the ER ambiguity margin policy). Instead of returning a correct refusal or asking the user for clarification, the LLM attempted to guess the user's intent and picked one of the ambiguous edges.
- **Impact:** Forced match penalty. While the ER layer successfully caught the ambiguity, the agent failed to leverage the ambiguity signal correctly.

### D. Hallucinated Number
- **Description:** When spatial queries returned empty (e.g., searching a new subdivision), Systems A and B sometimes attempted to estimate traffic volume based on road classification instead of returning a strict no-data refusal.
- **Impact:** System C largely mitigated this because canonical entities are strictly typed; if `observations` is empty, the agent confidently reports no data.
