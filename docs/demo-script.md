# TransGIS Demo Script (3-5 Minutes)

## Goal
Demonstrate TransGIS v1.1's capability to safely resolve heterogeneous transportation data, block hallucinations, enforce ambiguity clarification, and perform crash-safe ingestion.

## 1. Normal Query (Single-source lookup)
**Action:** Type: *"What is the AADT on NW 43rd Street?"*
**Talking Point:** 
- "Notice how quickly the agent retrieves the data. It uses the canonical layer to pull FDOT observations attached to the street network without needing to guess or iterate through raw GIS API paginations."

## 2. Cross-Source Query
**Action:** Type: *"How does the traffic volume here compare to the intersection at NW 13th St and University Ave?"*
**Talking Point:**
- "This requires reasoning across state and municipal jurisdictions. System B would struggle to merge the Gainesville point data with the FDOT linear segments on the fly, sometimes hallucinating sums. System C pulls the pre-resolved `canonical_node`, correctly returning both records."

## 3. Ambiguous Location (Forcing Clarification)
**Action:** Click near the Archer Road / I-75 interchange (where frontage roads and ramps overlap tightly) and ask: *"How many cars pass through here?"*
**Talking Point:**
- "Here is our hard ambiguity gate in action. The Entity Resolution model flagged the location as `AMBIGUOUS`. Instead of guessing, the orchestration layer intercepts the tool call and returns a `CLARIFICATION_REQUIRED` state. The UI prompts the user to select the specific ramp or the main carriageway."

## 4. Provenance & Verification
**Action:** Select the main carriageway. The agent returns the data. Click the "Provenance" toggle in the UI.
**Talking Point:**
- "Every number output by the LLM is strictly verified against the database. You can see the exact FDOT source record ID, the observation year, and the original geometry preserved. The LLM cannot invent math."

## 5. Crash-Safe Ingestion
**Action:** Open terminal. Run the ingestion worker script with a `--crash-simulate` flag halfway through processing the Gainesville dataset.
**Talking Point:**
- "In production, data ingestion fails. Notice that the frontend map hasn't changed. The database kept the partial load isolated in `STAGING`. When I restart the worker, it picks up safely, finishes, and atomically publishes the new view without duplicating records or causing downtime."
