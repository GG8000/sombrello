# Work Plan — Gedeon (TDD)

Solar position · UV exposure · API · frontend demonstrator.

Everything here is ordered so that **each step is testable with zero external
data**. No DTM, no CHM, no CAMS download, no API key is needed to finish Phases
1–6. The heavy geodata stays on Emil's side.

---

## Scope

| I own | I consume from Emil |
|---|---|
| `sombrello/models` — shared `Trackpoint` | — |
| `sombrello/solar` — sun azimuth/elevation | — |
| `sombrello/uv` — UV index & effective UV | `shadow_index` (stubbed until ready) |
| `sombrello/api` — FastAPI endpoints | `shadow_index` (stubbed until ready) |
| `frontend/index.html` — demonstrator | — |

Contracts are fixed in [INTERFACES.md](INTERFACES.md) — do not change a signature
without telling Emil:

- Trackpoint: `{lat, lon, elevation, timestamp}`
- Solar out: `{azimuth_deg, elevation_deg}`
- Shadow out: `shadow_index` float in `[0.0, 1.0]`

---

## How to work: TDD in five lines

1. **Red** — write one test for one behaviour. Run `pytest`. It must fail.
2. **Green** — write the *dumbest* code that makes it pass. Hardcoding is allowed here.
3. **Refactor** — clean up. Tests still green.
4. Commit on every green. Small commits, message = the behaviour you added.
5. Never write production code without a failing test asking for it.

If a test passes the moment you write it, it is testing nothing. Break the
implementation on purpose once to check the test actually watches it.

The four pytest tools used in this plan:

```python
assert value == pytest.approx(12.5, abs=0.1)      # floats — never use ==
with pytest.raises(ValidationError): ...           # expected failures
@pytest.mark.parametrize("lat", [-91, 91])         # same test, many inputs
def test_x(client): ...                            # fixture injected by name
```

---

## Phase 0 — Setup (~20 min)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Add to `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

This repo is **not a git repository yet**. Since the workflow above says "commit
on every green", initialise it first (from the project root, not `backend/`):

```bash
git init && git add -A && git commit -m "Initial skeleton"
```

Baseline check — `pytest` from `backend/` should report *no tests ran*. That is
your green starting point.

Then write your first red test, just to see the machinery work:

```python
# tests/test_models.py
def test_pytest_is_wired_up():
    assert False, "delete me once you have seen red"
```

Run it, see it fail, delete it. Now start Phase 1.

---

## Phase 1 — `Trackpoint` model

**File:** `sombrello/models/__init__.py` **Test:** `tests/test_models.py` (new)

Pydantic ships with FastAPI, so validation is nearly free and the same model is
reused by the API in Phase 5.

### Red

```python
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from sombrello.models import Trackpoint


def test_trackpoint_holds_its_four_fields():
    tp = Trackpoint(lat=47.8, lon=13.04, elevation=424.0,
                    timestamp=datetime(2024, 6, 21, 12, tzinfo=timezone.utc))
    assert tp.lat == 47.8
    assert tp.elevation == 424.0


@pytest.mark.parametrize("lat", [-91.0, 91.0])
def test_latitude_outside_the_globe_is_rejected(lat):
    with pytest.raises(ValidationError):
        Trackpoint(lat=lat, lon=0.0, elevation=0.0,
                   timestamp=datetime(2024, 6, 21, tzinfo=timezone.utc))
```

### Green

```python
from pydantic import BaseModel, Field

class Trackpoint(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    elevation: float
    timestamp: datetime
```

### Done when
Both tests pass, and the same `parametrize` test exists for `lon` (`±181`).

---

## Phase 2 — Solar position

**File:** `sombrello/solar/__init__.py` **Test:** `tests/test_solar.py`

`pvlib` is already a dependency and does the astronomy. Your job is a thin
wrapper that returns the contract from INTERFACES.md §2 — so test *your*
contract, not pvlib's internals.

### Red

Assert on **physics you know is true**, not on numbers you copied from somewhere:

```python
from datetime import datetime, timezone
from sombrello.solar import sun_position

SALZBURG = (47.80, 13.04)


def test_sun_is_below_the_horizon_at_local_midnight():
    pos = sun_position(*SALZBURG, datetime(2024, 6, 21, 0, tzinfo=timezone.utc))
    assert pos.elevation_deg < 0


def test_sun_is_almost_overhead_at_the_equator_on_the_equinox():
    pos = sun_position(0.0, 0.0, datetime(2024, 3, 20, 12, tzinfo=timezone.utc))
    assert pos.elevation_deg > 85


def test_azimuth_is_a_compass_bearing():
    pos = sun_position(*SALZBURG, datetime(2024, 6, 21, 12, tzinfo=timezone.utc))
    assert 0 <= pos.azimuth_deg <= 360
```

### Green

