"""Agent tool execution functions."""
import json
import logging
from typing import Optional, Union, Any
from pydantic import BaseModel, ValidationError, Field
from sqlalchemy.orm import Session

from app.gis.intersection import find_nearby_intersections, get_intersection_details
from app.gis.traffic import (
    find_traffic_sites_near_intersection,
    get_hourly_traffic_volume,
    get_aadt_near_intersection,
    get_signal_info_near_intersection,
    get_available_data_near_intersection,
)

logger = logging.getLogger(__name__)

class FindNearbyIntersectionsArgs(BaseModel):
    latitude: float
    longitude: float
    radius_m: Optional[float] = Field(default=250.0)

class GetIntersectionDetailsArgs(BaseModel):
    intersection_id: Union[int, str]

class FindNearbyTrafficSitesArgs(BaseModel):
    intersection_id: Union[int, str]
    radius_m: Optional[float] = Field(default=500.0)

class GetHourlyTrafficVolumeArgs(BaseModel):
    site_id: Union[int, str]
    date: Optional[str] = None
    start_time: Optional[str] = "00:00"
    end_time: Optional[str] = "23:59"

class GetSignalInformationArgs(BaseModel):
    intersection_id: Union[int, str]

class GetAadtNearIntersectionArgs(BaseModel):
    intersection_id: Union[int, str]

class GetAvailableDataArgs(BaseModel):
    intersection_id: Union[int, str]

def _to_int(val: Union[int, str]) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

def _execute_find_nearby_intersections(session: Optional[Session], **kwargs):
    args = FindNearbyIntersectionsArgs(**kwargs)
    candidates = find_nearby_intersections(session, args.latitude, args.longitude, args.radius_m or 250.0)
    return [c.model_dump() for c in candidates]

def _execute_get_intersection_details(session: Optional[Session], **kwargs):
    args = GetIntersectionDetailsArgs(**kwargs)
    return get_intersection_details(session, _to_int(args.intersection_id))

def _execute_find_nearby_traffic_sites(session: Optional[Session], **kwargs):
    args = FindNearbyTrafficSitesArgs(**kwargs)
    return find_traffic_sites_near_intersection(session, _to_int(args.intersection_id), args.radius_m or 500.0)

def _execute_get_hourly_traffic_volume(session: Optional[Session], **kwargs):
    args = GetHourlyTrafficVolumeArgs(**kwargs)
    from datetime import datetime
    obs_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else None
    start_t = datetime.strptime(args.start_time, "%H:%M").time() if args.start_time else None
    end_t = datetime.strptime(args.end_time, "%H:%M").time() if args.end_time else None
    res = get_hourly_traffic_volume(session, args.site_id, obs_date, start_t, end_t)
    if not res:
        return {
            "result_type": "UNAVAILABLE",
            "message": f"No authoritative hourly traffic-volume observation was found for site {args.site_id}."
        }
    return res

def _execute_get_signal_information(session: Optional[Session], **kwargs):
    args = GetSignalInformationArgs(**kwargs)
    return get_signal_info_near_intersection(session, _to_int(args.intersection_id))

def _execute_get_aadt_near_intersection(session: Optional[Session], **kwargs):
    args = GetAadtNearIntersectionArgs(**kwargs)
    return get_aadt_near_intersection(session, _to_int(args.intersection_id))

def _execute_get_available_data(session: Optional[Session], **kwargs):
    args = GetAvailableDataArgs(**kwargs)
    return get_available_data_near_intersection(session, _to_int(args.intersection_id))

TOOL_FUNCTIONS = {
    "find_nearby_intersections": _execute_find_nearby_intersections,
    "get_intersection_details": _execute_get_intersection_details,
    "find_nearby_traffic_sites": _execute_find_nearby_traffic_sites,
    "get_hourly_traffic_volume": _execute_get_hourly_traffic_volume,
    "get_signal_information": _execute_get_signal_information,
    "get_aadt_near_intersection": _execute_get_aadt_near_intersection,
    "get_available_data": _execute_get_available_data,
}

def execute_tool(tool_name: str, arguments: dict, session: Optional[Session]) -> str:
    """Execute a tool by name with validated arguments. Returns JSON string."""
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = TOOL_FUNCTIONS[tool_name](session=session, **arguments)
        return json.dumps(result, default=str)
    except ValidationError as e:
        logger.error(f"Tool validation error for {tool_name}: {e}")
        return json.dumps({"error": f"Invalid arguments: {e.errors()}"})
    except Exception as e:
        logger.error(f"Tool execution error: {tool_name}: {e}")
        return json.dumps({"error": str(e)})
