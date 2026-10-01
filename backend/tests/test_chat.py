"""Behavioral agent tests: mocked source records, no model or public data calls."""
import pytest

from app.agents import agent as agent_module
from app.schemas import ChatRequest, IntersectionCandidate


class OfflineNavigator:
    def is_configured(self):
        return False


@pytest.fixture
def agent(monkeypatch):
    monkeypatch.setattr(agent_module, "NavigatorClient", OfflineNavigator)
    monkeypatch.setattr(agent_module, "get_intersection_details", lambda *args, **kwargs: {
        "id": 80329, "roadway": "26000000", "intersecting_roadway": "26010000",
        "lat": 29.6516, "lon": -82.3248, "latitude": 29.6516, "longitude": -82.3248,
    })
    monkeypatch.setattr(agent_module, "find_traffic_sites_near_intersection", lambda *args, **kwargs: [])
    monkeypatch.setattr(agent_module, "get_aadt_near_intersection", lambda *args, **kwargs: [])
    monkeypatch.setattr(agent_module, "get_signal_info_near_intersection", lambda *args, **kwargs: [])
    monkeypatch.setattr(agent_module, "get_available_data_near_intersection", lambda *args, **kwargs: {
        "traffic_signals_count": 0, "aadt_segments_count": 0, "traffic_sites_count": 0,
    })
    return agent_module.TransportationAgent()


def ask(agent, message, **kwargs):
    return agent.process_query(ChatRequest(message=message, conversation_id="fixture-conversation",
                                           **kwargs), None)


def test_chat_location_resolution(agent, monkeypatch):
    candidate = IntersectionCandidate(id=80329, name="Fixture intersection", latitude=29.6516,
                                      longitude=-82.3248, distance_m=12.5)
    monkeypatch.setattr(agent_module, "find_nearby_intersections", lambda *args, **kwargs: [candidate])
    response = ask(agent, "What intersections are here?",
                   location={"latitude": 29.6516, "longitude": -82.3248, "source": "map_click"})
    assert response.status == "answer"
    assert response.candidates == [candidate]
    assert response.conversation_id == "fixture-conversation"


def test_chat_close_candidates_require_selection(agent, monkeypatch):
    candidates = [
        IntersectionCandidate(id=1, name="First", latitude=29.65, longitude=-82.32, distance_m=45),
        IntersectionCandidate(id=2, name="Second", latitude=29.65, longitude=-82.32, distance_m=55),
    ]
    monkeypatch.setattr(agent_module, "find_nearby_intersections", lambda *args, **kwargs: candidates)
    response = ask(agent, "What intersections are here?",
                   location={"latitude": 29.65, "longitude": -82.32, "source": "map_click"})
    assert response.status == "needs_clarification"
    assert response.candidates == candidates


def test_hourly_request_never_substitutes_aadt(agent, monkeypatch):
    monkeypatch.setattr(agent_module, "get_aadt_near_intersection", lambda *args, **kwargs: [{
        "id": 42, "aadt": 12500, "aadt_year": 2024, "distance_m": 42.0, "roadway": "26000000",
        "association_status": "proximity_only", "source_agency": "FDOT",
    }])
    response = ask(agent, "What was the hourly traffic volume from 5 PM to 6 PM here?",
                   selected_intersection_id=80329)
    assert response.status == "no_data"
    assert response.result.result_type == "UNAVAILABLE"
    assert response.result.value is None
    assert "hour" in response.message.lower()


def test_aadt_uses_exact_source_value_and_provenance(agent, monkeypatch):
    monkeypatch.setattr(agent_module, "get_aadt_near_intersection", lambda *args, **kwargs: [{
        "id": 42, "aadt": 12500, "aadt_year": 2024, "distance_m": 42.0, "roadway": "26000000",
        "source_agency": "FDOT", "dataset": "Annual Average Daily Traffic",
        "association_status": "proximity_only",
        "source_url": "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0",
    }])
    response = ask(agent, "What is the AADT?", selected_intersection_id=80329)
    assert response.status == "answer"
    assert response.result.value == 12500
    assert response.result.unit == "vehicles/day"
    assert response.result.provenance.record_id == "42"
    assert response.result.provenance.agency == "FDOT"


def test_live_congestion_query_does_not_infer_peak_delays_from_aadt(agent, monkeypatch):
    monkeypatch.setattr(agent_module, "get_aadt_near_intersection", lambda *args, **kwargs: [{
        "id": 42, "aadt": 25000, "aadt_year": 2024, "distance_m": 42.0, "roadway": "26000000",
    }])
    response = ask(agent, "Is there a traffic jam right now?", selected_intersection_id=80329)
    text = response.message.lower()
    assert any(word in text for word in ("live", "real-time", "real time"))
    assert "estimated assumption" not in text
    assert "noticeable delays" not in text
    assert "7:30" not in text
    assert response.result is None or response.result.value is None


def test_missing_aadt_is_explicit_no_data(agent):
    response = ask(agent, "What is the AADT?", selected_intersection_id=80329)
    assert response.status == "no_data"
    assert response.result.result_type == "UNAVAILABLE"
    assert response.result.value is None


def test_no_location_invites_florida_selection(agent):
    response = ask(agent, "Tell me about this location")
    assert response.status in ("answer", "needs_clarification")
    assert "gainesville" in response.message.lower()
