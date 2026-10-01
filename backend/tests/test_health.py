import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_liveness_never_probes_external_services():
    # The global offline guard makes an accidental DB/LLM/provider probe fail.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_source_catalog_preserves_state_and_municipal_provenance():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/data/sources")
    assert response.status_code == 200
    sources = response.json()
    assert isinstance(sources, list) and sources
    agencies = [source["agency"] for source in sources]
    assert any("FDOT" in agency or "Florida" in agency for agency in agencies)
    assert any("Gainesville" in agency for agency in agencies)


@pytest.mark.asyncio
async def test_invalid_map_coordinates_rejected_without_provider_query():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/intersections/nearby", params={"lat": 999, "lon": -82})
    assert response.status_code == 422
