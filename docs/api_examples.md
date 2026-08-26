# API Usage Examples

Start server from root directory sombrello/ with: `python -m uvicorn sombrello.api.main:app --reload`

# Add Route
This function is called, when we add a route to the dataset and this is then saved for the whole session with a unique ID
Request:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/routes' \
  -H 'Content-Type: application/xml' \
  --data-binary @`your_route_path.gpx`
```
Response:
```bash
INFO:     127.0.0.1:61191 - "POST /routes HTTP/1.1" 201 Created
```
```bash
{
  "route_id": "e2cc74bf-feae-4775-9b5b-9785173eb022"
}
```

# Retrieve Route as GPX
This function will retrieve a route based on an ID with enriched shadow data, so the shadow-index, uv-index and uv_effective-index per trackpoint. 

insert route_id
Request:
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/routes/e2cc74bf-feae-4775-9b5b-9785173eb022' \
  -H 'accept: application/json'
```
Response:
```bash
INFO:     127.0.0.1:61202 - "GET /routes/e2cc74bf-feae-4775-9b5b-9785173eb022 HTTP/1.1" 200 OK
```
```bash
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:sombrello="https://sombrello.example/gpx/v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" creator="https://www.komoot.de">
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
    <name>Tübingen Ulmenweg</name>
    <sym>Flag, Blue</sym>
  </wpt>
  <wpt lat="48.551085" lon="9.050721">
    <name>Naturlehrpfad im Naturpark Schönbuch</name>
    <sym>Flag, Blue</sym>
  </wpt>
  <trk>
    <trkseg>
      <trkpt lat="48.545937" lon="9.057275">
        <ele>480.894457</ele>
        <time>2026-08-25T15:02:57.983000Z</time>
        <extensions>
          <sombrello:sun_elevation_deg>31.212398338053223</sombrello:sun_elevation_deg>
          <sombrello:shadow_index>1.0</sombrello:shadow_index>
          <sombrello:uv_index>2.620425845563728</sombrello:uv_index>
          <sombrello:uv_effective>0.0</sombrello:uv_effective>
        </extensions>
      </trkpt>
      ...
      <trkpt lat="48.551075" lon="9.050706">
        <ele>485.596578</ele>
        <time>2026-08-25T15:20:13.258000Z</time>
        <extensions>
          <sombrello:sun_elevation_deg>28.5183442505008</sombrello:sun_elevation_deg>
          <sombrello:shadow_index>1.0</sombrello:shadow_index>
          <sombrello:uv_index>2.149643423693805</sombrello:uv_index>
          <sombrello:uv_effective>0.0</sombrello:uv_effective>
        </extensions>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
```

# Retrieve Route as GPX
This function will retrieve a route based on an ID with enriched shadow data, so the shadow-index, uv-index and uv_effective-index per trackpoint. 

insert route_id
Request:
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/routes/e2cc74bf-feae-4775-9b5b-9785173eb022/json' \
  -H 'accept: application/json'
```
Response:
```bash
INFO:     127.0.0.1:61209 - "GET /routes/e2cc74bf-feae-4775-9b5b-9785173eb022/json HTTP/1.1" 200 OK
```
```bash
[
  {
    "lat":48.545937,
    "lon":9.057275,
    "elevation_m":480.894457,
    "timestamp":"2026-08-25T15:02:57.983000Z",
    "sun_elevation_deg":31.212398338053223,
    "shadow_index":0.0,
    "uv_index":2.620425845563728,
    "uv_effective":2.620425845563728
  },
  ...
  {
    "lat":48.551075,
    "lon":9.050706,
    "elevation_m":485.596578,
    "timestamp":"2026-08-25T15:20:13.258000Z",
    "sun_elevation_deg":28.5183442505008,
    "shadow_index":1.0,
    "uv_index":2.149643423693805,
    "uv_effective":0.0
  }
]
```