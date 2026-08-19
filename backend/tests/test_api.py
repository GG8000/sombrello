import pytest
from fastapi.testclient import TestClient
from sombrello.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}
    
def test_post_routes_returns_route_id(client):
    response = client.post("/routes", json={
        "trackpoints" : [
            {"lat" : 47.70, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T13:00:00+00:00"}
        ]
    })
    assert response.status_code == 201
    assert response.json()["route_id"]
    
def test_get_route_returns_enriched_trackpoints(client):
    trackpoints = [
        {"lat" : 47.70, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
        {"lat" : 47.80, "lon" : 13.05, "elevation_m" : 430.0, "timestamp" : "2027-06-21T13:00:00+00:00"},
        {"lat" : 47.90, "lon" : 13.03, "elevation_m" : 444.0, "timestamp" : "2027-06-21T14:00:00+00:00"},
        {"lat" : 47.91, "lon" : 13.04, "elevation_m" : 432.0, "timestamp" : "2027-06-21T15:00:00+00:00"},
        {"lat" : 47.89, "lon" : 13.06, "elevation_m" : 443.0, "timestamp" : "2027-06-21T16:00:00+00:00"},
        {"lat" : 47.87, "lon" : 13.06, "elevation_m" : 410.0, "timestamp" : "2027-06-21T17:00:00+00:00"}
    ]
    created = client.post("/routes", json={"trackpoints" : trackpoints})
    route_id = created.json()["route_id"]
    
    response = client.get(f"/routes/{route_id}")
    assert response.status_code == 200
    
    point = response.json()["trackpoints"][0]
    assert point["uv_effective"] == pytest.approx(
        point["uv_index"] * (1 - point["shadow_index"])
    )
    
def test_unknown_route_returns_404(client):
    response = client.get("/routes/does-not-exist")
    assert response.status_code == 404
    

def test_invalid_latitude_returns_422(client):
    response = client.post("/routes", json={
        "trackpoints" : [
            {"lat" : 3000.70, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
        ]
    })
    assert response.status_code == 422
    
def test_invalid_longitude_returns_422(client):
    response = client.post("/routes", json={
        "trackpoints" : [
            {"lat" : 47.70, "lon" : 999.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
        ]
    })
    assert response.status_code == 422