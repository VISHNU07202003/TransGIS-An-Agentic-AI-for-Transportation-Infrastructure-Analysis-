import logging
import asyncio
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas import IntersectionCandidate
from app.gis.spatial import find_features_within_radius, haversine_distance_m
from app.data.fdot_client import FDOTClient

logger = logging.getLogger(__name__)

def _format_intersection_name(roadway: Optional[str], intersecting_roadway: Optional[str], description: Optional[str] = None) -> str:
    parts = []
    if roadway and roadway.strip():
        parts.append(roadway.strip())
    if intersecting_roadway and intersecting_roadway.strip():
        parts.append(intersecting_roadway.strip())
    
    if parts:
        name = " & ".join(parts)
    elif description and description.strip():
        name = description.strip()
    else:
        name = "Unnamed Intersection"
        
    if description and description.strip() and parts:
        # If there's an additional descriptive note
        name = f"{name} ({description.strip()})"
    return name

def find_nearby_intersections_db(
    session: Session,
    lat: float,
    lon: float,
    radius_m: float = 250,
    max_results: int = 20,
) -> list[IntersectionCandidate]:
    """Find intersections from local PostGIS database."""
    cols = [
        "id", "source_id", "source_object_id", "roadway",
        "intersecting_roadway", "description", "district", "county"
    ]
    try:
        # Step 1: Search within initial radius
        results = find_features_within_radius(session, "intersections", lat, lon, radius_m, cols, limit=max_results)
        
        # Step 2: If no results, expand to 2x radius
        if not results:
            results = find_features_within_radius(session, "intersections", lat, lon, radius_m * 2, cols, limit=max_results)
            
        candidates = []
        for r in results:
            name = _format_intersection_name(r.get("roadway"), r.get("intersecting_roadway"), r.get("description"))
            candidates.append(
                IntersectionCandidate(
                    id=int(r["id"]),
                    name=name,
                    latitude=float(r.get("latitude", lat)),
                    longitude=float(r.get("longitude", lon)),
                    distance_m=round(float(r["distance_m"]), 1)
                )
            )
        return candidates
    except Exception as e:
        logger.warning(f"Database query for intersections failed: {e}")
        return []

async def find_nearby_intersections_live(
    lat: float,
    lon: float,
    radius_m: float = 250,
    max_results: int = 20,
) -> list[IntersectionCandidate]:
    """Query FDOT ArcGIS FeatureServer directly live for intersections."""
    fdot = FDOTClient()
    try:
        # Initial search
        features = await fdot.query_intersections_near(lat, lon, radius_m)
        if not features:
            features = await fdot.query_intersections_near(lat, lon, radius_m * 2)
            
        candidates = []
        for f in features:
            attrs = f.get("attributes", {})
            geom = f.get("geometry", {})
            item_lon = float(geom.get("x", lon))
            item_lat = float(geom.get("y", lat))
            dist = haversine_distance_m(lat, lon, item_lat, item_lon)
            
            roadway = attrs.get("ROADWAY") or ""
            intsec_roa = attrs.get("INTSEC_ROA") or ""
            intsec_des = attrs.get("INTSEC_DES") or ""
            name = _format_intersection_name(roadway, intsec_roa, intsec_des)
            
            obj_id = attrs.get("OBJECTID", 0)
            candidates.append(
                IntersectionCandidate(
                    id=int(obj_id),
                    name=name,
                    latitude=round(item_lat, 6),
                    longitude=round(item_lon, 6),
                    distance_m=round(dist, 1)
                )
            )
            
        candidates.sort(key=lambda c: c.distance_m)
        return candidates[:max_results]
    finally:
        await fdot.close()

async def find_nearby_intersections_async(
    session: Optional[Session],
    lat: float,
    lon: float,
    radius_m: float = 250,
    max_results: int = 20,
) -> list[IntersectionCandidate]:
    """Async intersection search: tries PostGIS database first, falls back to live FDOT API."""
    if session is not None:
        db_candidates = find_nearby_intersections_db(session, lat, lon, radius_m, max_results)
        if db_candidates:
            return db_candidates
            
    return await find_nearby_intersections_live(lat, lon, radius_m, max_results)

