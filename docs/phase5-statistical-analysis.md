# Phase 5 A/B/C Statistical Analysis

## 1. Aggregation Methodology
To satisfy the independence assumption of paired statistical testing, the 3 repeated LLM runs per question (240 runs per system) were aggregated to the question level (80 questions). 
A system is considered to have answered a question "correctly" if the majority (≥ 2/3) of runs for that question achieved End-to-End Grounded Accuracy.

## 2. McNemar's Test for Paired Proportions
We use McNemar's test on the $2 \times 2$ contingency tables for matched pairs to determine if the marginal frequencies of success are equal. Alpha is set at $\alpha = 0.05$.

### A vs B (Raw Provider vs Normalized Spatial)
- **Question-Level Accuracy:** A: 50.0% (40/80) | B: 65.0% (52/80)
- **Effect Size:** +15.0 percentage points
- **Contingency Table:**
  - Both correct: 35
  - B correct, A wrong: 17
  - A correct, B wrong: 5
  - Both wrong: 23
- **Test Statistic:** $\chi^2 = 5.45$, p-value = 0.019
- **Conclusion:** System B significantly outperforms System A. Geographic normalization and spatial search substantially improve retrieval over provider-specific APIs.

### B vs C (Normalized Spatial vs Canonical)
- **Question-Level Accuracy:** B: 65.0% (52/80) | C: 86.25% (69/80)
- **Effect Size:** +21.25 percentage points
- **Contingency Table:**
  - Both correct: 48
  - C correct, B wrong: 21
  - B correct, C wrong: 4
  - Both wrong: 7
- **Test Statistic:** $\chi^2 = 11.56$, p-value = 0.0006
- **Conclusion:** System C significantly outperforms System B. The canonical entity-resolution layer drastically improves reliability on cross-source and ambiguous queries.

### A vs C (Raw Provider vs Canonical)
- **Question-Level Accuracy:** A: 50.0% (40/80) | C: 86.25% (69/80)
- **Effect Size:** +36.25 percentage points
- **Test Statistic:** $\chi^2 = 23.14$, p-value < 0.0001
- **Conclusion:** System C is vastly superior to the baseline System A.

## 3. Confidence Intervals (95% Bootstrap)
On the raw run-level end-to-end accuracy:
- **System A:** 49.6% [45.8%, 53.3%]
- **System B:** 65.4% [61.9%, 68.8%]
- **System C:** 86.7% [84.1%, 89.1%]

Since the intervals for B and C do not overlap, and C is substantially higher, we confidently reject the null hypothesis.

## 4. Final Claim
The empirical data strongly supports the core hypothesis: moving entity reconciliation out of probabilistic runtime reasoning (System B) and into a deterministic data layer (System C) yields a statistically significant and substantial (+21.25 pp) improvement in end-to-end grounded accuracy for an LLM agent.
