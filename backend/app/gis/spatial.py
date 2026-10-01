from sqlalchemy import text
from sqlalchemy.orm import Session
from geographiclib.geodesic import Geodesic
import math
import re


def valid_coordinate(lat, lon) -> bool:
    """Accept finite WGS84 degrees only; never substitute the requested pin."""
    try:
        return not isinstance(lat, bool) and not isinstance(lon, bool) and math.isfinite(float(lat)) and math.isfinite(float(lon)) and -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
    except (TypeError, ValueError):
        return False


def point_coordinates(geometry: dict | None) -> tuple[float, float] | None:
    """Read (latitude, longitude) from WGS84 ArcGIS or GeoJSON point geometry.

    ArcGIS clients must request outSR=4326 and propagate response spatialReference.
    Missing per-feature CRS is accepted only under that client contract.
    """
    if not isinstance(geometry, dict):
        return None
    sr = geometry.get("spatialReference") or {}
    if sr and sr.get("latestWkid", sr.get("wkid")) != 4326:
        return None
    if "x" in geometry and "y" in geometry:
        lat, lon = geometry["y"], geometry["x"]
    elif geometry.get("type") == "Point" and isinstance(geometry.get("coordinates"), (list, tuple)) and len(geometry["coordinates"]) >= 2:
        lon, lat = geometry["coordinates"][:2]
    else:
        return None
    return (float(lat), float(lon)) if valid_coordinate(lat, lon) else None


def geodesic_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """WGS84 ellipsoidal shortest surface distance, in meters (not route length)."""
    if not valid_coordinate(lat1, lon1) or not valid_coordinate(lat2, lon2):
        raise ValueError("Distance requires finite WGS84 coordinates")
    return float(Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)["s12"])


def geometry_distance_m(lat: float, lon: float, geometry: dict | None) -> float | None:
    """Shortest WGS84 surface distance to point or all geodesic polyline segments.

    A line's vertices are joined by shortest WGS84 geodesics. Each segment is
    searched (including endpoints), not just its vertices or centroid. Long
    segments are subdivided into <=20km search intervals. Numerical search
    tolerance is 1cm; it does not imply centimeter source geometry accuracy.
    Missing, malformed and unsupported CRS geometries return None.
    """
    if not valid_coordinate(lat, lon) or not isinstance(geometry, dict):
        return None
    sr = geometry.get("spatialReference") or {}
    if sr and sr.get("latestWkid", sr.get("wkid")) != 4326:
        return None
    point = point_coordinates(geometry)
    if point:
        return geodesic_distance_m(lat, lon, *point)
    paths = geometry.get("paths")
    if geometry.get("type") == "LineString":
        paths = [geometry.get("coordinates")]
    elif geometry.get("type") == "MultiLineString":
        paths = geometry.get("coordinates")
    if not isinstance(paths, list) or not paths:
        return None
    best = math.inf
    for path in paths:
        if not isinstance(path, list) or len(path) < 2:
            return None
        if any(not isinstance(p, (list, tuple)) or len(p) < 2 or not valid_coordinate(p[1], p[0]) for p in path):
            return None
        for start, end in zip(path, path[1:]):
            line = Geodesic.WGS84.InverseLine(float(start[1]), float(start[0]), float(end[1]), float(end[0]))
            length = line.s13
            def distance_at(position):
                p = line.Position(position)
                return geodesic_distance_m(lat, lon, p["lat2"], p["lon2"])
            best = min(best, distance_at(0), distance_at(length))
            intervals = max(1, math.ceil(length / 20000))
            ratio = (math.sqrt(5) - 1) / 2
            for part in range(intervals):
                left, right = length * part / intervals, length * (part + 1) / intervals
                a, b = right - ratio * (right - left), left + ratio * (right - left)
                da, db = distance_at(a), distance_at(b)
                while right - left > 0.01:
                    if da < db:
                        right, b, db = b, a, da
                        a = right - ratio * (right - left)
                        da = distance_at(a)
                    else:
                        left, a, da = a, b, db
                        b = left + ratio * (right - left)
                        db = distance_at(b)
                best = min(best, da, db)
    return best if math.isfinite(best) else None


