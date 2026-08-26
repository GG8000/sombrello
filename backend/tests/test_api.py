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

def gpx_with(trackpoints : list[dict]) -> str:
    xml = "".join([
            f"""
            <trkpt lat="{tp['lat']}" lon="{tp['lon']}">
                <ele>{tp['elevation_m']}</ele>
                <time>{tp['timestamp']}</time>
            </trkpt>
            """ for tp in trackpoints
            ]
        )
    return gpx_test_string.format(trackpoints_xml=xml)

VALID_TRACKPOINTS = [
    {"lat" : 47.70, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"},
    {"lat" : 47.71, "lon" : 13.05, "elevation_m" : 425.0, "timestamp" : "2027-06-21T12:05:00+00:00"},
    {"lat" : 47.72, "lon" : 13.05, "elevation_m" : 426.0, "timestamp" : "2027-06-21T12:08:00+00:00"},
    {"lat" : 47.73, "lon" : 13.05, "elevation_m" : 427.0, "timestamp" : "2027-06-21T12:09:00+00:00"},

]


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def route_id(client):
    response = client.post(
        "/routes",
        content=gpx_with(trackpoints=VALID_TRACKPOINTS),
        headers={"Content-Type": "application/xml"}
    )
    
    assert response.status_code == 201
    return response.json()["route_id"]
    

def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status" : "ok"}
    
def test_post_routes_gpx_returns_route_id(client):
    trackpoints = [
        {"lat" : 47.70, "lon" : 13.04, "elevation_m" : 424.0, "timestamp" : "2027-06-21T12:00:00+00:00"}
    ]
    
    response = client.post(
        "/routes", 
        content=gpx_with(trackpoints),
        headers={"Content-Type": "application/xml"} 
    )
    
    assert response.status_code == 201
    assert "route_id" in response.json()
    
def test_get_route_returns_enriched_trackpoints(client, route_id):
    response = client.get(f"/routes/{route_id}")
    assert response.status_code == 200
    
    
def test_unknown_route_returns_404(client):
    response = client.get("/routes/does-not-exist")
    assert response.status_code == 404
    
@pytest.mark.parametrize("lat", [3000.01,90.01,-90.1])
def test_invalid_latitude_returns_422(client, lat):
    response = client.post(
        "/routes", 
        content=gpx_with([{
            "lat" : lat, 
            "lon" : 13.04, 
            "elevation_m" : 424.0, 
            "timestamp" : "2027-06-21T12:00:00+00:00"
            }]),
        headers={"Content-Type": "application/xml"}
    ) 
    assert response.status_code == 422
    
@pytest.mark.parametrize("lon", [181.10, -231, 1000])
def test_invalid_longitude_returns_422(client, lon):
    response = client.post(
        "/routes", 
        content=gpx_with([{
            "lat" : 49.01, 
            "lon" : lon, 
            "elevation_m" : 424.0, 
            "timestamp" : "2027-06-21T12:00:00+00:00"}]),
        headers={"Content-Type": "application/xml"}
    ) 
    assert response.status_code == 422
    
def test_get_enriched_route_json(client, route_id):
    enriched_response = client.get(
        f"/routes/{route_id}/json",
    )
    expected = {"sun_elevation_deg", "shadow_index", "uv_index", "uv_effective"}
    for tp in enriched_response.json():
        assert expected <= tp.keys() # <= means subset of 
    
    
@pytest.mark.parametrize("content", [
    "This is no xml",
    "<BLABLABLA>",
    "<!XML>",
    "<>"
])
def test_wrong_formatted_xml(client,content):
    response = client.post("/routes", content=content, headers={"Content-Type": "application/gpx+xml"})
    assert response.status_code == 422
    
def test_no_trackpoints_422(client):
    response = client.post("/routes", 
                           content="<?xml version='1.0' encoding='UTF-8'?>\n<gpx version=\"1.1\" creator=\"https://www.komoot.de\" xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\">\n  <metadata>\n    <name>Testroute-Sombrello</name>\n    <author>\n      <link href=\"https://www.komoot.de\">\n        <text>komoot</text>\n        <type>text/html</type>\n      </link>\n    </author>\n  </metadata>\n  <wpt lat=\"48.545926\" lon=\"9.057296\">\n    <name>T\u00fcbingen Ulmenweg</name>\n    <sym>Flag, Blue</sym>\n  </wpt>\n  <wpt lat=\"48.551085\" lon=\"9.050721\">\n    <name>Naturlehrpfad im Naturpark Sch\u00f6nbuch</name>\n    <sym>Flag, Blue</sym>\n  </wpt>\n  <trk>\n    <name>Testroute-Sombrello</name>\n    <type>hike</type>\n    <trkseg></gpx>",
                           headers={"Content-Type": "application/gpx+xml"})
    assert response.status_code == 422