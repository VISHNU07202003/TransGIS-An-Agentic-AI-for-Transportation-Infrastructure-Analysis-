# Geographic Split for Conflation Testing

## 1. Overview
To ensure the machine learning entity resolver (to be developed in Phase 4) does not overfit to specific local topology patterns or naming conventions (like "University Ave"), the dataset is partitioned geographically. 

**Rule:** We do not randomly split individual point/line pairs. If neighboring intersections on the same street fall into both the training and test set, the model may simply memorize the street name instead of learning generalized spatial matching rules.

## 2. Partition Strategy

### A. Training Geography
- **Region:** East Gainesville (East of Main St), North Gainesville (North of NW 39th Ave), and Alachua County rural sectors (e.g., Waldo, Hawthorne).
- **Approximate Record Share:** ~60% of available source records.
- **Reasoning:** Provides a mix of dense grid topologies, rural highways, and standard state roads (e.g., Waldo Rd, SR 20).

### B. Validation Geography
- **Region:** NW Gainesville (between Main St and NW 43rd St, North of University Ave)
- **Approximate Record Share:** ~20% of available source records.
- **Reasoning:** Contains dense residential collector roads and major divided arterials (e.g., NW 13th St / US 441, NW 39th Ave) for hyperparameter tuning.

### C. Held-Out Test Geography
- **Region:** Southwest Gainesville (South of University Ave, West of Main St), explicitly including the University of Florida Campus, Shands Hospital complex, and the I-75 / Archer Road interchange.
- **Approximate Record Share:** ~20% of available source records.
- **Reasoning:** This is the most complex topological zone in the county. It features high density, heavy divided highways, dense overlapping aliases (SR 24 vs Archer Rd vs Waldo Rd), service roads, and highly irregular campus street grids. If the model generalizes well to this held-out set, it is robust.

## 3. Enforcement
These bounding boxes will be strictly enforced during the dataset generation pipeline before any models are fitted.
