import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import httpx

from app.db import check_database_connection
from app.schemas import GeocodeResult
from app.gis.intersection import find_nearby_intersections_async, get_intersection_details_async
from app.gis.traffic import find_traffic_sites_near_intersection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

def _safe_db_session():
    if check_database_connection():
        from app.db import SessionLocal
        try:
            return SessionLocal()
        except Exception:
            return None
    return None

@router.get("/intersections/nearby")
async def get_nearby_intersections(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_m: float = Query(default=250.0, ge=25, le=2000)
) -> Dict[str, Any]:
    """Find nearby intersections and return them as a GeoJSON FeatureCollection."""
    db = _safe_db_session()
    try:
        candidates = await find_nearby_intersections_async(db, lat, lon, radius_m)
    finally:
        if db:
            db.close()
            
    features = []
    for c in candidates:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [c.longitude, c.latitude]
            },
            "properties": {
                "id": c.id,
                "name": c.name,
                "distance_m": c.distance_m
            }
        })
        
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/intersections/{intersection_id}")
async def get_intersection(intersection_id: int) -> Dict[str, Any]:
    """Get single intersection details as GeoJSON Feature."""
    db = _safe_db_session()
    try:
        details = await get_intersection_details_async(db, intersection_id)
    finally:
        if db:
            db.close()
            
    if not details:
        raise HTTPException(status_code=404, detail="Intersection not found")
        
    lat = details.get("lat") or 29.6516
    lon = details.get("lon") or -82.3248
    
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "properties": {
            "id": details.get("id"),
            "roadway": details.get("roadway"),
            "intersecting_roadway": details.get("intersecting_roadway"),
            "description": details.get("description"),
            "district": details.get("district"),
            "county": details.get("county")
        }
    }

@router.get("/intersections/{intersection_id}/traffic-sites")
async def get_intersection_traffic_sites(
    intersection_id: int,
    radius_m: float = Query(default=500.0, ge=25, le=2000)
) -> Dict[str, Any]:
    """Get traffic monitoring sites near an intersection as a GeoJSON FeatureCollection."""
    db = _safe_db_session()
    try:
        sites = find_traffic_sites_near_intersection(db, intersection_id, radius_m)
    finally:
        if db:
            db.close()
            
    features = []
    for s in sites:
        lat = s.get("latitude")
        lon = s.get("longitude")
        if lat is not None and lon is not None:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "id": s.get("id"),
                    "source_agency": s.get("source_agency"),
                    "source_site_id": s.get("source_site_id"),
                    "roadway": s.get("roadway"),
                    "description": s.get("description"),
                    "distance_m": s.get("distance_m"),
                    "aadt": s.get("aadt") or s.get("adt_2014") or s.get("adt_1314")
                }
            })
            
    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/geocode", response_model=GeocodeResult)
async def geocode_address(address: str = Query(..., min_length=1)):
    """Geocode an address in Gainesville, FL via Nominatim."""
    clean_addr = address.strip()
    query_addr = clean_addr
    if "gainesville" not in clean_addr.lower() and "fl" not in clean_addr.lower():
        query_addr = f"{clean_addr}, Gainesville, FL"

    headers = {
        "User-Agent": "AgenticTransportationApp/1.0 (UF Research Transportation Prototype)"
    }
    params = {
        "q": query_addr,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
            resp.raise_for_status()
            results = resp.json()
            
            if results:
                top = results[0]
                return GeocodeResult(
                    latitude=float(top["lat"]),
                    longitude=float(top["lon"]),
                    display_name=top.get("display_name", clean_addr),
                    confidence=float(top.get("importance", 0.5))
                )
    except Exception as e:
        logger.error(f"Geocoding error for '{address}': {e}")
        
    return GeocodeResult(
        latitude=29.651634,
        longitude=-82.324826,
        display_name=f"{clean_addr} (Gainesville fallback)",
        confidence=0.0
    )
