# Trip Planner — Engine Reference

Deterministic-first pipeline. The model runs at most twice per trip (parse docs,
write blurbs); everything below is algorithm + cached API = 0 tokens.

## Pipeline
| Stage | Fn (scripts/engine.py) | Method |
|---|---|---|
| S0 ingest docs → events | (AI, cached, optional) | AI |
| S1 anchors from stays | `build_anchors` | ALGO |
| S2 enrich targets | `enrich.py::enrich` | API (Places), cached |
| S3 cluster → nearest base | `cluster` | ALGO |
| S4 allocate to days | `allocate` | ALGO |
| S5 order a day | `route_day` (NN + 2-opt) | ALGO |
| S6 clock times | `schedule` | ALGO |
| S7 conflict checks | `check_conflicts` | ALGO (rule table) |
| S8 blurbs / narrative | (AI, batched, cached) | AI |

## Allocation rules (S4)
pace → cap (relaxed 2 / balanced 3 / packed 4) · opening-day filter · pool/light
day reserved at long bases · spread load across days · priority = embraced >
must_see > votes > stars. Unplaceable targets get state `overflow`.

## Conflict rules (S7) — extend by adding rows
CAR_AFTER_FLIGHT (return within airport buffer of departure) · NO_LODGING (night
with no stay) · BOOK_AHEAD (target tagged needs_booking, not booked). Add ZTL /
dress-code / riposo / heat as new checks.

## Distances
`enrich.py::distance_matrix(origins, dests)` → `{ 'oid|did': minutes }`. Online via
Google Distance Matrix (batched, cached per origin-dest), offline via haversine
at ~70 km/h. The "distance from a specific place" feature = call with reference as
the single origin; rewrite each card's directions link to that origin.

## Caching
place_id → facts (permanent) · ratings/photos (TTL) · matrix (per pair) ·
AI ingest (sha of doc) · AI narrative (sha of plan). See enrich.py `_cache`.

## Target bank states & collaboration
states: suggested | embraced | dismissed | maybe. Votes feed `priority()`.
Embrace/remove → re-run S3–S6 for the affected base only (incremental reflow).

## Outputs
`generate_workbook.py` → 7-sheet xlsx (live budget formulas, source links).
`generate_brochure.py` → self-contained HTML (stars, distance, Go links).
Both consume the same bundle (assets/bundle_schema.json).
