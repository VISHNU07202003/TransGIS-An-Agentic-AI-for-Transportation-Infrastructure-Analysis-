"""Published statewide roadway context; proximity never proves applicability.

Schemas verified against official FDOT responses retained under tests/fixtures/
research. This adapter provides inventory, not current traffic or safety advice.
"""
from datetime import datetime, timezone
import math

from app.config import get_settings
from app.gis.spatial import geometry_distance_m, nearby_relation, valid_coordinate
from app.providers import ProviderUnavailable, SchemaChanged, get_json_sync


FUNCTIONAL_CLASSES = {
    "01": "Rural principal arterial - interstate",
    "02": "Rural principal arterial - expressway",
    "04": "Rural principal arterial - other",
    "06": "Rural minor arterial",
    "07": "Rural major collector",
    "08": "Rural minor collector",
    "09": "Rural local",
    "11": "Urban principal arterial - interstate",
    "12": "Urban principal arterial - expressway",
    "14": "Urban principal arterial - other",
    "16": "Urban minor arterial",
    "17": "Urban major collector",
    "18": "Urban minor collector (federal aid)",
    "19": "Urban local",
}
CLASSIFICATION_SOURCE = "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/MapServer/3"
LAYERS = {
    "roadway_inventory": (29, ("MAXSPEED_R", "MAXSPEED_L", "NOLANES_R", "NOLANES_L", "FUNCLASS", "TYPEROAD")),
    "functional_classification": (3, ("FUNCLASS",)),
    "truck_volumes": (19, ("YEAR_", "TRUCKAADT", "AADT", "TFCTR", "COSITE")),
    "bridges": (1, ("STRUCTURE_", "ROAD_SIDE")),
}
COMMON_FIELDS = ("OBJECTID", "ROADWAY", "COUNTY", "BEGIN_POST", "END_POST")


def _positive_number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _integer(value):
    number = _positive_number(value)
    return int(number) if number is not None and number.is_integer() else None


def _text(value):
    return str(value).strip() if value is not None and str(value).strip() else None


def _classification(value):
    code = _text(value)
    return {"code": code, "label": FUNCTIONAL_CLASSES.get(code), "definition_source": CLASSIFICATION_SOURCE}


def _details(group, attributes):
    if group == "roadway_inventory":
        return {
            "posted_speed_mph": {"right": _integer(attributes.get("MAXSPEED_R")), "left": _integer(attributes.get("MAXSPEED_L"))},
            "through_lanes": {"right": _integer(attributes.get("NOLANES_R")), "left": _integer(attributes.get("NOLANES_L"))},
            "functional_classification": _classification(attributes.get("FUNCLASS")),
            "roadway_type_code": _text(attributes.get("TYPEROAD")),
            "limitations": "Published inventory; observation date unavailable. Left/right refer to inventory sides, not compass directions. Zero or missing speed/lane values are unknown. Do not sum lane fields or infer current vehicle speeds.",
        }
    if group == "functional_classification":
        return {"functional_classification": _classification(attributes.get("FUNCLASS")), "limitations": "Roadway function inventory; observation date unavailable. Unknown classification codes are preserved without a guessed label."}
    if group == "truck_volumes":
        return {
            "truck_aadt": _integer(attributes.get("TRUCKAADT")), "truck_aadt_unit": "trucks/day (annual average)",
            "aadt": _integer(attributes.get("AADT")), "aadt_unit": "vehicles/day (annual average)",
            "truck_factor_percent": _positive_number(attributes.get("TFCTR")), "site_id": _text(attributes.get("COSITE")),
            "limitations": "Published annual segment statistics, not measured hourly counts or an intersection total. Zero/missing values are not treated as validated observations.",
        }
    return {
        "structure_id": _text(attributes.get("STRUCTURE_")), "road_side": _text(attributes.get("ROAD_SIDE")),
        "limitations": "Nearby bridge inventory only; this source supplies no condition rating, current closure, clearance, or safety assessment.",
    }


