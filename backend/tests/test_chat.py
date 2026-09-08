import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_chat_location_resolution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "What intersections are here?",
            "location": {
                "latitude": 29.6516,
                "longitude": -82.3248,
                "source": "map_click"
            },
            "conversation_id": "test-uuid"
        }
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["answer", "needs_clarification"]
        assert len(data.get("candidates") or []) > 0

@pytest.mark.asyncio
async def test_chat_signal_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Near University Ave / Main St intersection in Gainesville
        payload = {
            "message": "Is this intersection signalized?",
            "location": {
                "latitude": 29.6516,
                "longitude": -82.3248,
                "source": "map_click"
            },
            "selected_intersection_id": 80329,
            "conversation_id": "test-uuid-2"
        }
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "answer"
        assert "signal" in data["message"].lower()

@pytest.mark.asyncio
async def test_chat_hourly_traffic_volume_no_data_policy():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "What was the traffic volume from 5 PM to 6 PM here?",
            "selected_intersection_id": 80329,
            "conversation_id": "test-uuid-3"
        }
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Per data rules, must return no_data when no hourly observation exists rather than fabricating
        assert data["status"] == "no_data"
        assert "no authoritative hourly" in data["message"].lower()
        assert data["result"]["result_type"] == "UNAVAILABLE"

@pytest.mark.asyncio
async def test_chat_how_many_vehicles_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "how many vehicles go in this intersection",
            "selected_intersection_id": 80329,
            "conversation_id": "test-uuid-4"
        }
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "answer"
        assert "aadt" in data["message"].lower() or "vehicles/day" in data["message"].lower()
        assert data["result"]["value"] is not None

@pytest.mark.asyncio
async def test_chat_traffic_jam_realtime_refusal():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "is there a traffic jam in this intersection?",
            "selected_intersection_id": 80329,
            "conversation_id": "test-uuid-5"
        }
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "answer"
        assert "does not monitor real-time" in data["message"].lower() or "out of scope" in data["message"].lower()

@pytest.mark.asyncio
async def test_geocode_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/geocode?address=University+Ave")
        assert response.status_code == 200
        data = response.json()
        assert "latitude" in data
        assert "longitude" in data
        assert 29.5 < data["latitude"] < 29.8
        assert -82.5 < data["longitude"] < -82.2

