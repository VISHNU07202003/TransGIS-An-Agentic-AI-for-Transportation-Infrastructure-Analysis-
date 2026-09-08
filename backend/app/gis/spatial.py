from sqlalchemy import text
from sqlalchemy.orm import Session

def create_point_wkt(lon: float, lat: float) -> str:
    """Create WKT point string."""
    return f"POINT({lon} {lat})"

import math

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in meters between two points on the earth."""
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

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
        col_str = ", ".join([f'"{c}"' for c in columns])
        
    order_clause = ""
    if order_by_distance:
        order_clause = "ORDER BY distance_m ASC"
        
    sql = f"""
        SELECT {col_str}, 
               ST_Distance(geography(geometry), geography(ST_SetSRID(ST_Point(:lon, :lat), 4326))) AS distance_m,
               ST_Y(geometry::geometry) AS latitude,
               ST_X(geometry::geometry) AS longitude
        FROM {table}
        WHERE ST_DWithin(geography(geometry), geography(ST_SetSRID(ST_Point(:lon, :lat), 4326)), :radius)
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
    return session.execute(text(sql), {
        "lon1": lon1,
        "lat1": lat1,
        "lon2": lon2,
        "lat2": lat2
    }).scalar() or 0.0
