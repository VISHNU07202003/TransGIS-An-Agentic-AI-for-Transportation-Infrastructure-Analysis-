import logging
import asyncio
import math
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, time
from app.gis.spatial import haversine_distance_m, point_coordinates, valid_coordinate, geometry_distance_m, nearby_relation
from app.data.fdot_client import FDOTClient
from app.data.gainesville_client import GainesvilleClient

logger = logging.getLogger(__name__)


def _decorate_db_records(records: list[dict], kind: str) -> list[dict]:
    safe = []
    for record in records:
        distance = record.get("distance_m")
        if distance is None or not math.isfinite(float(distance)) or float(distance) < 0:
            continue
        record.update(nearby_relation(float(distance), kind, bool(record.pop("roadway_match", False))))
        record["distance_method"] = "PostGIS ST_Distance(geography), WGS84 spheroid"
        safe.append(record)
    return safe

def _get_intersection_point(session: Optional[Session], intersection_id: int) -> Optional[tuple[float, float]]:
    from app.gis.intersection import get_intersection_details
    details = get_intersection_details(session, intersection_id)
    if details and valid_coordinate(details.get("lat"), details.get("lon")):
        return float(details["lat"]), float(details["lon"])
    return None

def find_traffic_sites_near_intersection(
    session: Optional[Session],
    intersection_id: int,
    radius_m: float = 500,
) -> list[dict]:
    """Find traffic monitoring sites near a selected intersection."""
    # 1. Try local database if available
    if session is not None:
        try:
            sql = """
                SELECT ts.id, ts.source_id, ts.source_site_id, ts.roadway, ts.description,
                       ds.agency AS source_agency, ds.dataset_name AS dataset, ds.source_url,
                       ts.roadway IS NOT NULL AND ts.roadway IN (i.roadway, i.intersecting_roadway) AS roadway_match,
                       ST_Distance(geography(ts.geometry), geography(i.geometry)) AS distance_m
                FROM intersections i
                JOIN traffic_sites ts ON ST_DWithin(geography(ts.geometry), geography(i.geometry), :radius)
                JOIN data_sources ds ON ds.id = ts.source_id
                WHERE i.source_object_id = :intersection_id
                  AND i.source_id IN (SELECT id FROM data_sources WHERE agency = 'FDOT' AND dataset_name = 'RCI Intersections')
                ORDER BY distance_m ASC
            """
            result = session.execute(text(sql), {"intersection_id": str(intersection_id), "radius": radius_m})
            db_sites = [dict(row._mapping) for row in result]
            if db_sites:
                return _decorate_db_records(db_sites, "monitoring site")
        except Exception as e:
            logger.warning(f"Database query for traffic sites failed: {e}")

    # 2. Live query fallback
    pt = _get_intersection_point(session, intersection_id)
    if not pt:
        return []
    lat, lon = pt

    async def fetch_live():
        fdot = FDOTClient()
        gnv = GainesvilleClient()
        try:
            fdot_features = await fdot.query_traffic_monitoring_near(lat, lon, radius_m)
            gnv_features = await gnv.get_traffic_sites_near(lat, lon, radius_m)
            
            combined = []
            for f in fdot_features:
                attrs = f.get("attributes", {})
                geom = f.get("geometry", {})
                point = point_coordinates(geom)
                if point is None:
                    continue
                site_lat, site_lon = point
                dist = haversine_distance_m(lat, lon, site_lat, site_lon)
                if dist > radius_m:
                    continue
                combined.append({
                    "id": f"fdot:{attrs.get('COSITE') or attrs.get('OBJECTID')}",
                    "source_agency": "FDOT",
                    "source_site_id": attrs.get("COSITE") or str(attrs.get("OBJECTID")),
                    "roadway": attrs.get("SECTION_"),
                    "description": f"FDOT Traffic Monitoring Site ({attrs.get('SITETYPE', 'Continuous/Portable')})",
                    "latitude": site_lat,
                    "longitude": site_lon,
                    **nearby_relation(dist, "monitoring site"),
                    "source_url": f.get("source_url", f"{fdot.base_url}/16"),
                    "aadt": attrs.get("AADT"),
                    "year": attrs.get("YEAR_")
                })
                
            for g in gnv_features:
                point = point_coordinates(g.get("the_geom"))
                if point is None:
                    continue
                site_lat, site_lon = point
                dist = haversine_distance_m(lat, lon, site_lat, site_lon)
                if dist > radius_m:
                    continue
                combined.append({
                    "id": f"gainesville:{g.get('station')}",
                    "source_agency": "City of Gainesville",
                    "source_site_id": g.get("station"),
                    "roadway": g.get("street", "Gainesville City Street"),
                    "description": f"Gainesville Traffic Count Station {g.get('station')} at {g.get('street', '')} (Block {g.get('block', '')})",
                    "latitude": site_lat,
                    "longitude": site_lon,
                    **nearby_relation(dist, "historical count site"),
                    "source_url": gnv.resource_url,
                    "dataset": "Gainesville Traffic Counts (historical)",
                    "annual_adt": {key[4:]: value for key, value in g.items() if key.startswith("adt_") and len(key) == 8 and key[4:].isdigit() and str(value).replace('.', '', 1).isdigit() and float(value) > 0},
                    "adt_2014": g.get("adt_2014"),
                    "adt_1314": g.get("adt_1314"),
                    "pkam": g.get("pkam_1314"),
                    "pkpm": g.get("pkpm_1314")
                })
                
            combined.sort(key=lambda s: s["distance_m"])
            return combined
        finally:
            await fdot.close()
            await gnv.close()

    try:
        try:
            return asyncio.run(fetch_live())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(fetch_live())
    except Exception as e:
        logger.error(f"Live traffic sites query failed: {e}")
        return []

