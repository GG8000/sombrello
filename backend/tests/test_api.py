import pytest
from fastapi.testclient import TestClient
from sombrello.api.main import app

gpx_test_string = """<?xml version='1.0' encoding='UTF-8'?>
    <gpx version="1.1" creator="https://www.komoot.de" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
    <metadata>
        <name>Testroute-Sombrello</name>
        <author>
        <link href="https://www.komoot.de">
        <text>komoot</text>
        <type>text/html</type>
        </link>
        </author>
        </metadata>
        <wpt lat="48.545926" lon="9.057296">
            <name>T\u00fcbingen Ulmenweg</name>
            <sym>Flag, Blue</sym>
        </wpt>
        <wpt lat="48.551085" lon="9.050721">
            <name>Naturlehrpfad im Naturpark Sch\u00f6nbuch</name>
            <sym>Flag, Blue</sym>
        </wpt>
        <trk>
            <name>Testroute-Sombrello</name>
            <type>hike</type>
            <trkseg>
                {trackpoints_xml}
            </trkseg> 
        </trk>
    </gpx>"""


@pytest.fixture
def client():
    return TestClient(app)

def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}
    
def test_post_routes_gpx_returns_route_id(client):
    trackpoints = [
            {"lat" : 47.70, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"}
        ]
    
    trackpoints_xml = "".join([
            f"""
            <trkpt lat="{tp['lat']}" lon="{tp['lon']}">
                <ele>{tp['elevation_m']}</ele>
                <time>{tp['timestamp']}</time>
            </trkpt>
            """ for tp in trackpoints
            ]
        )
    
    response = client.post(
        "/routes", 
        content=gpx_test_string.format(trackpoints_xml=trackpoints_xml),
        headers={"Content-Type": "application/xml"} 
    )
    
    assert response.status_code == 201
    assert "route_id" in response.json()
    
def test_get_route_returns_enriched_trackpoints(client):
    trackpoints = [
        {"lat" : 47.70, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
        {"lat" : 47.80, "lon" : 13.05, "elevation_m" : 430.0, "timestamp" : "2027-06-21T13:00:00+00:00"},
        {"lat" : 47.90, "lon" : 13.03, "elevation_m" : 444.0, "timestamp" : "2027-06-21T14:00:00+00:00"},
        {"lat" : 47.91, "lon" : 13.04, "elevation_m" : 432.0, "timestamp" : "2027-06-21T15:00:00+00:00"},
        {"lat" : 47.89, "lon" : 13.06, "elevation_m" : 443.0, "timestamp" : "2027-06-21T16:00:00+00:00"},
        {"lat" : 47.87, "lon" : 13.06, "elevation_m" : 410.0, "timestamp" : "2027-06-21T17:00:00+00:00"}
    ]
    
    trackpoints_xml = "".join([
            f"""
            <trkpt lat="{tp['lat']}" lon="{tp['lon']}">
                <ele>{tp['elevation_m']}</ele>
                <time>{tp['timestamp']}</time>
            </trkpt>
            """ for tp in trackpoints
            ]
        )
    
    created = client.post(
        "/routes", 
        content=gpx_test_string.format(trackpoints_xml=trackpoints_xml),
        headers={"Content-Type": "application/xml"}
    ) 
    route_id = created.json()["route_id"]
    
    response = client.get(f"/routes/{route_id}")
    assert response.status_code == 200
    
    gpx = response.content
    
    
    
def test_unknown_route_returns_404(client):
    response = client.get("/routes/does-not-exist")
    assert response.status_code == 404
    

def test_invalid_latitude_returns_422(client):
    trackpoints = [
        {"lat" : 3000.01, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
        {"lat" : 90.01, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
        {"lat" : -90.01, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
    ]
    
    trackpoints_xml = "".join([
            f"""
            <trkpt lat="{tp['lat']}" lon="{tp['lon']}">
                <ele>{tp['elevation_m']}</ele>
                <time>{tp['timestamp']}</time>
            </trkpt>
            """ for tp in trackpoints
            ]
        )
    
    response = client.post(
        "/routes", 
        content=gpx_test_string.format(trackpoints_xml=trackpoints_xml),
        headers={"Content-Type": "application/xml"}
    ) 
    assert response.status_code == 422
    
def test_invalid_longitude_returns_422(client):
    trackpoints = [
            {"lat" : 49.01, "lon" : 181.10, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
            {"lat" : 47.1, "lon" : -231, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
            {"lat" : 50.61, "lon" : 1000, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
    ]
    
    trackpoints_xml = "".join([
            f"""
            <trkpt lat="{tp['lat']}" lon="{tp['lon']}">
                <ele>{tp['elevation_m']}</ele>
                <time>{tp['timestamp']}</time>
            </trkpt>
            """ for tp in trackpoints
            ]
        )
    
    response = client.post(
        "/routes", 
        content=gpx_test_string.format(trackpoints_xml=trackpoints_xml),
        headers={"Content-Type": "application/xml"}
    ) 
    assert response.status_code == 422
    
def test_get_enriched_route_json(client):
    trackpoints = [
        {"lat" : 49.01, "lon" : 10.05, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
        {"lat" : 47.1, "lon" : 10.05, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
        {"lat" : 50.61, "lon" : 12.09, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
    ]
    
    trackpoints_xml = "".join([
            f"""
            <trkpt lat="{tp['lat']}" lon="{tp['lon']}">
                <ele>{tp['elevation_m']}</ele>
                <time>{tp['timestamp']}</time>
            </trkpt>
            """ for tp in trackpoints
            ]
        )
    
    response = client.post(
        "/routes", 
        content=gpx_test_string.format(trackpoints_xml=trackpoints_xml),
        headers={"Content-Type": "application/xml"}
    ) 
    assert response.status_code == 201
    route_id = response.json()["route_id"]
    
    enriched_response = client.get(
        f"/routes/{route_id}/json",
    )
    expected = {"sun_elevation_deg", "shadow_index", "uv_index", "uv_effective"}
    for tp in enriched_response.json():
        assert expected <= tp.keys() # <= means subset of 