```python
from dataclasses import dataclass
from datetime import datetime
import pvlib
import pandas as pd

@dataclass(frozen=True)
class SolarPosition:
    azimuth_deg: float
    elevation_deg: float


def sun_position(lat: float, lon: float, when: datetime) -> SolarPosition:
    times = pd.DatetimeIndex([when])
    result = pvlib.solarposition.get_solarposition(times, lat, lon)
    return SolarPosition(
        azimuth_deg=float(result["azimuth"].iloc[0]),
        elevation_deg=float(result["apparent_elevation"].iloc[0]),
    )
```

### Refactor step worth doing
`print(pos)` in a scratch run, read the real Salzburg values, then **tighten** the
loose bound into a precise one, e.g. `== pytest.approx(59.4, abs=0.5)`. Loose
first, precise second — that is the honest way to arrive at a magic number.

### Done when
Three tests green, and a batch helper exists if you want it:
`sun_positions(trackpoints) -> list[SolarPosition]` (a plain list comprehension is
fine; optimise only if it ever gets slow).

---

## Phase 3 — UV exposure

**File:** `sombrello/uv/__init__.py` **Test:** `tests/test_uv.py` (new)

Pure arithmetic, no I/O — the easiest thing in the whole project to test, and the
place where your work meets Emil's.

Clear-sky model (good enough for the demonstrator):

```
UVI = 12.5 · sin(elevation)^2.42 · (1 + 0.06 · altitude_km),  elevation > 0
UVI = 0.0                                                      elevation ≤ 0
uv_effective = UVI · (1 − shadow_index)
```

### Red

```python
import pytest
from sombrello.uv import uv_index, uv_effective


def test_no_uv_when_the_sun_is_down():
    assert uv_index(elevation_deg=-5.0) == 0.0


def test_overhead_sun_at_sea_level_is_the_maximum():
    assert uv_index(elevation_deg=90.0) == pytest.approx(12.5, abs=0.1)


def test_uv_rises_with_the_sun():
    assert uv_index(20.0) < uv_index(45.0) < uv_index(70.0)


def test_altitude_increases_uv():
    assert uv_index(45.0, altitude_m=2000) > uv_index(45.0, altitude_m=0)


@pytest.mark.parametrize("shadow,expected", [(0.0, 10.0), (1.0, 0.0), (0.5, 5.0)])
def test_shade_reduces_the_dose(shadow, expected):
    assert uv_effective(10.0, shadow) == pytest.approx(expected)
```

### Green

```python
import math

def uv_index(elevation_deg: float, altitude_m: float = 0.0) -> float:
    if elevation_deg <= 0:
        return 0.0
    clear_sky = 12.5 * math.sin(math.radians(elevation_deg)) ** 2.42
    return clear_sky * (1 + 0.06 * altitude_m / 1000)


def uv_effective(uvi: float, shadow_index: float) -> float:
    return uvi * (1 - shadow_index)
```

### Done when
All five tests green. Add `pytest.raises(ValueError)` for a `shadow_index`
outside `[0, 1]` if you want the extra practice — write the test first.

---

## Phase 4 — Shadow stub + the contract test

**File:** `sombrello/shadow/__init__.py` **Test:** `tests/test_shadow.py`

INTERFACES.md §5 says the API uses a dummy shadow function until Emil's raycaster
lands. **This is the most valuable TDD lesson in the project**: the test below
describes the *contract*, so it must pass for your stub today and for Emil's real
implementation later, unchanged. Write it now, hand it to Emil, and neither of you
can break the other.

### Red

```python
from datetime import datetime, timezone
import pytest
from sombrello.models import Trackpoint
from sombrello.solar import sun_position
from sombrello.shadow import shadow_index


@pytest.fixture
def trackpoint():
    return Trackpoint(lat=47.8, lon=13.04, elevation=424.0,
                      timestamp=datetime(2024, 6, 21, 12, tzinfo=timezone.utc))


@pytest.fixture
def sun(trackpoint):
    return sun_position(trackpoint.lat, trackpoint.lon, trackpoint.timestamp)


def test_shadow_index_is_a_fraction(trackpoint, sun):
    value = shadow_index(trackpoint, sun)
    assert isinstance(value, float)
    assert 0.0 <= value <= 1.0    # must stay true for Emil's real version too


def test_shadow_index_is_deterministic(trackpoint, sun):
    assert shadow_index(trackpoint, sun) == shadow_index(trackpoint, sun)
```

### Green

```python
def shadow_index(trackpoint, solar_position) -> float:
    """Stub. Replaced by Emil's raycasting implementation — same signature."""
    return 0.0
```

### Done when
Both tests green, and the docstring makes the stub status obvious to anyone
reading it. Tell Emil these two tests are the acceptance criteria for his module.

---

## Phase 5 — API

**Files:** `sombrello/api/main.py`, `sombrello/api/routes.py` **Test:** `tests/test_api.py`

Storage is a module-level `dict` keyed by a `uuid4` string. No database, no ORM,
no migrations — this is a demonstrator.

Endpoints:

| Method | Path | Body / Params | Returns |
|---|---|---|---|
| GET | `/health` | — | `{"status": "ok"}` |
| POST | `/routes` | `{"trackpoints": [Trackpoint, ...]}` | `{"route_id": "<uuid>"}` |
| GET | `/routes/{route_id}` | — | trackpoints enriched with solar + UV |
| GET | `/routes/{unknown}` | — | 404 |

