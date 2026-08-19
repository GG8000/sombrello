# API Usage Examples

Start server from root directory sombrello/ with: `python -m uvicorn sombrello.api.main:app --reload`

# Add Route
This function is called, when we add a route to the dataset and this is then saved for the whole session with a unique ID
Request:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/routes' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "trackpoints": [
    {
      "lat": -90,
      "lon": -180,
      "elevation_m": -500,
      "timestamp": "2026-08-18T19:06:40.691Z"
    }
  ]
}'
```
Response:
```bash
{
  "route_id": "434c74d8-42bc-4625-95a9-8887e58b6def"
}
```

# Retrieve Route
This function will retrieve a route based on an ID with enriched shadow data, so the shadow-index, uv-index and uv_effective-index per trackpoint. 

insert route_id
Request:
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/routes/434c74d8-42bc-4625-95a9-8887e58b6def' \
  -H 'accept: application/json'
```
Response:
```bash
{
  "trackpoints": [
    {
      "timestamp": "2026-08-18T19:06:40.691000Z",
      "elevation_deg": -12.900937273579876,
      "shadow_index": 0.5,
      "uv_index": 0,
      "uv_effective": 0
    }
  ]
}
```