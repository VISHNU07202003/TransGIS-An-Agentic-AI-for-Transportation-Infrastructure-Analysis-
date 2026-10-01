# Logistic Regression Feature Analysis

## Learned Coefficients

The Point→Edge Logistic Regression matcher learned the following standardized coefficients:

- `perpendicular_distance_m`: **-0.237**
  - *Sign:* Negative.
  - *Interpretation:* As distance increases, the probability of a match decreases. This is expected.
- `normalized_name_similarity`: **+0.069**
  - *Sign:* Positive.
  - *Interpretation:* Higher Jaro-Winkler string similarity strongly pulls the prediction toward a MATCH.
- `route_reference_match`: **+0.028**
  - *Sign:* Positive.
  - *Interpretation:* A boolean match on route aliases (e.g. "SR 26") increases match likelihood, useful for state roads lacking local names.
- `orientation_difference`: **-0.830**
  - *Sign:* Negative.
  - *Interpretation:* The absolute angular difference between the source feature bearing and the candidate edge bearing heavily penalizes matches if they are perpendicular (e.g., cross streets).

## Feature Ablation (Impact on Validation F1)
- **Distance Only:** 0.973
- **Rules (Distance + Name Logic):** 1.000
- **Logistic Regression (Full Feature Set):** 1.000

The primary value of the Logistic Regression model is in cleanly rejecting false candidates that happen to be physically closer (e.g., within 5 meters) but have the wrong name or orientation, which distance-only matching inevitably selects.
