import pytest
from app.data.fdot_client import FDOTClient
from app.data.gainesville_client import GainesvilleClient

@pytest.mark.asyncio
async def test_fdot_client_intersections_query():
    client = FDOTClient()
    try:
        results = await client.query_intersections_near(29.6516, -82.3248, 500)
        assert isinstance(results, list)
        assert len(results) > 0
        attrs = results[0].get("attributes", {})
        assert "OBJECTID" in attrs
        assert "ROADWAY" in attrs
    finally:
        await client.close()

@pytest.mark.asyncio
async def test_gainesville_client_traffic_sites_query():
    client = GainesvilleClient()
    try:
        sites = await client.get_traffic_sites_near(29.6516, -82.3248, 1000)
        assert isinstance(sites, list)
        assert len(sites) > 0
        first = sites[0]
        assert "station" in first
        assert "the_geom" in first
    finally:
        await client.close()
