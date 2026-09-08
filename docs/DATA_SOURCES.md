# Authoritative Data Sources

## 1. FDOT (Florida Department of Transportation)

### 1.1 RCI FeatureServer Overview
- **Base Endpoint**: `https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer`
- **Native Spatial Reference**: EPSG:26917 (NAD83 / UTM zone 17N)
- **Application Target Spatial Reference**: EPSG:4326 (WGS84 via `outSR=4326`)

### 1.2 Discovered Layers & Field Mappings

#### Layer 6: Intersections (`esriGeometryPoint`)
- **URL**: `https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/6`
- **Purpose**: Authoritative statewide intersection inventory identifying connecting roadways and configurations.
- **Key Fields**:
  - `OBJECTID` (integer): Unique record identifier.
  - `ROADWAY` (string): Primary roadway code/identifier.
  - `INTSEC_ROA` (string): Intersecting roadway name (e.g., `SE 1ST ST`, `NW 13TH ST`).
  - `INTSEC_DIR` (string): Intersection direction code.
  - `INTSEC_DES` (string): Physical configuration description (e.g., `INTERSECTING STREET 90 DEGREES TO THE LEFT`).
  - `COUNTY` (string): County name (`Alachua`).
  - `DISTRICT` (string): FDOT District (`2`).

#### Layer 0: Annual Average Daily Traffic (AADT) (`esriGeometryPolyline`)
- **URL**: `https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0`
- **Purpose**: Roadway segment traffic statistics representing annualized 24-hour daily traffic.
- **Key Fields**:
  - `OBJECTID` (integer): Unique segment identifier.
  - `ROADWAY` (string): State roadway ID.
  - `AADT` (integer): Annual Average Daily Traffic volume in vehicles per day.
  - `YEAR_` (smallint): Observation count year.
  - `DESC_FRM` (string): Roadway segment starting landmark description.
  - `DESC_TO` (string): Roadway segment ending landmark description.
  - `KFCTR`, `DFCTR`, `TFCTR` (double): K-factor, Directional distribution, and Truck percentage factors.

#### Layer 9 & 16: Traffic Monitoring Sites (`esriGeometryPoint`)
- **URL Layer 9 (Portable)**: `https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/9`
- **URL Layer 16 (Telemetered)**: `https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/16`
- **Purpose**: Locations of permanent telemetered and temporary portable traffic monitoring stations.
- **Key Fields**:
  - `OBJECTID` / `COSITE` (string): County-site equipment identifier.
  - `AADT` (integer): Site-level measured annual volume.
  - `YEAR_` (integer): Measurement year.
  - `SITETYPE` (string): Equipment classification.
  - `ACTIVE` (string): Operational status (`Y`/`N`).

#### Traffic Signal Locations (`esriGeometryPoint`)
- **Service Endpoint**: `https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/Traffic_Signal_Locations_TDA/FeatureServer/0`
- **Purpose**: State and locally operated traffic control signal equipment.
- **Key Fields**:
  - `FID` (integer): Unique feature ID.
  - `SIGNALID` (string): Signal identification number.
  - `VALUE_` (string): Equipment type (e.g., `Traffic Control Signal`, `Pedestrian Hybrid Beacon`).
  - `RDWYID` / `SDESTRET` (string): Roadway corridor identifier.
  - `MAINTAGC` (string): Maintaining agency name.

---

## 2. City of Gainesville Open Data

### 2.1 Traffic Counts Dataset
- **Portal**: dataGNV (`https://data.cityofgainesville.org`)
- **Underlying Tabular Dataset ID**: `v2qq-gus2`
- **Map View ID**: `pfc3-w5ih`
- **Resource API Endpoint**: `https://data.cityofgainesville.org/resource/v2qq-gus2.json`
- **Attribution**: City of Gainesville Public Works, Transportation Planning Division
- **Record Count**: 463 count stations across Gainesville

### 2.2 Key Attributes
- `the_geom` (Point): WGS84 point coordinates `[longitude, latitude]`.
- `station` (text): Local municipal count station identifier (e.g., `1000`, `1001`).
- `street` (text): Street name (e.g., `N MAIN ST`, `UNIVERSITY AVE`).
- `block` (text): Block reference number (e.g., `900`, `1200`).
- `count_type` (text): Station type (e.g., `CI` for City Inventory).
- `adt_2000` through `adt_2016` (number): Historical annual average daily traffic counts.
- `adt_1314` (number): Most recent consolidated count period volume (2013–2014).
- `pkam_1314` / `pkpm_1314` (number): Peak morning and peak afternoon one-hour volumes during count period.
- `heavy_1314` (number): Commercial/heavy truck vehicle percentage.

---

## 3. Data Provenance & Freshness Policy

1. **Date Separation**: The system strictly separates the *Observation Date / Year* (when physical counts occurred) from the *Retrieval Timestamp* (when the API fetched the record).
2. **No Data Fabrication**: Where authoritative hourly breakdown counts do not exist in the published feeds, the system refuses to estimate or synthesize hourly values, in compliance with project data rules.
