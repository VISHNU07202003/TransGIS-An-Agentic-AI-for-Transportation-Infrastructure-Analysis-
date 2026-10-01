# Entity Semantics

## 1. FDOT RCI Intersections (Layer 6)
- **Dataset:** FDOT Roadway Characteristics Inventory (RCI) - Intersections (Layer 6)
- **One record represents:** An intersection where two state-managed roadways meet.
- **Geometry:** Point
- **Measurement applies to:** Intersection
- **Stable source identifier:** `OBJECTID`
- **Street/route identifiers:** `ROADWAY` (e.g., "26000000"), `INTERSECTING_ROADWAY`
- **Traffic measurement semantics:** No direct traffic measurements; structural representation only.
- **Temporal semantics:** Snapshot of current physical infrastructure.
- **Can this logically map to a canonical node?** Yes. It represents the physical convergence of road segments.
- **Can this logically map to a canonical edge?** No.
- **Important ambiguity:** Only covers state-maintained intersections. Local cross-streets may be present as `INTERSECTING_ROADWAY` text, but the point itself is tied to the state route.

## 2. FDOT AADT (Layer 0)
- **Dataset:** FDOT RCI Annual Average Daily Traffic (Layer 0)
- **One record represents:** A continuous segment of state-maintained roadway for which a single AADT volume is estimated.
- **Geometry:** LineString
- **Measurement applies to:** Road segment (Edge)
- **Stable source identifier:** `OBJECTID`
- **Street/route identifiers:** `ROADWAY`
- **Traffic measurement semantics:** Average daily traffic (vehicles/day) annualized over a year.
- **Temporal semantics:** Valid for a specific year (`AADT_YEAR`).
- **Can this logically map to a canonical node?** No.
- **Can this logically map to a canonical edge?** Yes. May span one or more canonical edges depending on the topology granularity.
- **Important ambiguity:** A single FDOT AADT segment might cross multiple local intersections. Mapping this to a canonical topology requires splitting or replicating the association across multiple canonical edges.

## 3. FDOT Traffic Signals TDA
- **Dataset:** FDOT Traffic Signal Locations TDA
- **One record represents:** The location of a traffic signal assembly.
- **Geometry:** Point
- **Measurement applies to:** Intersection (typically) or mid-block pedestrian crossing.
- **Stable source identifier:** `OBJECTID`
- **Street/route identifiers:** `ROADWAY`
- **Traffic measurement semantics:** Presence/Absence of signalization, signal type.
- **Temporal semantics:** Current status.
- **Can this logically map to a canonical node?** Yes, usually indicates a canonical node (intersection) is signalized.
- **Can this logically map to a canonical edge?** Yes, if it is a mid-block pedestrian signal, though most map to nodes.
- **Important ambiguity:** Not all signals are at intersections (e.g., HAWK beacons).

## 4. Gainesville Traffic Counts (pfc3-w5ih / v2qq-gus2)
- **Dataset:** City of Gainesville Traffic Counts / TrafficData20140522
- **One record represents:** A physical location where a traffic counter (hose or sensor) was placed to record passing vehicles.
- **Geometry:** Point
- **Measurement applies to:** Road segment (Edge) passing through the point.
- **Stable source identifier:** `station` or `site_id`
- **Street/route identifiers:** `street` (e.g., "N MAIN ST"), `block` (e.g., "900")
- **Traffic measurement semantics:** Volume of vehicles passing the site. Represents the flow *along the road segment*, not the total capacity of an intersection.
- **Temporal semantics:** Historically tied to specific years (e.g., `adt_2014`).
- **Can this logically map to a canonical node?** No. Although often placed *near* intersections, the count applies to vehicles on the segment itself (one direction or bidirectional).
- **Can this logically map to a canonical edge?** Yes. It represents traffic flow on the canonical edge on which the point lies.
- **Important ambiguity:** A count site point is often geolocated exactly at an intersection, but its *semantics* apply to one of the intersecting roads. Mapping it to an intersection node would falsely imply the count measures all legs of the intersection. It must map to the specific edge matching its `street` name.