def nearby_relation(distance_m: float, kind: str = "record", roadway_match: bool = False) -> dict:
    """Proximity and matching road IDs never establish an intersection total."""
    return {
        "distance_m": round(distance_m, 1),
        "distance_method": "WGS84 ellipsoidal shortest surface distance to source geometry",
        "geometry_crs": "EPSG:4326",
        "association_status": "roadway_id_match" if roadway_match else "proximity_only",
        "spatial_relation": f"Nearby {kind}, {distance_m:.1f} meters from the selected intersection. " +
            ("Source roadway identifier matches an intersection roadway. " if roadway_match else "Roadway association is unverified. ") +
            "This is not an intersection-wide total or proof of a signal controlling the intersection.",
    }

def create_point_wkt(lon: float, lat: float) -> str:
    """Create WKT point string."""
    return f"POINT({lon} {lat})"

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compatibility alias; now uses the WGS84 ellipsoid, not a spherical radius."""
    return geodesic_distance_m(lat1, lon1, lat2, lon2)

def find_features_within_radius(
    session: Session,
    table: str,
    lat: float,
    lon: float,
    radius_m: float,
    columns: list[str] | None = None,
    order_by_distance: bool = True,
    limit: int = 20,
) -> list[dict]:
    """Find features within radius_m meters of a point using PostGIS geography."""
    allowed_tables = ["intersections", "traffic_sites", "traffic_signals", "roadway_segments"]
    if table not in allowed_tables:
        raise ValueError(f"Table {table} not allowed.")
    
    col_str = "*"
    if columns:
        if any(not re.fullmatch(r"[a-z_][a-z0-9_]*", c) for c in columns):
            raise ValueError("Invalid SQL column identifier")
        col_str = ", ".join([f'"{c}"' for c in columns])
        
    order_clause = ""
    source_clause = ""
    if table == "intersections":
        source_clause = "AND source_id IN (SELECT id FROM data_sources WHERE agency = 'FDOT' AND dataset_name = 'RCI Intersections')"
    if order_by_distance:
        order_clause = "ORDER BY distance_m ASC"
        
    sql = f"""
        SELECT {col_str}, 
               ST_Distance(geography(geometry), geography(ST_SetSRID(ST_Point(:lon, :lat), 4326))) AS distance_m,
               ST_Y(ST_ClosestPoint(geometry, ST_SetSRID(ST_Point(:lon, :lat), 4326))) AS latitude,
               ST_X(ST_ClosestPoint(geometry, ST_SetSRID(ST_Point(:lon, :lat), 4326))) AS longitude
        FROM {table}
        WHERE ST_DWithin(geography(geometry), geography(ST_SetSRID(ST_Point(:lon, :lat), 4326)), :radius)
        {source_clause}
        {order_clause}
        LIMIT :limit
    """
    
    result = session.execute(text(sql), {
        "lon": lon,
        "lat": lat,
        "radius": radius_m,
        "limit": limit
    })
    
    return [dict(row._mapping) for row in result]

def create_search_buffer(
    session: Session,
    lat: float, 
    lon: float,
    radius_m: float,
) -> dict:
    """Create a circular buffer geometry around a point. Returns GeoJSON."""
    sql = """
        SELECT ST_AsGeoJSON(ST_Buffer(geography(ST_SetSRID(ST_Point(:lon, :lat), 4326)), :radius)) AS geojson
    """
    result = session.execute(text(sql), {
        "lon": lon,
        "lat": lat,
        "radius": radius_m
    }).scalar()
    
    import json
    return json.loads(result) if result else {}

def calculate_distance_m(
    session: Session,
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> float:
    """Calculate distance in meters between two points."""
    sql = """
        SELECT ST_Distance(
            geography(ST_SetSRID(ST_Point(:lon1, :lat1), 4326)),
            geography(ST_SetSRID(ST_Point(:lon2, :lat2), 4326))
        )
    """
    value = session.execute(text(sql), {
        "lon1": lon1,
        "lat1": lat1,
        "lon2": lon2,
        "lat2": lat2
    }).scalar()
    if value is None:
        raise ValueError("Database returned no spatial distance")
    return float(value)
