import json

from app.agents import tools
from app.agents.tool_registry import AGENT_TOOLS
from app.schemas import IntersectionCandidate


def test_tool_registry_schemas():
    names = [tool["function"]["name"] for tool in AGENT_TOOLS]
    assert len(names) == len(set(names)), "Duplicate tool names make dispatch ambiguous"
    assert set(names) == set(tools.TOOL_FUNCTIONS)
    for tool in AGENT_TOOLS:
        function = tool["function"]
        assert function["description"]
        assert function["parameters"]["type"] == "object"


def test_execute_unknown_tool():
    result = json.loads(tools.execute_tool("nonexistent_tool", {}, None))
    assert "Unknown tool" in result["error"]


def test_execute_find_intersections_tool(monkeypatch):
    candidate = IntersectionCandidate(id=123, name="Fixture intersection", latitude=29.6516,
                                      longitude=-82.3248, distance_m=12.5)
    calls = []

    def find(session, latitude, longitude, radius_m):
        calls.append((session, latitude, longitude, radius_m))
        return [candidate]

    monkeypatch.setattr(tools, "find_nearby_intersections", find)
    result = json.loads(tools.execute_tool("find_nearby_intersections",
                        {"latitude": 29.6516, "longitude": -82.3248, "radius_m": 500}, None))
    assert result == [candidate.model_dump()]
    assert calls == [(None, 29.6516, -82.3248, 500)]


def test_missing_coordinates_rejected_before_query(monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("Invalid arguments reached GIS execution")

    monkeypatch.setattr(tools, "find_nearby_intersections", unexpected)
    result = json.loads(tools.execute_tool("find_nearby_intersections", {}, None))
    assert "Invalid arguments" in result["error"]
