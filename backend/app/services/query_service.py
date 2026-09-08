from sqlalchemy.orm import Session
from datetime import datetime
from app.gis.intersection import find_nearby_intersections, resolve_intersection, get_intersection_details
from app.gis.traffic import (
    find_traffic_sites_near_intersection,
    get_hourly_traffic_volume,
    get_aadt_near_intersection,
    get_signal_info_near_intersection,
    get_available_data_near_intersection,
)

def handle_location_query(
    session: Session,
    lat: float,
    lon: float,
    radius_m: float = 250,
) -> dict:
    """Handle the initial location -> intersection resolution."""
    candidates = find_nearby_intersections(session, lat, lon, radius_m)
    resolution = resolve_intersection(candidates)
    return resolution

def handle_traffic_volume_query(
    session: Session,
    intersection_id: int,
    date_str: str | None = None,
    start_time_str: str | None = None,
    end_time_str: str | None = None,
) -> dict:
    """Handle hourly traffic volume query for a selected intersection."""
    sites = find_traffic_sites_near_intersection(session, intersection_id)
    if not sites:
        return {"status": "no_data", "message": "No traffic sites near intersection"}
        
    closest_site = sites[0]
    
    obs_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time() if start_time_str else None
    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time() if end_time_str else None
    
    volumes = get_hourly_traffic_volume(
        session, closest_site["id"], obs_date, start_time, end_time
    )
    
    return {
        "status": "success",
        "site": closest_site,
        "observations": volumes
    }

def handle_aadt_query(
    session: Session,
    intersection_id: int,
) -> dict:
    segments = get_aadt_near_intersection(session, intersection_id)
    if not segments:
        return {"status": "no_data", "message": "No AADT segments near intersection"}
    return {"status": "success", "segments": segments}

def handle_signal_query(
    session: Session,
    intersection_id: int,
) -> dict:
    signals = get_signal_info_near_intersection(session, intersection_id)
    if not signals:
        return {"status": "no_data", "message": "No signals near intersection"}
    return {"status": "success", "signals": signals}

def handle_available_data_query(
    session: Session,
    intersection_id: int,
) -> dict:
    summary = get_available_data_near_intersection(session, intersection_id)
    return {"status": "success", "summary": summary}
