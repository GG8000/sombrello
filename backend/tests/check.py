import time
from sombrello.gpx import gpx_to_trackpoint_list, enrich
from sombrello.config import get_settings

with open("backend/tests/testgpx.gpx", "r", encoding="utf-8") as f:
    gpx_string = f.read()

t0 = time.perf_counter()
trackpoints, metadata = gpx_to_trackpoint_list(gpx_string=gpx_string)
t1 = time.perf_counter()
print(f"Parsing: {t1 - t0:.2f}s, {len(trackpoints)} points")

settings = get_settings()

t2 = time.perf_counter()
enriched = [enrich(tp, settings) for tp in trackpoints]
t3 = time.perf_counter()
print(f"Enrichment: {t3 - t2:.2f}s ({(t3-t2)/len(trackpoints)*1000:.1f}ms/point)")