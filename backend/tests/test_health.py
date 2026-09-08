import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert data["fdot"] == "ok"
        assert data["gainesville"] == "ok"
        assert "navigator" in data

@pytest.mark.asyncio
async def test_data_sources_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/data/sources")
        assert response.status_code == 200
        sources = response.json()
        assert isinstance(sources, list)
        assert len(sources) >= 5
        agencies = [s["agency"] for s in sources]
        assert any("FDOT" in a or "Florida" in a for a in agencies)
        assert any("Gainesville" in a for a in agencies)
