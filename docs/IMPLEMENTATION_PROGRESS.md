# Florida expansion and reliability work

Requested scope: statewide FDOT coverage with Gainesville supplemental records; richer grounded answers; defensible spatial relationships; offline CI and opt-in live checks; authentication/authorization, rate limits, durable shared caching, tracing, background jobs, circuit breakers, and schema monitoring.

Implementation order:
1. Audit current behavior and verify official datasets/research.
2. Correct spatial distances, geometry validation and association semantics.
3. Add usable official data and explanations with explicit coverage/provenance.
4. Replace speculative answer generation with evidence-constrained answers.
5. Add operational protections and persistent analysis jobs.
6. Integrate statewide UI, access controls and background progress.
7. Run deterministic tests, selected live contracts, production build and UI checks.
8. Document deployment, evaluation and unresolved external-data limits.

Existing UI edits are preserved. Public data availability is not equivalent to completeness or accuracy at every location. No completeness or zero-defect guarantee is made without evidence.

Initial confirmed defects: fabricated AADT distances, missing-geometry coordinate fallbacks, proximity treated as direct observation, congestion inferred from AADT, hardcoded healthy providers, live network tests in default CI, Gainesville-only geocoder fallback.
