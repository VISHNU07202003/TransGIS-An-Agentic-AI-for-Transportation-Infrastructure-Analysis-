"""Address search and pin labels. Geocoding is not a traffic data source."""
from collections import OrderedDict
from time import monotonic

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/api/places", tags=["places"])
_cache: OrderedDict[tuple, tuple[float, list[dict]]] = OrderedDict()


class PlaceResult(BaseModel):
    latitude: float
    longitude: float
    name: str
    display_name: str
    locality: str


def normalize_place(feature: dict) -> dict | None:
    geometry = feature.get("geometry") or {}
    coordinates = geometry.get("coordinates") or []
    if geometry.get("type") != "Point" or len(coordinates) < 2:
        return None
    try:
        lon, lat = float(coordinates[0]), float(coordinates[1])
    except (ValueError, TypeError):
        return None
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        return None
    p = feature.get("properties") or {}
    city = p.get("city") or p.get("town") or p.get("village") or p.get("district")
    # Cities often have a name but no parent city field.
    if not city and p.get("osm_key") == "place":
        city = p.get("name")
    locality = ", ".join(str(x) for x in [city or p.get("county"), p.get("state")] if x)
    street = " ".join(str(x) for x in [p.get("housenumber"), p.get("street")] if x)
    name = p.get("name") or street or city or p.get("county") or "Selected place"
    parts = list(dict.fromkeys(str(x) for x in [name, street, city, p.get("state"), p.get("postcode"), p.get("country")] if x))
    return {"latitude": lat, "longitude": lon, "name": str(name),
            "display_name": ", ".join(parts), "locality": locality or str(p.get("country") or name)}


async def query_places(path: str, params: dict) -> list[dict]:
    key = (path, tuple(sorted(params.items())))
    cached = _cache.get(key)
    if cached and monotonic() - cached[0] < 3600:
        _cache.move_to_end(key)
        return cached[1]
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(
                f"{get_settings().place_geocoder_base_url.rstrip('/')}/{path}",
                params=params,
                headers={"User-Agent": "TransGIS/1.0 (transportation research prototype)"},
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict) or not isinstance(data.get("features"), list):
                raise ValueError("Unexpected geocoder response")
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(status_code=503, detail="Place lookup is temporarily unavailable.") from exc
    places = []
    seen = set()
    for feature in data["features"]:
        if not isinstance(feature, dict):
            continue
        place = normalize_place(feature)
        if place:
            identity = (place["latitude"], place["longitude"], place["display_name"])
            if identity not in seen:
                places.append(place)
                seen.add(identity)
    _cache[key] = (monotonic(), places)
    _cache.move_to_end(key)
    while len(_cache) > 128:
        _cache.popitem(last=False)
    return places


@router.get("/search", response_model=list[PlaceResult])
async def search_places(
    q: str = Query(..., min_length=3, max_length=200),
    lat: float = Query(default=29.6516, ge=-90, le=90),
    lon: float = Query(default=-82.3248, ge=-180, le=180),
):
    if len(q.strip()) < 3:
        return []
    return await query_places("api/", {"q": q.strip(), "lat": lat, "lon": lon, "limit": 5, "lang": "en"})


@router.get("/reverse", response_model=PlaceResult)
async def reverse_place(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180)):
    places = await query_places("reverse", {"lat": lat, "lon": lon, "limit": 1, "lang": "en"})
    if not places:
        raise HTTPException(status_code=404, detail="No place name found for this pin.")
    return places[0]
