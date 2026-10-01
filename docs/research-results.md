# Phase 5 Research Results

## Primary Metric: A/B/C Grounded Answer Accuracy
The following table summarizes the performance of the three LLM grounding architectures across 720 runs (80 independently verified queries x 3 runs/system).

| Category | System A (Raw Provider) | System B (Normalized PostGIS) | System C v1.0 (Canonical ER) |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | 49.6% | 65.4% | **86.7%** |
| Single-source | 86.1% | 88.9% | **94.4%** |
| Cross-source | 30.6% | 61.1% | **86.1%** |
| Ambiguous Topology | 16.7% | 33.3% | **91.7%** |
| Multi-step | 42.4% | **75.8%** | 72.7% |
| Adversarial / Edge-cases | 27.3% | 42.4% | **84.8%** |

## Secondary Metrics & Guardrails

| Metric | System A | System B | System C v1.0 |
| :--- | :---: | :---: | :---: |
| Entity-Selection Accuracy | 64.2% | 75.0% | **90.8%** |
| Provenance Correctness | 71.3% | 82.5% | **92.9%** |
| Hallucinated-Number Rate | 16.7% | 15.4% | **4.2%** |
| p50 Latency (ms) | 3965 | 3498 | **2755** |
| p95 Latency (ms) | 4871 | 4306 | **3533** |

## Statistical Significance
- **System C vs System B:** McNemar's test yields $p = 0.0006$. System C outperformed the normalized spatial baseline by **21.25 percentage points**.
- **Conclusion:** The canonical entity resolution layer significantly reduces hallucinations and numeric grounding violations on cross-source and topologically ambiguous queries.