def find_nearby_intersections(
    session: Optional[Session],
    lat: float,
    lon: float,
    radius_m: float = 250,
    max_results: int = 20,
) -> list[IntersectionCandidate]:
    """Hybrid intersection search: tries PostGIS database first, falls back to live FDOT API."""
    if session is not None:
        db_candidates = find_nearby_intersections_db(session, lat, lon, radius_m, max_results)
        if db_candidates:
            return db_candidates
            
    # Fallback to live FDOT FeatureServer
    try:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(find_nearby_intersections_live(lat, lon, radius_m, max_results))
            else:
                return loop.run_until_complete(find_nearby_intersections_live(lat, lon, radius_m, max_results))
        except RuntimeError:
            return asyncio.run(find_nearby_intersections_live(lat, lon, radius_m, max_results))
    except Exception as e:
        logger.error(f"Live FDOT query failed: {e}")
        return []

async def get_intersection_details_async(
    session: Optional[Session],
    intersection_id: int,
) -> dict | None:
    """Async full details for a specific intersection."""
    if session is not None:
        try:
            sql = "SELECT id, source_id, source_object_id, roadway, intersecting_roadway, description, district, county, ST_Y(geometry::geometry) as lat, ST_X(geometry::geometry) as lon FROM intersections WHERE id = :id"
            result = session.execute(text(sql), {"id": intersection_id}).first()
            if result:
                return dict(result._mapping)
        except Exception as e:
            logger.warning(f"Database lookup for intersection {intersection_id} failed: {e}")
            
    fdot = FDOTClient()
    try:
        res = await fdot.query_layer(
            layer_url=f"{fdot.base_url}/6",
            where=f"OBJECTID = {int(intersection_id)}",
            out_sr=4326
        )
        features = res.get("features", [])
        if features:
            attrs = features[0].get("attributes", {})
            geom = features[0].get("geometry", {})
            return {
                "id": attrs.get("OBJECTID"),
                "roadway": attrs.get("ROADWAY"),
                "intersecting_roadway": attrs.get("INTSEC_ROA"),
                "description": attrs.get("INTSEC_DES"),
                "district": attrs.get("DISTRICT"),
                "county": attrs.get("COUNTY"),
                "lat": geom.get("y"),
                "lon": geom.get("x")
            }
        return None
    finally:
        await fdot.close()

def get_intersection_details(
    session: Optional[Session],
    intersection_id: int,
) -> dict | None:
    """Get full details for a specific intersection."""
    if session is not None:
        try:
            sql = "SELECT id, source_id, source_object_id, roadway, intersecting_roadway, description, district, county, ST_Y(geometry::geometry) as lat, ST_X(geometry::geometry) as lon FROM intersections WHERE id = :id"
            result = session.execute(text(sql), {"id": intersection_id}).first()
            if result:
                return dict(result._mapping)
        except Exception as e:
            logger.warning(f"Database lookup for intersection {intersection_id} failed: {e}")
            
    try:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(get_intersection_details_async(session, intersection_id))
            else:
                return loop.run_until_complete(get_intersection_details_async(session, intersection_id))
        except RuntimeError:
            return asyncio.run(get_intersection_details_async(session, intersection_id))
    except Exception as e:
        logger.error(f"Failed to fetch live intersection details for {intersection_id}: {e}")
        return None

def resolve_intersection(
    candidates: list[IntersectionCandidate],
    address_hint: str | None = None,
) -> dict:
    """Determine if we have a clear match or need clarification."""
    if not candidates:
        return {"status": "not_found", "candidates": []}
        
    if len(candidates) == 1:
        return {"status": "resolved", "intersection": candidates[0]}
        
    closest = candidates[0]
    next_closest = candidates[1]
    
    # If the closest intersection is very close (<50m) and significantly closer than the second closest (>100m away), it's clearly dominant
    if closest.distance_m < 50 and next_closest.distance_m > 120:
        return {"status": "resolved", "intersection": closest}
        
    return {"status": "needs_clarification", "candidates": candidates}