### Red — start with the smallest possible endpoint

```python
import pytest
from fastapi.testclient import TestClient
from sombrello.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint_reports_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Green: three lines with `@app.get("/health")`. Commit. Now the real ones:

```python
POINT = {"lat": 47.8, "lon": 13.04, "elevation": 424.0,
         "timestamp": "2024-06-21T12:00:00Z"}


def test_posting_a_route_returns_an_id(client):
    response = client.post("/routes", json={"trackpoints": [POINT]})
    assert response.status_code == 201
    assert response.json()["route_id"]


def test_stored_route_comes_back_enriched(client):
    route_id = client.post("/routes", json={"trackpoints": [POINT]}).json()["route_id"]

    response = client.get(f"/routes/{route_id}")

    assert response.status_code == 200
    point = response.json()["trackpoints"][0]
    assert 0 <= point["azimuth_deg"] <= 360
    assert point["uv_index"] >= 0
    assert 0.0 <= point["shadow_index"] <= 1.0
    assert point["uv_effective"] == pytest.approx(
        point["uv_index"] * (1 - point["shadow_index"]))


def test_unknown_route_is_404(client):
    assert client.get("/routes/does-not-exist").status_code == 404


def test_invalid_latitude_is_rejected(client):
    bad = {**POINT, "lat": 999.0}
    assert client.post("/routes", json={"trackpoints": [bad]}).status_code == 422
```

The last one passes for free — pydantic from Phase 1 already guards it. That is
the payoff for building the model first.

### Green — sketch

```python
# routes.py
from uuid import uuid4
from fastapi import APIRouter, HTTPException

router = APIRouter()
_routes: dict[str, list[Trackpoint]] = {}


class RouteIn(BaseModel):          # request body wrapper
    trackpoints: list[Trackpoint]


@router.post("/routes", status_code=201)
def create_route(payload: RouteIn) -> dict:
    route_id = str(uuid4())
    _routes[route_id] = payload.trackpoints
    return {"route_id": route_id}


@router.get("/routes/{route_id}")
def get_route(route_id: str) -> dict:
    if route_id not in _routes:
        raise HTTPException(status_code=404, detail="route not found")
    return {"trackpoints": [_enrich(tp) for tp in _routes[route_id]]}
```

`_enrich` is where Phases 2–4 come together: `sun_position` → `shadow_index` →
`uv_index` → `uv_effective`. `main.py` just creates the `app` and includes the
router.

### Done when
Five tests green, `uvicorn sombrello.api.main:app --reload` serves
<http://127.0.0.1:8000/docs>, and you have pasted two working `curl` calls into
[api_examples.md](api_examples.md) — that file is currently a placeholder and is
yours to fill.

---

## Phase 6 — Frontend demonstrator

**File:** `frontend/index.html` — deliberately **not** unit-tested. README.md
already declares it AI-generated and demo-only; do not spend time on a JS test
setup.

Minimum that demonstrates the backend:

1. A textarea or a hardcoded demo route (3–5 trackpoints).
2. `POST /routes` → `GET /routes/{id}` via `fetch`.
3. A table: time · elevation angle · shadow index · UV effective.
4. A time slider that re-requests with a different timestamp.
5. Enable CORS in `main.py` (`CORSMiddleware`, `allow_origins=["*"]`) or the
   browser will block you — expect to hit this and recognise it in the console.

Manual checklist: page loads from `file://`, table fills, slider changes values,
no console errors.

---

## Definition of Done

| Phase | Deliverable | Check |
|---|---|---|
| 0 | pytest runs, git initialised | `pytest` → no tests, exit 0 |
| 1 | `Trackpoint` + validation | `tests/test_models.py` green |
| 2 | `sun_position` | `tests/test_solar.py` green |
| 3 | `uv_index`, `uv_effective` | `tests/test_uv.py` green |
| 4 | Shadow stub + contract test | `tests/test_shadow.py` green, Emil informed |
| 5 | 4 endpoints | `tests/test_api.py` green, `/docs` reachable |
| 6 | Demonstrator | Manual checklist above |

Whole suite: `cd backend && pytest -v` — everything green, no skips.

---

## Optional extensions (only after everything above is green)

- **Real UV from CAMS.** Keep `uv_index(elevation_deg, altitude_m)` as the
  signature and add `uv_index_from_cams(lat, lon, when)` behind the same return
  type. Needs an ADS account, `cdsapi` key, and a small committed NetCDF slice as
  a test fixture — that fixture is the reason this is *not* Phase 3.
- **GPX in/out.** Once Emil's `sombrello/gpx` module exists: accept a `.gpx`
  upload on `POST /routes` and return one with the namespaced
  `shadow_index` / `uv_effective` extensions from INTERFACES.md §4.
- **Caching.** `functools.lru_cache` on `sun_position` if a long route ever feels
  slow. Measure before you add it.