def query_road_context(lat: float, lon: float, radius_m: float = 500, roadway: str | None = None) -> dict:
    """Return bounded groups of nearby official inventory and explicit failures.

    Exact source-roadway equality adds evidence of corridor identity only. The
    caller must supply an authoritative roadway ID; street names are not IDs.
    At most 100 candidates per layer are inspected and 5 records returned. A
    truncated provider response is explicitly partial, never a complete census.
    """
    if not valid_coordinate(lat, lon):
        raise ValueError("Finite WGS84 latitude and longitude are required")
    if isinstance(radius_m, bool) or not _positive_number(radius_m) or float(radius_m) > 5000:
        raise ValueError("radius_m must be greater than zero and at most 5000 meters")
    lat, lon, radius_m = float(lat), float(lon), float(radius_m)
    roadway = _text(roadway)
    base = get_settings().fdot_rci_base_url.rstrip("/")
    result = {
        "status": "ok", "latitude": lat, "longitude": lon, "radius_m": radius_m,
        "coverage": "Florida FDOT published inventory; coverage varies by roadway and attribute",
        "association_policy": "Proximity-only unless source ROADWAY exactly matches the supplied authoritative roadway ID. Even a match does not establish intersection-wide applicability.",
        "record_limit_per_group": 5, "errors": [], "warnings": [], "layer_status": {},
        **{group: [] for group in LAYERS},
    }
    for group, (layer_id, fields) in LAYERS.items():
        source_url = f"{base}/{layer_id}"
        params = {
            "f": "json", "where": "1=1", "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint", "inSR": 4326, "outSR": 4326,
            "spatialRel": "esriSpatialRelIntersects", "distance": radius_m,
            "units": "esriSRUnit_Meter", "returnGeometry": "true",
            "outFields": ",".join(COMMON_FIELDS + fields), "resultRecordCount": 100,
            "orderByFields": "OBJECTID ASC",
        }
        try:
            data = get_json_sync(f"{source_url}/query", params=params, required_fields=set(COMMON_FIELDS + fields))
            if not isinstance(data, dict) or not isinstance(data.get("features"), list):
                raise ValueError("Invalid feature collection")
            if data.get("error"):
                raise ValueError("Provider returned a query error")
            sr = data.get("spatialReference") or {}
            if sr.get("latestWkid", sr.get("wkid")) != 4326 and data["features"]:
                raise ValueError("Missing or unexpected response coordinate reference system")
            candidates = []
            invalid = 0
            retrieved_at = datetime.now(timezone.utc).isoformat()
            for feature in data["features"][:100]:
                if not isinstance(feature, dict):
                    invalid += 1
                    continue
                attrs, geometry = feature.get("attributes"), feature.get("geometry")
                if not isinstance(attrs, dict) or attrs.get("OBJECTID") is None or not isinstance(geometry, dict):
                    invalid += 1
                    continue
                geometry = {**geometry, "spatialReference": geometry.get("spatialReference") or sr}
                distance = geometry_distance_m(lat, lon, geometry)
                if distance is None:
                    invalid += 1
                    continue
                if distance > radius_m:
                    continue
                source_roadway = _text(attrs.get("ROADWAY"))
                candidates.append({
                    "source_agency": "Florida Department of Transportation", "source_url": source_url,
                    "source_record_id": str(attrs["OBJECTID"]), "roadway_id": source_roadway,
                    "county": _text(attrs.get("COUNTY")), "observation_year": _integer(attrs.get("YEAR_")),
                    "retrieved_at": retrieved_at,
                    "milepoint_interval": {"begin": attrs.get("BEGIN_POST"), "end": attrs.get("END_POST")},
                    **nearby_relation(distance, kind=group.replace("_", " "), roadway_match=bool(roadway and source_roadway == roadway)),
                    **_details(group, attrs),
                })
            candidates.sort(key=lambda record: (record["distance_m"], record["source_record_id"]))
            result[group] = candidates[:5]
            truncated = bool(data.get("exceededTransferLimit")) or len(data["features"]) > 100
            result["layer_status"][group] = {"status": "partial" if truncated or invalid else "ok", "candidate_set_complete": not truncated and not invalid, "records_returned": len(result[group]), "records_omitted_from_display": max(0, len(candidates) - 5), "invalid_records": invalid}
            if truncated:
                result["warnings"].append({"dataset": group, "reason": "Provider candidate limit reached; displayed records may not include every nearer record."})
            if invalid:
                result["warnings"].append({"dataset": group, "reason": f"Skipped {invalid} records without usable identifiers or geometry."})
        except (ProviderUnavailable, SchemaChanged, ValueError, TypeError) as exc:
            result["errors"].append({"dataset": group, "source_url": source_url, "error_type": type(exc).__name__, "message": "Source unavailable or response failed validation; this is not evidence of no nearby data."})
            result["layer_status"][group] = {"status": "unavailable", "candidate_set_complete": False}
    if len(result["errors"]) == len(LAYERS):
        result["status"] = "unavailable"
    elif result["errors"] or result["warnings"]:
        result["status"] = "partial"
    elif not any(result[group] for group in LAYERS):
        result["status"] = "no_data"
    return result
