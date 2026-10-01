# Florida-wide TransGIS: verified data and research

Verified on 2026-09-21. This is a source-access and integration assessment, not a claim that every source below is integrated. Public records were queried without credentials. Eight small response fixtures are retained in `backend/tests/fixtures/research/`; each records its exact request URL. These frozen samples are for reproducibility, never a fallback presented as live data.

## 1. Coverage and the most useful additions

Use FDOT as the statewide inventory backbone and Gainesville as an explicitly historical municipal supplement. Statewide publication does **not** imply every local road or requested measurement exists. Return coverage, observation year, source, and association confidence with each answer.

The quickest new capabilities are roadway inventory context (posted speed and lane fields), functional classification, truck AADT, and nearby bridge inventory. These support questions about the kind of roadway and its published attributes without inventing traffic conditions. Obtain current values through bounded spatial queries; retain snapshots for testing separately.

### Public, machine-readable sources verified with actual responses

All FDOT layer numbers below refer to [RCI FeatureServer](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer). The inspected layers allow JSON/GeoJSON queries and report a 1,000-record maximum. Native coordinates are EPSG:26917; request `outSR=4326`, retain the response CRS, and calculate distances from returned geometry.

| Dataset and exact metadata endpoint | Useful fields and units | Coverage and limitations |
|---|---|---|
| [AADT /0](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0) | `AADT` vehicles/day, `YEAR_`, `COSITE`, `ROADWAY`, `BEGIN_POST`, `END_POST`, source flags | Published roadway segments. Annual average daily volume is neither current congestion nor a measured hourly count. Marion sample: 2025, 14,600 vehicles/day. |
| [Intersections /6](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/6) | `OBJECTID`, `ROADWAY`, `INTSEC_ROA`, `INTSEC_DES`, `BEGIN_POST` | Point inventory; source roadway ID and milepoint support association. A crossing name alone does not establish the other road's identifier. |
| [RCI Top 30 /29](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/29) | `MAXSPEED_R/L`, `NOLANES_R/L`, `FUNCLASS`, `TYPEROAD`, `ROADWAY`, milepoint interval | Inventory segments, not speed sensors. Keep right/left fields separate. Sample has right speed 45 and left speed 0: zero must not be presented as a posted 0 mph limit. No observation-year field was found. |
| [Functional classification /3](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/3) | `FUNCLASS`, `ROADWAY`, milepoint interval | Coded roadway function. Decode using official [MapServer renderer labels](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/MapServer/3?f=json), preserving the original code. |
| [Truck volume /19](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/19) | `TRUCKAADT` trucks/day, `AADT`, `YEAR_`, `TFCTR`, `COSITE`, `ROADWAY` | Annual segment statistics. Sample: 2025 truck AADT 217, AADT 19,700, truck factor 1.1. Prefer the published truck AADT over recreating its rounding. |
| [Bridges /1](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/1) | `STRUCTURE_`, `ROADWAY`, `ROAD_SIDE`, milepoint interval | Polyline inventory and structure identifiers. This layer does not contain inspection ratings, current structural safety, closure status, or clearance. |
| [Signals /18](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/18) | `SIGNALID`, `RDWYID`, `SDESTRET`, `MAINTAGC`, `VALUE_`, `BEGPT` | Inventory only. Raw `VALUE_` is coded (sample `02`), unlike some hosted TDA representations. `EFFDATE` can be a placeholder (sample 1950), not a reliable freshness date. No signal phase/timing or live operational state. |
| [Roadway names /13](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/13) | `NAME`, `ROADWAY`, milepoint interval | Useful for human-readable corridor names; joins require matching roadway and interval, not just nearby geometry. |
| [Portable sites /9](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/9), [telemetered sites /16](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/16) | `COSITE`, `AADT`, `YEAR_`, `ACTIVE`, `SITETYPE` where present | Station inventory and annual statistics. Station existence/active flag does not mean an accessible real-time feed. Inspect each schema separately. |
| [Bike lanes /28](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/28), [median /25](https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/25) | Bike/sidewalk codes and widths; `MEDIAN_TYP`; roadway and interval | Public candidates for later additions. Validate codebooks and width units before exposing values. Missing inventory is not evidence that a facility does not exist. |

