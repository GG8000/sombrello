# Interfaces & Data Contracts

Define these BEFORE implementing. Both team members must agree on any change.

## 1. Trackpoint
`{lat: float, lon: float, elevation_m: float, timestamp: ISO-8601 UTC}`

## 2. Solar output (Gedeon -> Emil)
`{azimuth_deg: float, elevation_deg: float}` per trackpoint/timestamp

## 3. Shadow output (Emil -> API)
`shadow_index: float` in [0.0, 1.0] per trackpoint

## 4. GPX extensions
Namespaced extensions carrying `shadow_index` and `uv_effective`.

## 5. Stub strategy
The API integrates the shadow algorithm as a dummy function until the
real implementation lands, so both workstreams stay independent.
