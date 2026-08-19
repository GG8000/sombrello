# Sombrello

Shadow and UV prediction for GPX routes using Digital Terrain Models,
Canopy Height Models, solar position and CAMS UV forecasts.

## Structure
- `backend/` — installable Python package (the actual B2B product) + FastAPI
- `frontend/` — demonstrator: a single static HTML file. **This frontend is AI-generated** and only serves to demonstrate the backend API.
- `docs/` — work plan, interface contracts, API examples
- `data/` — local geodata (DTM, CHM, NetCDF). Never committed to git; see `data/README.md`.

## Quickstart (backend)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m uvicorn sombrello.api.main:app --reload
```

## Team
- Gedeon: solar position, API, UV exposure, frontend demonstrator
- Emil: GIS pipeline, raycasting shadow algorithm, GPX metadata
