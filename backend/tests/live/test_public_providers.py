"""Small opt-in public service checks: no NaviGator calls or database writes."""
import httpx
import pytest

from app.config import get_settings

pytestmark = [pytest.mark.live, pytest.mark.asyncio]


async def test_fdot_intersection_layer_schema():
    settings = get_settings()
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"{settings.fdot_rci_base_url}/6", params={"f": "json"})
        response.raise_for_status()
    metadata = response.json()
    assert "error" not in metadata, metadata.get("error")
    fields = {field["name"] for field in metadata["fields"]}
    assert {"OBJECTID", "ROADWAY"} <= fields
    assert metadata["geometryType"] == "esriGeometryPoint"


async def test_gainesville_traffic_site_contract():
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get("https://data.cityofgainesville.org/resource/v2qq-gus2.json",
                                    params={"$limit": 1})
        response.raise_for_status()
    rows = response.json()
    assert isinstance(rows, list) and rows, "Provider returned no records; inspect dataset status"
    assert "station" in rows[0] and "the_geom" in rows[0]


async def test_photon_florida_search_contract():
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(f"{get_settings().place_geocoder_base_url.rstrip('/')}/api/",
                                    params={"q": "Ocala Florida", "limit": 1, "lang": "en"})
        response.raise_for_status()
    features = response.json()["features"]
    assert features and features[0]["geometry"]["type"] == "Point"
    assert len(features[0]["geometry"]["coordinates"]) >= 2
