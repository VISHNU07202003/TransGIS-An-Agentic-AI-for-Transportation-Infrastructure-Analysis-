"""Provider request/response contracts backed by small inspectable fixtures."""
import json
from urllib.parse import parse_qs

import httpx
import pytest

from app.data.fdot_client import FDOTClient
from app.data.gainesville_client import GainesvilleClient


@pytest.mark.asyncio
async def test_fdot_intersections_use_meter_radius_and_wgs84(public_transport):
    record = {"attributes": {"OBJECTID": 123, "ROADWAY": "26000000"},
              "geometry": {"x": -82.3248, "y": 29.6516}}
    calls = []

    def respond(request):
        calls.append(request)
        assert request.url.path.endswith("/6/query")
        params = parse_qs(request.content.decode())
        assert json.loads(params["geometry"][0]) == {"x": -82.3248, "y": 29.6516}
        assert params["geometryType"] == ["esriGeometryPoint"]
        assert params["distance"] == ["500"]
        assert params["units"] == ["esriSRUnit_Meter"]
        assert params["inSR"] == params["outSR"] == ["4326"]
        assert params["returnGeometry"] == ["true"]
        return httpx.Response(200, json={"features": [record]})

    public_transport(respond)
    client = FDOTClient()
    try:
        result = await client.query_intersections_near(29.6516, -82.3248, 500)
        assert len(result) == 1
        assert result[0]["attributes"]["ROADWAY"] == "26000000"
        assert result[0]["geometry"]["x"] == -82.3248
        assert "spatialReference" in result[0]["geometry"]
        assert len(calls) == 1
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_gainesville_uses_spatial_filter_and_preserves_source_fields(public_transport):
    row = {"station": "fixture-17", "the_geom": {"type": "Point", "coordinates": [-82.3248, 29.6516]},
           "adt_2014": "12500"}

    def respond(request):
        assert request.url.path.endswith("/resource/v2qq-gus2.json")
        assert request.url.params["$where"] == "within_circle(the_geom, 29.6516, -82.3248, 1000)"
        return httpx.Response(200, json=[row])

    public_transport(respond)
    client = GainesvilleClient()
    try:
        assert await client.get_traffic_sites_near(29.6516, -82.3248, 1000) == [row]
    finally:
        await client.close()
