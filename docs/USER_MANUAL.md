# User Manual

## 1. Opening the application

1. Start the FastAPI backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. In a separate terminal, launch the React frontend:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open your browser to `http://localhost:5173`.
4. The application presents an interactive map centered on Gainesville, Florida, an address search bar at the top, a question chat panel on the lower-left, and a structured result and provenance panel on the lower-right.

---

## 2. Selecting a location by address

1. In the search bar at the top of the interface, enter a street address or intersection in Gainesville (e.g., `13th St & University Ave` or `Main St`).
2. Click **Search** or press Enter.
3. The system geocodes the address using OpenStreetMap Nominatim with strict Gainesville, FL localization.
4. The map centers on the resolved coordinates, places a location marker, and retrieves candidate intersections within the search radius.

---

## 3. Selecting a location by map click

1. Navigate around the interactive web map using pan and zoom controls.
2. Click on any roadway or intersection in the Gainesville urban area.
3. A pin marks your clicked point, and the system automatically queries authoritative FDOT intersection records within an initial 250-meter radius (expanding to 500 meters if needed).

---

## 4. Asking a transportation question

Once an intersection is identified or selected, type your transportation question in the chat panel:

- *"What was the traffic volume from 5 PM to 6 PM here?"*
- *"Is this intersection signalized?"*
- *"What is the AADT on the nearby roadway?"*
- *"What transportation information is available here?"*

Click **Send** or press Enter. The agent interprets the query, invokes the appropriate GIS/data retrieval tools, validates the result, and returns an answer.

---

## 5. Choosing among multiple intersections

If your click or address is near multiple intersections (e.g., within 50–100 meters of a complex junction):
1. The agent will respond: *"I found multiple intersections near your selected location. Please select one to analyze:"*
2. A candidate list appears in the results panel and on the map.
3. Each candidate displays the intersecting street names and exact distance in meters from your point.
4. Click your desired intersection from the list or map.
5. Only after selection does the system proceed with data querying and analysis.

---

## 6. Understanding the answer

- **Factual, non-fabricated responses**: The AI agent never guesses or interpolates transportation statistics. Every number comes directly from official FDOT or City of Gainesville records.
- **Metric distinction**:
  - **AADT (Annual Average Daily Traffic)**: An annualized estimate of average daily 24-hour traffic volume on that roadway segment (vehicles/day).
  - **Hourly Traffic Volume**: An observation of actual vehicles passing through during a specific one-hour interval.
- **Visual highlight**: When data is retrieved, the selected intersection and corresponding monitoring site or roadway segment are highlighted on the map.

---

## 7. Understanding source/provenance

Every factual numerical answer includes an authoritative provenance box:
- **Agency**: FDOT or City of Gainesville Public Works
- **Dataset**: Specific dataset name (e.g., *FDOT Annual Average Daily Traffic*, *FDOT Traffic Signal Locations TDA*, *City of Gainesville Traffic Counts*)
- **Source URL**: Direct link to the official GIS layer or open data portal
- **Record Identifier**: Official station ID, OBJECTID, or roadway segment ID
- **Observation Date / Year**: When the count was taken
- **Spatial Relation**: Exact distance in meters between the queried intersection and the monitoring equipment

---

## 8. Understanding "no authoritative data found"

A core reliability safeguard of this system is its refusal to hallucinate:
- If you ask for hourly volume at an intersection where continuous hourly count telemetry does not exist, the agent explicitly states:
  > *"No authoritative hourly traffic-volume observation was found for this intersection."*
- If nearby AADT is available, the agent will note the AADT value while explicitly reminding you that AADT is an annualized daily average, not the requested hourly volume.

---

## 9. Example questions

| Question | Expected System Behavior |
|---|---|
| *"What was the traffic volume from 5 PM to 6 PM here?"* | Checks for hourly count records; if none, returns verified no-data response explaining AADT differences. |
| *"Is this intersection signalized?"* | Queries FDOT Traffic Signal inventory; confirms presence of state-recorded signals within 250m. |
| *"What is the AADT near this intersection?"* | Queries FDOT RCI Layer 0; returns annual average daily volume in vehicles/day with year. |
| *"What transportation information is available here?"* | Returns a multi-source summary of signals, nearby monitoring sites, and roadway segments. |

---

## 10. Known limitations

- **Prototype Scope**: Restricted to the Gainesville, Florida urban boundary.
- **Authoritative Data Sources**: Relies exclusively on FDOT ArcGIS REST services and the City of Gainesville Open Data portal.
- **No Real-time Control**: The application is a research information tool. It does not perform active signal timing, traffic prediction, autonomous vehicle dispatch, or emergency control.