def get_hourly_traffic_volume(
    session: Optional[Session],
    site_id: Any,
    observation_date: date | None = None,
    start_time: time | None = None,
    end_time: time | None = None,
) -> list[dict]:
    """Get hourly traffic volume observations from database."""
    if session is not None and isinstance(site_id, int) and not isinstance(site_id, bool):
        try:
            params: dict[str, Any] = {"site_id": site_id}
            where_clauses = ["traffic_site_id = :site_id"]
            
            if observation_date:
                where_clauses.append("observation_date = :obs_date")
                params["obs_date"] = observation_date
            if start_time:
                where_clauses.append("start_time >= :start_time")
                params["start_time"] = start_time
            if end_time:
                where_clauses.append("end_time <= :end_time")
                params["end_time"] = end_time
                
            where_sql = " AND ".join(where_clauses)
            sql = f"""
                SELECT id, traffic_site_id, source_id, observation_date, start_time, end_time, volume, unit
                FROM traffic_observations
                WHERE {where_sql}
                ORDER BY observation_date ASC, start_time ASC
            """
            result = session.execute(text(sql), params)
            return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.warning(f"Database query for hourly traffic observations failed: {e}")
            
    # Neither FDOT FeatureServer nor Gainesville Open Data publishes 24-hr breakdown hourly bin feeds for general sites in these REST endpoints.
    # Return empty list to signal UNAVAILABLE as strictly mandated by the build guide rules!
    return []

def get_aadt_near_intersection(
    session: Optional[Session],
    intersection_id: int,
    radius_m: float = 500,
) -> list[dict]:
    """Find AADT roadway segments near an intersection."""
    # 1. Try local DB
    if session is not None:
        try:
            sql = """
                SELECT rs.id, rs.source_object_id, rs.roadway, rs.aadt, rs.aadt_year,
                       ds.agency AS source_agency, ds.dataset_name AS dataset, ds.source_url,
                       rs.roadway IS NOT NULL AND rs.roadway IN (i.roadway, i.intersecting_roadway) AS roadway_match,
                       ST_Distance(geography(rs.geometry), geography(i.geometry)) AS distance_m
                FROM intersections i
                JOIN roadway_segments rs ON ST_DWithin(geography(rs.geometry), geography(i.geometry), :radius)
                JOIN data_sources ds ON ds.id = rs.source_id
                WHERE i.source_object_id = :intersection_id
                  AND i.source_id IN (SELECT id FROM data_sources WHERE agency = 'FDOT' AND dataset_name = 'RCI Intersections')
                  AND rs.aadt IS NOT NULL AND rs.aadt >= 0
                ORDER BY distance_m ASC
            """
            result = session.execute(text(sql), {"intersection_id": str(intersection_id), "radius": radius_m})
            db_res = [dict(row._mapping) for row in result]
            if db_res:
                return _decorate_db_records(db_res, "AADT roadway segment")
        except Exception as e:
            logger.warning(f"Database AADT query failed: {e}")

    # 2. Live FDOT AADT query
    pt = _get_intersection_point(session, intersection_id)
    if not pt:
        return []
    lat, lon = pt

    async def fetch_live():
        fdot = FDOTClient()
        try:
            features = await fdot.query_aadt_near(lat, lon, radius_m)
            segments = []
            for f in features:
                attrs = f.get("attributes", {})
                aadt_val = attrs.get("AADT")
                dist = geometry_distance_m(lat, lon, f.get("geometry"))
                if dist is None or dist > radius_m:
                    continue
                if aadt_val is not None and isinstance(aadt_val, (int, float)) and aadt_val >= 0:
                    segments.append({
                        "id": attrs.get("OBJECTID"),
                        "roadway": attrs.get("ROADWAY") or "Unknown Roadway",
                        "aadt": int(aadt_val),
                        "aadt_year": attrs.get("YEAR_"),
                        "desc_from": attrs.get("DESC_FRM"),
                        "desc_to": attrs.get("DESC_TO"),
                        **nearby_relation(dist, "AADT roadway segment"),
                        "source_url": f"{fdot.base_url}/0",
                        "source_site_id": attrs.get("COSITE"),
                        "source_geometry": f.get("geometry"),
                        "source_agency": "FDOT",
                        "dataset": "FDOT Annual Average Daily Traffic"
                    })
            segments.sort(key=lambda segment: segment["distance_m"])
            return segments
        finally:
            await fdot.close()

    try:
        try:
            return asyncio.run(fetch_live())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(fetch_live())
    except Exception as e:
        logger.error(f"Live AADT query failed: {e}")
        return []

