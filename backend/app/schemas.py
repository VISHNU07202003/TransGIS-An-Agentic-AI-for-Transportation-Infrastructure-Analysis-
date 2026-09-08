from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
from datetime import date as dt_date, time as dt_time, datetime as dt_datetime

class MapLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    source: Literal["map_click", "geocoder"]

class IntersectionCandidate(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    distance_m: float

class TrafficQuery(BaseModel):
    metric: Literal["hourly_traffic_volume", "aadt", "signal_status", "general_info"]
    date: Optional[dt_date] = None
    start_time: Optional[dt_time] = None
    end_time: Optional[dt_time] = None

class Provenance(BaseModel):
    agency: str
    dataset: str
    source_url: str
    record_id: Optional[str] = None
    observation_date: Optional[dt_date] = None
    retrieval_timestamp: dt_datetime
    spatial_relation: Optional[str] = None

class TrafficResult(BaseModel):
    value: Optional[float] = None
    unit: str = "vehicles/hour"
    result_type: Literal["DIRECT_OBSERVATION", "NEARBY_OBSERVATION", "DERIVED_FROM_SOURCE_DATA", "UNAVAILABLE"]
    provenance: Optional[Provenance] = None
    message: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    location: MapLocation | None = None
    selected_intersection_id: int | None = None
    conversation_id: str | None = None

class MapFeature(BaseModel):
    type: str = "Feature"
    geometry: dict
    properties: dict

class ChatResponse(BaseModel):
    status: Literal["answer", "needs_clarification", "no_data", "error"]
    message: str
    result: TrafficResult | None = None
    candidates: list[IntersectionCandidate] | None = None
    map_features: list[MapFeature] | None = None
    conversation_id: str | None = None

class GeocodeResult(BaseModel):
    latitude: float
    longitude: float
    display_name: str
    confidence: float | None = None

class HealthResponse(BaseModel):
    status: str
    database: str
    fdot: str
    gainesville: str
    navigator: str

class NearbyIntersectionsRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_m: float = Field(default=250, ge=25, le=2000)
