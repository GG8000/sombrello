# Sombrello

Shadow and UV prediction for GPX routes using Digital Terrain Models,
Canopy Height Models, solar position and CAMS UV forecasts.

## Structure
- `backend/` — installable Python package (the actual B2B product) + FastAPI
- `frontend/` — demonstrator: a single static HTML file. **This frontend is AI-generated** and only serves to demonstrate the backend API.
- `docs/` — work plan, interface contracts, API examples
- `data/` — local geodata (DTM, CHM, NetCDF). Never committed to git; see `data/README.md`.

## Setup
sombrello needs specific geospatial packages to run correctly. Run the following first before running the code:
```
python -m pip install -r requirements.txt
```

It also reads .gpkg files for buildings and vegetation (converted from raster) that contain height columns.
Vegetation height was inferred from a normalized DSM representing non-building elevated surfaces in Tuebingen.

[The vegetation and building data for Tuebingen can be downloaded here.](https://zenodo.org/records/22772283?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjNlNTFlMzg4LWYxN2EtNGFmMC04NTFmLThiMmRlMmFlNjVjZiIsImRhdGEiOnt9LCJyYW5kb20iOiJiOTJkZWNjZjA3NzgxY2UzNWJhYTRlOTBkMjIwZWY2MiJ9.9nf64_ariulivKVoonRnUd-wQtbgujt5KJSr44KUod1w1AmfH41QCcaoBEHXlZ6Z53xhQG8q_nizcVcAAvEj_g). They are to be stored in /data.

## Quickstart (backend)
```bash
python -m pip install -r requirements.txt
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m uvicorn sombrello.api.main:app --reload
```

## Quickstart (frontend)
```bash
cd frontend/
python3 -m http.server 5000
```
For local deployment (localhost), the map provider does not need an api key

## Team
- Gedeon: solar position, API, UV exposure, frontend demonstrator, testing
- Emil: GIS pipeline, raycasting shadow algorithm, GPX metadata
