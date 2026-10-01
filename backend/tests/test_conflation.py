import pytest
from app.conflation.normalization import normalize_street_name, normalize_route_alias

def test_normalize_street_name_basic():
    assert normalize_street_name("W University Ave") == "WEST UNIVERSITY AVENUE"
    assert normalize_street_name("NW 13th St") == "NORTHWEST 13TH STREET"
    assert normalize_street_name("S. Main St.") == "SOUTH MAIN STREET"
    
def test_normalize_route_alias():
    assert normalize_route_alias("State Road 26") == "SR 26"
    assert normalize_route_alias("STATE ROAD 24") == "SR 24"
    assert normalize_route_alias("US Highway 441") == "US 441"
    assert normalize_route_alias("SR   222") == "SR 222"

def test_normalization_handles_none_or_empty():
    assert normalize_street_name("") is None
    assert normalize_street_name(None) is None
    assert normalize_route_alias("") is None
    assert normalize_route_alias(None) is None
