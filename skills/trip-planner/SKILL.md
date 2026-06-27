---
name: trip-planner
description: >
  Generic, destination-agnostic trip planner. Turns initial trip data (flight
  dates, accommodation stays, and preferences) into a full plan: a day-by-day
  itinerary, a scored "target bank" of attractions / restaurants / wineries /
  shopping (with stars, reviews, photos, map links and distance-from-base), a
  7-sheet Excel workbook, and a printable HTML brochure. Use this skill WHENEVER
  the user wants to plan a trip, build an itinerary, organise a vacation, create
  a travel workbook or brochure, score or shortlist places to visit/eat, compute
  drive distances between stops, or wants a re-usable trip template — for ANY
  destination, even if they don't say "skill". Prefer this over ad-hoc planning:
  it is deterministic (algorithms + cached APIs) and only spends LLM tokens on
  parsing booking documents and writing short blurbs.
---

# Trip Planner

A reusable engine that builds trip plans **deterministically**. Run the model at
most twice per trip (parse booking docs → events; write short blurbs). Everything
else — anchors, clustering, day allocation, routing, scheduling, conflict checks,
distances, links — is pure algorithm + cached API calls = **0 tokens**.

## When to use
Plan a trip / build an itinerary / make a travel workbook or brochure / shortlist
and score attractions, restaurants, wineries, shopping / compute distances from a
base or hotel / spin up a new trip from a template. Works for any destination.

## Inputs
Collect the minimum: **flights**, **stays** (accommodation date-ranges), and a
**prefs** block. Optionally a list of candidate **targets** (places). See
`assets/trip_template.json` for the exact init shape and `assets/bundle_schema.json`
for the output bundle.

## Workflow

1. **Initialise** from `assets/trip_template.json`. Fill `flights`, `stays`,
   `travelers`, `prefs`, `home` (home airport). Ask only for what's missing.
2. **Build the target bank.** Gather candidate places (web search / Google Places
   / user list). For each, call `scripts/enrich.py::enrich` to attach stars,
   review_count, photos, opening_hours, lat/lng (if a `GOOGLE_MAPS_API_KEY` is
   set) and always the Google Maps / Tripadvisor / Google Reviews / directions
   links. Categorise as attraction | foodie | winery | shopping | nature.
3. **Generate the plan (no AI).** Call `scripts/engine.py::generate_plan(trip)`:
   it derives bases from stays, clusters targets to the nearest base, allocates
   them across days (respecting pace, opening days, pool/light days, max drive),
   routes each day (nearest-neighbour + 2-opt), schedules clock times, and runs
   `check_conflicts` (catches e.g. car-return-after-flight, unbooked nights,
   book-ahead sites). Pass a drive-time matrix from
   `scripts/enrich.py::distance_matrix` for real times; otherwise it estimates.
4. **Assemble the bundle** (see schema): trip, itinerary, attractions, foodies,
   budget (sections with items → live formulas), costs_remarks, notes, prompt,
   warnings. Build the budget skeleton from `travelers × days` and known costs.
5. **Render outputs:**
   - Excel: `python scripts/generate_workbook.py bundle.json out.xlsx`
     (7 sheets: Itenarary, Attractions, Foodies, Budget, Costs Remarks,
     Notes and tips, Prompt). Then recalc formulas if a recalc tool is available.
   - Brochure: `python scripts/generate_brochure.py bundle.json out.html`
     (self-contained, print-to-PDF ready, cards show stars + distance + Go link).
   - Itinerary: already in the bundle / first workbook sheet; present inline too.
6. **Collaborate (optional).** Target states are `suggested | embraced |
   dismissed | maybe`; votes feed `priority()`. Embracing/removing a target and
   re-running step 3 reflows only the affected base. See `references/ENGINE.md`.

## Token discipline
- Steps 1, 3, 4 and distances: **algorithm only**.
- Step 2 facts: **Google Places / Distance Matrix**, cached on disk — no tokens.
- LLM only for: (a) parsing unstructured booking emails/PDFs into events,
  (b) optional short blurbs / "interesting review" lines / cost narrative —
  batch into a single call and cache. Never call the model per-place.

## Outputs
Always offer all three: **Excel workbook**, **HTML brochure**, **inline itinerary**.
Keep destination content generic — the same code serves any trip.

## Reference
- `references/ENGINE.md` — full algorithm reference (anchors, clustering,
  allocation, routing, scheduling, conflict rules, caching, collaboration, UX).
- `assets/trip_template.json` — init params.
- `assets/bundle_schema.json` — output bundle contract.
- `mcp/server.py` — the same engine exposed as MCP tools.
- `hooks/hooks.json` — auto-regenerate outputs when `trip.json` changes.