def get_signal_info_near_intersection(
    session: Optional[Session],
    intersection_id: int,
    radius_m: float = 250,
) -> list[dict]:
    """Find traffic signals near an intersection."""
    # 1. Try local DB
    if session is not None:
        try:
            sql = """
                SELECT ts.id, ts.source_signal_id, ts.signal_type, ts.roadway,
                       ds.agency AS source_agency, ds.dataset_name AS dataset, ds.source_url,
                       ts.roadway IS NOT NULL AND ts.roadway IN (i.roadway, i.intersecting_roadway) AS roadway_match,
                       ST_Distance(geography(ts.geometry), geography(i.geometry)) AS distance_m
                FROM intersections i
                JOIN traffic_signals ts ON ST_DWithin(geography(ts.geometry), geography(i.geometry), :radius)
                JOIN data_sources ds ON ds.id = ts.source_id
                WHERE i.source_object_id = :intersection_id
                  AND i.source_id IN (SELECT id FROM data_sources WHERE agency = 'FDOT' AND dataset_name = 'RCI Intersections')
                ORDER BY distance_m ASC
            """
            result = session.execute(text(sql), {"intersection_id": str(intersection_id), "radius": radius_m})
            db_res = [dict(row._mapping) for row in result]
            if db_res:
                return _decorate_db_records(db_res, "signal inventory point")
        except Exception as e:
            logger.warning(f"Database traffic signals query failed: {e}")

    # 2. Live FDOT Traffic Signals query
    pt = _get_intersection_point(session, intersection_id)
    if not pt:
        return []
    lat, lon = pt

    async def fetch_live():
        fdot = FDOTClient()
        try:
            features = await fdot.query_traffic_signals_near(lat, lon, radius_m)
            signals = []
            for f in features:
                attrs = f.get("attributes", {})
                geom = f.get("geometry", {})
                point = point_coordinates(geom)
                if point is None:
                    continue
                sig_lat, sig_lon = point
                dist = haversine_distance_m(lat, lon, sig_lat, sig_lon)
                if dist > radius_m:
                    continue
                signals.append({
                    "id": attrs.get("FID") or attrs.get("SIGNALID"),
                    "signal_type": attrs.get("VALUE_") or "Traffic Control Signal",
                    "roadway": attrs.get("RDWYID") or attrs.get("SDESTRET") or "FDOT Signalized Corridor",
                    **nearby_relation(dist, "signal inventory point"),
                    "source_url": "https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/Traffic_Signal_Locations_TDA/FeatureServer/0",
                    "source_agency": "FDOT",
                    "dataset": "Traffic Signal Locations TDA"
                })
            signals.sort(key=lambda s: s["distance_m"])
            return signals
        finally:
            await fdot.close()

    try:
        try:
            return asyncio.run(fetch_live())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(fetch_live())
    except Exception as e:
        logger.error(f"Live traffic signals query failed: {e}")
        return []

def get_available_data_near_intersection(
    session: Optional[Session],
    intersection_id: int,
    radius_m: float = 500,
) -> dict:
    """Get summary of all available data near an intersection."""
    sites = find_traffic_sites_near_intersection(session, intersection_id, radius_m)
    segments = get_aadt_near_intersection(session, intersection_id, radius_m)
    signals = get_signal_info_near_intersection(session, intersection_id, 250)
    
    return {
        "intersection_id": intersection_id,
        "traffic_sites_count": len(sites),
        "closest_traffic_site": sites[0] if sites else None,
        "aadt_segments_count": len(segments),
        "closest_aadt_segment": segments[0] if segments else None,
        "traffic_signals_count": len(signals),
        "closest_signal": signals[0] if signals else None
    }
