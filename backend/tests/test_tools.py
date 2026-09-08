import json
import pytest
from app.agents.tools import execute_tool, TOOL_FUNCTIONS
from app.agents.tool_registry import AGENT_TOOLS

def test_tool_registry_schemas():
    assert len(AGENT_TOOLS) >= 7
    tool_names = [t["function"]["name"] for t in AGENT_TOOLS]
    assert "find_nearby_intersections" in tool_names
    assert "get_intersection_details" in tool_names
    assert "find_nearby_traffic_sites" in tool_names
    assert "get_hourly_traffic_volume" in tool_names
    assert "get_signal_information" in tool_names
    assert "get_aadt_near_intersection" in tool_names
    assert "get_available_data" in tool_names

def test_execute_unknown_tool():
    res_str = execute_tool("nonexistent_tool", {}, None)
    res = json.loads(res_str)
    assert "error" in res
    assert "Unknown tool" in res["error"]

def test_execute_find_intersections_tool():
    # Execute with valid Gainesville coordinates
    res_str = execute_tool("find_nearby_intersections", {"latitude": 29.6516, "longitude": -82.3248, "radius_m": 500}, None)
    res = json.loads(res_str)
    assert isinstance(res, list)
    assert len(res) > 0
    first = res[0]
    assert "id" in first
    assert "name" in first
    assert "latitude" in first
    assert "longitude" in first
    assert "distance_m" in first
