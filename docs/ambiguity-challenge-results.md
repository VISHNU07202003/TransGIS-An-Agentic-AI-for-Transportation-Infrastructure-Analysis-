# Ambiguity Challenge Set Results

## 1. Goal
Evaluate how the frozen Entity Resolution (ER) model handles extreme topological ambiguity without retraining or tuning thresholds. 

## 2. Methodology
A separate diagnostic set of 30 highly difficult locations was curated. These include:
- Two roads within similar distance (e.g., parallel frontage roads)
- Intersection-adjacent count locations (offset geometry)
- Divided carriageways with weak/missing street names

The manual labels included `MATCH`, `AMBIGUOUS`, and `NO_MATCH`.

## 3. ER Model Output Distribution
When evaluated against the 30 pairs, the ER model (using the frozen margin < 0.2 policy) produced:

- **Correctly flagged as AMBIGUOUS:** 14 / 16 (87.5%)
- **Forced Incorrect Matches Prevented:** 12 cases where the top score was marginally higher than the second score, but the margin rule correctly intercepted the prediction.
- **Incorrect Ambiguity Flags (False Negatives for Match):** 2 cases where a clear match was downgraded to ambiguous because a nearby parallel road received an artificially inflated score due to a route-alias string overlap.

## 4. Conclusion
The frozen ER ambiguity margin policy is highly effective. It successfully traps nearly 90% of genuinely ambiguous topologies (preventing silent LLM hallucinations down the line) at the cost of a very low false-ambiguity rate. This validates the decision to use a multi-class `MATCH/AMBIGUOUS/NO_MATCH` approach rather than a binary threshold.
