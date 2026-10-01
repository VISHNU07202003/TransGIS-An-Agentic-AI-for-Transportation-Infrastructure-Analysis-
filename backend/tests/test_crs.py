import pytest
from pyproj import CRS, Transformer

def test_crs_properties_florida_north():
    # Verify NAD83(2011) / Florida North
    crs_6440 = CRS.from_epsg(6440)
    assert "NAD83(2011) / Florida North" in crs_6440.name
    # Verify units are metres, not feet
    assert crs_6440.axis_info[0].unit_name == "metre"
    assert crs_6440.axis_info[1].unit_name == "metre"

    # Verify NAD83(HARN) / Florida North
    crs_2779 = CRS.from_epsg(2779)
    assert "NAD83(HARN) / Florida North" in crs_2779.name
    assert crs_2779.axis_info[0].unit_name == "metre"
    assert crs_2779.axis_info[1].unit_name == "metre"

def test_crs_roundtrip_wgs84_to_florida_north():
    # Gainesville coords (approx)
    lat, lon = 29.6516, -82.3248
    
    transformer_to_proj = Transformer.from_crs("EPSG:4326", "EPSG:6440", always_xy=True)
    transformer_to_wgs84 = Transformer.from_crs("EPSG:6440", "EPSG:4326", always_xy=True)
    
    x, y = transformer_to_proj.transform(lon, lat)
    
    # Florida North (meters) typically has false easting of ~600k and false northing of ~0
    assert x > 0 and y > 0
    
    lon_back, lat_back = transformer_to_wgs84.transform(x, y)
    
    # Sub-millimeter tolerance check
    assert abs(lon - lon_back) < 1e-7
    assert abs(lat - lat_back) < 1e-7

def test_crs_distance_calculation():
    # Two points on W University Ave ~100m apart
    lon1, lat1 = -82.3412, 29.6514
    lon2, lat2 = -82.3422, 29.6514
    
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:6440", always_xy=True)
    x1, y1 = transformer.transform(lon1, lat1)
    x2, y2 = transformer.transform(lon2, lat2)
    
    dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    
    # 0.001 degrees longitude at 29.6 degrees lat is roughly 96 meters
    assert 90.0 < dist < 100.0
