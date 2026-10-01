from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.api import routes_places as places


def feature(city="Ocala", coordinates=None):
    return {"geometry": {"type": "Point", "coordinates": coordinates or [-82.1401, 29.1872]},
            "properties": {"name": "Downtown", "city": city, "state": "Florida", "country": "United States"}}


def test_ocala_locality_is_not_gainesville():
    result = places.normalize_place(feature())
    assert result["locality"] == "Ocala, Florida"
    assert result["longitude"] == -82.1401
    assert "Gainesville" not in result["display_name"]


def test_city_feature_without_parent_city():
    city = feature()
    city["properties"] = {"name": "Ocala", "osm_key": "place", "osm_value": "city", "state": "Florida"}
    assert places.normalize_place(city)["locality"] == "Ocala, Florida"


@pytest.mark.parametrize("geometry", [{}, {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                                     {"type": "Point", "coordinates": [None, 29]},
                                     {"type": "Point", "coordinates": [500, 29]}])
def test_bad_geometry_is_not_a_suggestion(geometry):
    assert places.normalize_place({"geometry": geometry}) is None


@pytest.mark.asyncio
async def test_search_keeps_city_and_location_bias():
    with patch.object(places, "query_places", new_callable=AsyncMock, return_value=[]) as query:
        await places.search_places(q=" Ocala ", lat=29.65, lon=-82.32)
    assert query.call_args.args == ("api/", {"q": "Ocala", "lat": 29.65, "lon": -82.32, "limit": 5, "lang": "en"})


@pytest.mark.asyncio
async def test_reverse_no_match_does_not_invent_a_location():
    with patch.object(places, "query_places", new_callable=AsyncMock, return_value=[]):
        with pytest.raises(HTTPException) as exc:
            await places.reverse_place(lat=29, lon=-82)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_provider_failure_is_503():
    places._cache.clear()
    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, side_effect=httpx.ConnectError("offline")):
        with pytest.raises(HTTPException) as exc:
            await places.query_places("reverse", {"lat": 29, "lon": -82})
    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_duplicate_results_and_repeated_requests_are_cached():
    places._cache.clear()
    response = httpx.Response(200, json={"features": [feature(), feature()]}, request=httpx.Request("GET", "https://photon.komoot.io/api/"))
    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=response) as get:
        first = await places.query_places("api/", {"q": "Ocala"})
        second = await places.query_places("api/", {"q": "Ocala"})
    assert len(first) == 1
    assert second == first
    assert get.await_count == 1
    places._cache.clear()