Posted speed semantics come from [RCI Feature 311](https://ftp.fdot.gov/public/file/3Sk3Lfw5_0WgiGgjclpuaA/FDOT_RCI_Handbook_F311.pdf): the inventory describes maximum posted speed, in mph. Roadside interpretation is tied to inventory direction; it is not automatically northbound/southbound. Consult [RCI handbook](https://www.fdot.gov/statistics/rci/default.shtm) and [number-of-lanes metadata](https://www.arcgis.com/sharing/rest/content/items/3f217f88f25347709458ee7f9f651e03/info/metadata/metadata.xml?format=default&output=html) before combining lane fields.

### Gainesville: valuable local detail, explicitly historical

The [actual Socrata resource](https://data.cityofgainesville.org/resource/v2qq-gus2.json) is `v2qq-gus2`; `pfc3-w5ih` is a map view. [Metadata](https://data.cityofgainesville.org/api/views/v2qq-gus2.json) reports `TrafficData20140522`, 463 rows, and `rowsUpdatedAt=1401371012` (2014-05-29 UTC). The first retrieved station has 2015/2016 zero values and a 2014 ADT of 16,070. Field names alone do not prove later observations exist.

Use street/station identifiers, geometry, historical ADT, and labeled AM/PM peak volumes. Do not call ADT an annual average unless its methodology establishes that. A peak volume without the clock interval cannot answer an arbitrary 08:00–09:00 question. `heavy_1314` is a decimal in the sample while `heavy_1112` is percent text; percentages require a documented normalization rule. A local government source is not automatically more accurate or newer than FDOT. Never apply this city's records statewide.

## 2. Sources requiring more ingestion work or access

| Access tier | Source | What it can add | Concrete next step / constraint |
|---|---|---|---|
| Public bulk/download | [FDOT GIS directory](https://www.fdot.gov/statistics/gis/default.shtm) | Statewide historical AADT, roadway inventory, network geometry | Weekly published ZIPs; stage and validate before replacing a local snapshot. Some links use a Guest web login. Check archive CRS and schema. |
| Public reports / bulk | [Florida Traffic Online](https://tdaappsprod.dot.state.fl.us/fto/) and [FDOT traffic information](https://www.fdot.gov/statistics/trafficinfo/default.shtm) | Site-specific historical and hourly continuous-count reports; daily CSV archive; FTI Access database | Reports depend on site and period. The official page links [2025 FTI ZIP](https://ftp.fdot.gov/public/file/hrhfapa6puq2vjyjr8ksua/fti_2025.zip) and a [Guest archive](https://ftp.fdot.gov/file/d/FTP/FDOT/co/planning/transtat/traffic/TRAFFIC_IMPACTS/). Build an explicit importer with count interval, timezone, direction, QA flags, and station keys. No stable hourly JSON contract was verified here. |
| Public display; feed access unverified | [FL511](https://fl511.com/) and [official architecture](https://teo.fdot.gov/architecture/architectures/statewide/html/projects/projarch11.html) | Incidents, road closures, and selected current travel information | FDOT documents a third-party feed; this review did not verify a current public developer API or permission terms. Ask the data owner for the supported feed contract before integration. Do not use an unofficial ArcGIS mirror merely because its title says FL511. |
| Public emergency-only display | [FDOT traffic information](https://www.fdot.gov/statistics/trafficinfo/default.shtm) real-time link | Emergency traffic counts | Official page explicitly says activated for emergencies. Do not promise year-round real-time counts. |
| Controlled detailed access | [FDOT crash data guidance](https://fdot.gov/Safety/safetyengineering/crash-data.shtm), [Signal Four guidance](https://www.fdot.gov/forecasting/fl-transportation-forecasting-resource-hub/resources) | Safety analyses and crash history | Public aggregate dashboards and restricted detailed records are different products. Confirm allowed fields and access before ingesting; exclude personal crash-report details. No crash records were obtained for these fixtures. |

The FTO GIS service [catalog](https://gis.fdot.gov/arcgis/rest/services/FTO/fto_PROD/MapServer) was also verified: layers 1/3 are TDA/non-TDA telemetered sites, 5 portable sites, 7 AADT, and 8 truck volume. These layer numbers differ from RCI. They are not interchangeable API configurations.

## 3. Related research and where its data came from

| Work | Data / method actually described | Application to TransGIS |
|---|---|---|
| [GeoGPT, 2023 preprint](https://arxiv.org/abs/2307.07930), [2024 journal article](https://doi.org/10.1016/j.jag.2024.103976) | LLM plans and executes GIS tools; examples include data collection, spatial queries, siting, mapping. Journal article links a task dataset on Figshare. | Keep language interpretation separate from executable GIS calculations. A useful comparison architecture, not a source of Florida counts. |
| [GS-QA, 2026 preprint](https://arxiv.org/abs/2605.22811) | 2,800 questions across 28 templates using OpenStreetMap and Wikipedia; evaluates distance and direction as well as text. | Evaluate spatial numeric error and multi-source joins. OSM may support reference features, but should not silently replace authoritative traffic measurements. |
| [GISAgentBench, 2026 preprint](https://arxiv.org/abs/2608.01645) | Practitioner tasks from GIS Stack Exchange, public data across six areas, reference workflows and exact output artifacts. | Use deterministic expected records and tolerance-based geometry checks instead of judging only fluent answers. Its reported model results do not establish TransGIS performance. |
| [FDOT BDK83 977-18, Moses and Mtoi, 2013](https://www.fdot.gov/docs/default-source/research/reports/FDOT-BDK83-977-18-rpt.pdf) | Archived FDOT TTMS hourly speed/classification files, RCI roadway attributes, and additional measurements at Tallahassee sites. | Demonstrates why inventory, measured speed, and model-estimated speed must be separate. Full hourly analysis requires station-level raw data and quality screening, not AADT divided by 24. |
| [Sharing Real-Time Traffic Information With Travelers Using Twitter, 2019](https://www.frontiersin.org/journals/built-environment/articles/10.3389/fbuil.2019.00083/full) | Historical posts collected from FDOT regional/FL511 and I-4 project accounts using the then-current Twitter API. | Useful for studying information usefulness, but historical social-media collection is not evidence of an available present-day authoritative feed. Prefer a supported agency feed. |

## 4. Integration and evaluation decisions

1. Query only relevant layers for each question. Reuse a bounded cache keyed by provider, layer, spatial query, and schema version; expose retrieval and observation dates separately.
2. Validate geometry CRS, required fields, identifiers, numeric values, and API error objects. A successful HTTP response is insufficient. Log schema drift separately from a valid empty response.
3. Use source geometry for point/segment distances. State the distance method and units; surface distance is not driving distance. A bounding box is only a candidate filter. Keep exact-radius checks after retrieval.
4. Label a nearby record as proximity-only unless independent roadway identifiers match. Even an ID match does not prove an intersection-wide count, approach direction, signal control, or applicability across a grade separation. Prefer a matching roadway and overlapping source milepoint interval when known.
5. Preserve codes, nulls, source flags, and unknown years. Do not convert absent or placeholder values to measured zero. Avoid labeling uncoded/unknown inventory as an observed negative.
6. Return relevant context and short definitions with citations: year, volume basis, roadway function, speed/lane inventory, and what cannot be concluded. More words alone do not improve answer quality.
7. Evaluate Gainesville, Ocala/Marion, Miami-Dade, Orlando, Jacksonville, Tallahassee, and the western Panhandle. Include parallel roads, ramps, bridges, ambiguous intersections, missing geometry, out-of-state locations, historical-only records, provider errors, and schema drift.
8. Compare deterministic retrieval, unconstrained LLM answers, and constrained tool use on the same frozen records. Report unsupported-claim rate, correct source/record/year, distance error, abstention correctness, latency, and provider calls. Keep live-provider tests optional and separately marked.

These are implementation recommendations derived from the verified source characteristics. They are not experimental performance claims. Coverage and accuracy must remain measurable rather than absolute promises.
