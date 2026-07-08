"""
server.py — Trip Planner MCP server (FastMCP / stdio).

Exposes the deterministic engine and the output generators as MCP tools so any
MCP client (Claude Desktop, Claude Code, the app's backend) can plan trips
without spending LLM tokens on the core.

Run:  python mcp/server.py
Register (Claude Desktop / .mcp.json):
  { "mcpServers": { "trip-planner": { "command": "python",
      "args": ["/abs/path/trip-planner/mcp/server.py"] } } }

Tools:
  trip_template()                      -> blank init template
  enrich_targets(targets)              -> targets + stars/links/geo (Places if key)
  distance_from(reference, targets)    -> drive-minutes from one place to many
  generate_plan(trip)                  -> itinerary + warnings bundle
  build_workbook(bundle, out_path)     -> writes 7-sheet .xlsx, returns path
  build_brochure(bundle, out_path)     -> writes HTML brochure, returns path
"""
from __future__ import annotations
import sys, os, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import engine                      # noqa: E402
import enrich as enrich_mod        # noqa: E402
import generate_workbook           # noqa: E402
import generate_brochure           # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("pip install 'mcp[cli]'  (and optionally requests, openpyxl)")

mcp = FastMCP("trip-planner")
OUT = Path(os.environ.get("TRIP_OUT", "/tmp")); OUT.mkdir(parents=True, exist_ok=True)


@mcp.tool()
def trip_template() -> dict:
    """Return the blank trip init template to fill (flights, stays, prefs, targets)."""
    return json.loads((HERE.parent / "assets" / "trip_template.json").read_text())


@mcp.tool()
def enrich_targets(targets: list[dict]) -> list[dict]:
    """Attach Google Maps / Tripadvisor / Google Reviews / directions links to each
    target, plus stars, review_count, photos, lat/lng and opening_hours when a
    GOOGLE_MAPS_API_KEY is configured. Cached on disk; no LLM tokens."""
    return [enrich_mod.enrich(dict(t)) for t in targets]


@mcp.tool()
def distance_from(reference: dict, targets: list[dict]) -> list[dict]:
    """Drive-time in minutes from one reference place {name,lat,lng[,place_id]} to
    each target. Adds 'drive_min' to every target. Uses Distance Matrix if a key
    is set, else a haversine estimate."""
    m = enrich_mod.distance_matrix([reference], targets)
    rid = reference.get("place_id") or reference.get("name")
    out = []
    for t in targets:
        tid = t.get("place_id") or t.get("name")
        d = m.get(f"{rid}|{tid}")
        out.append({**t, "drive_min": round(d) if d is not None else None})
    return out


@mcp.tool()
def generate_plan(trip: dict) -> dict:
    """Deterministically build the plan bundle (itinerary + conflict warnings)
    from a trip (flights, stays, prefs, targets). No LLM tokens used."""
    matrix = None
    targets = trip.get("targets") or []
    bases = trip.get("stays") or []
    if targets and bases and all("lat" in x for x in targets + bases):
        matrix = enrich_mod.distance_matrix(bases, targets)
    return engine.generate_plan(trip, matrix)


@mcp.tool()
def build_workbook(bundle: dict, out_path: str | None = None) -> str:
    """Render the bundle into a 7-sheet .xlsx (Itinerary, Attractions, Foodies,
    Budget w/ live formulas, Costs Remarks, Notes and tips, Prompt). Returns path."""
    out = out_path or str(OUT / "trip.xlsx")
    return generate_workbook.build(bundle, out)


@mcp.tool()
def build_brochure(bundle: dict, out_path: str | None = None) -> str:
    """Render the bundle into a self-contained, print-to-PDF HTML brochure with
    star ratings, distances and map/Go links. Returns the file path."""
    out = out_path or str(OUT / "trip.html")
    return generate_brochure.build(bundle, out)


if __name__ == "__main__":
    mcp.run()
