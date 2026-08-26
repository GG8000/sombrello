# Interfaces & Data Contracts

Define these BEFORE implementing. Both team members must agree on any change.

## 1. Trackpoint
`{
    lat: float, 
    lon: float, 
    elevation_m: float, 
    timestamp: ISO-8601 UTC
}`

Ranges (enforced by pydantic in `sombrello/models/trackpoint.py`):
- `lat` in [-90.0, 90.0]
- `lon` in [-180.0, 180.0]
- `elevation_m` >= -500.0 (metres above sea level)
- `timestamp` must be timezone-aware; past timestamps are valid

## 2. Enriched Trackpoint
`{
    lat: float, 
    lon: float, 
    elevation_m: float, 
    timestamp: ISO-8601 UTC, 
    sun_elevation_deg: float
    shadow_index: float 
    uv_index: float 
    uv_effective: float 
}`

Ranges:
- `sun_elevation_deg` in [-90.0, 90.0] (negative = sun below horizon)
- `shadow_index` in [0.0, 1.0]
- `uv_index` >= 0.0
- `uv_effective` >= 0.0, always `uv_index * (1 - shadow_index)`

Inherits all fields and ranges from §1.

## 3. Solar output (Gedeon -> Emil)
`{
    azimuth_deg: float, 
    elevation_deg: float
}`
per trackpoint/timestamp

Signature: `sun_position(lat: float, lon: float, when: datetime) -> SolarPosition`
Frozen dataclass, field names fixed. `azimuth_deg` in [0.0, 360.0] (bearing from
north, clockwise), `elevation_deg` is the apparent elevation including
atmospheric refraction.

## 4. Shadow output (Emil -> API)
`shadow_index: float` in [0.0, 1.0] per trackpoint -> 0 - no shadow, 1 - shadow

Signature: `shadow_index(<current signature — confirm with Emil>) -> float`
Must be deterministic: same input twice returns the same value.
Acceptance criteria are the contract tests in `tests/test_shadow.py`.

## 5. GPX extensions
Namespaced extensions carrying `shadow_index` and `uv_effective`.

Namespace URI: `https://sombrello.example/gpx/v1`, prefix `sombrello`.
Written per `<trkpt>`, GPX version 1.1 (extensions do not exist in 1.0).
All four enriched fields are serialised as text:

```xml
<trkpt lat="47.70" lon="13.04">
  <ele>424.0</ele>
  <time>2026-06-21T12:00:00Z</time>
  <extensions>
    <sombrello:sun_elevation_deg>63.75</sombrello:sun_elevation_deg>
    <sombrello:shadow_index>0.5</sombrello:shadow_index>
    <sombrello:uv_index>9.85</sombrello:uv_index>
    <sombrello:uv_effective>4.92</sombrello:uv_effective>
  </extensions>
</trkpt>
```

## 6. Stub strategy
The API integrates the shadow algorithm as a dummy function until the
real implementation lands, so both workstreams stay independent.

## 7. HTTP endpoints
- `GET /health` -> 200 `{"status": "ok"}`
- `POST /routes` -> 201 `{"route_id": str}`
  Body: raw GPX 1.1, `Content-Type: application/gpx+xml`.
  422 on invalid coordinates or malformed XML.
- `GET /routes/{id}` -> 200, enriched GPX (`application/gpx+xml`). 404 if unknown.
- `GET /routes/{id}/json` -> 200, `list[EnrichedTrackpoint]`. 404 if unknown.