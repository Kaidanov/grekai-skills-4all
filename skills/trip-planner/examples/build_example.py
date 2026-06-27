"""
build_example.py — assemble the worked Tuscany example bundle and render both
outputs (Excel workbook + HTML brochure) from it.

Demonstrates the full pipeline:
  trip JSON --(engine, 0 tokens)--> itinerary + warnings
            --(add target bank + budget skeleton)--> complete bundle
            --(generators)--> tuscany-workbook.xlsx + tuscany-brochure.html

Run from the skill root:  python examples/build_example.py
"""
from __future__ import annotations
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))

import engine                # noqa: E402
import enrich as enrich_mod  # noqa: E402
import generate_workbook     # noqa: E402
import generate_brochure     # noqa: E402

trip = json.loads((HERE / "tuscany-trip.json").read_text())

# S2 — enrich every target with Maps / Tripadvisor / Google Reviews / directions
# links (offline; no key needed). Live mode would also add stars + geo.
for t in trip["targets"]:
    enrich_mod.enrich(t)

# S1-S7 — deterministic plan (itinerary + conflict warnings), 0 LLM tokens.
# Real drive-times come from a distance matrix; offline it falls back to haversine.
matrix = enrich_mod.distance_matrix(trip["stays"], trip["targets"])
plan = engine.generate_plan(trip, matrix)

by_cat = lambda c: [t for t in plan["targets"] if t.get("category") == c]


def attraction(t):
    return {
        "name": t["name"], "type": t.get("category", "attraction").title(),
        "location": t.get("location", ""),
        "highlights": t.get("_highlights", ""),
        "accessibility": t.get("_accessibility", "Stroller-friendly main routes"),
        "cost": t.get("_cost", "€"),
        "popularity": f"{t.get('stars','')}/5",
        "reviews": f"{t.get('review_count','')} reviews" if t.get("review_count") else "",
        "suitable_for": "Families" if trip["prefs"].get("with_kids") else "All",
        "special": ("⭐ embraced" if t.get("state") == "embraced" else ""),
        "notes": t.get("_notes", ""),
        "importer_flag": t.get("state") == "embraced",
        "links": t.get("links", {}),
        "_drive_from_base": t.get("_drive_from_base"),
    }


def foodie(t):
    return {
        "name": t["name"], "price": t.get("_price", "€€"),
        "location": t.get("location", ""),
        "popularity": f"{t.get('stars','')}/5",
        "dishes": t.get("_dishes", ""), "specialty": t.get("_specialty", ""),
        "ambiance": t.get("_ambiance", ""), "notes": t.get("_notes", ""),
        "links": t.get("links", {}), "_drive_from_base": t.get("_drive_from_base"),
    }


# short human blurbs (the ONE place the model would normally write a few lines)
BLURBS = {
    "Piazza del Campo, Siena": ("Shell-shaped medieval square, the heart of Siena.",
                                "Go early — shade is scarce by midday in July."),
    "Duomo di Siena": ("Striped marble cathedral with a mosaic floor.",
                       "Timed entry — book the slot online the night before."),
    "San Gimignano Towers": ("Skyline of medieval stone towers; world-famous gelato below.",
                             "Gelateria Dondoli on the main square is worth the queue."),
    "Greve in Chianti Market": ("Saturday-morning produce, cheese and leather stalls.",
                                "Saturdays only — closed Sundays."),
    "Castello di Verrazzano (winery)": ("Hilltop Chianti Classico estate with cellar tours.",
                                        "Booked: 11:00 tour + tasting, kids get grape juice."),
    "Val d'Orcia Panorama (Pienza)": ("The postcard rolling hills and cypress lines.",
                                      "Golden hour from the Pienza town walls is unbeatable."),
    "Bagno Vignoni Thermal Village": ("A piazza that is a steaming thermal pool.",
                                      "Free to look; nearby pools for a warm soak."),
    "Montepulciano Old Town": ("Renaissance hill town famous for Vino Nobile.",
                              "Steep lanes — comfortable shoes; great sunset wine bars."),
    "Pienza Pecorino Tasting": ("Aged sheep's-milk pecorino, the town's signature.",
                               "Pair with local honey and a glass of Vino Nobile."),
}
for t in plan["targets"]:
    hi, note = BLURBS.get(t["name"], ("", ""))
    t["_highlights"] = hi
    t["_notes"] = note
    if t["category"] == "foodie":
        t["_dishes"] = "Aged pecorino, honey, cured meats"
        t["_specialty"] = "DOP Pecorino di Pienza"
        t["_ambiance"] = "Family-run tasting room"

bundle = {
    "trip": plan["trip"],
    "itinerary": plan["itinerary"],
    "attractions": [attraction(t) for t in plan["targets"]
                    if t.get("category") in ("attraction", "shopping", "winery", "nature")],
    "foodies": [foodie(t) for t in by_cat("foodie")],
    "budget": {
        "contingency_pct": 10,
        "sections": [
            {"title": "1. Flights", "items": [
                {"item": "TLV→FLR→TLV (family of 4)", "qty": 4, "unit": 320,
                 "note": "Round-trip economy estimate"}]},
            {"title": "2. Accommodation", "items": [
                {"item": "Agriturismo Chianti (Greve)", "qty": 4, "unit": 180, "note": "4 nights"},
                {"item": "Val d'Orcia Farmhouse (Pienza)", "qty": 3, "unit": 195, "note": "3 nights"}]},
            {"title": "3. Car & fuel", "items": [
                {"item": "Compact SUV rental", "qty": 7, "unit": 55, "note": "7 days"},
                {"item": "Fuel + tolls", "qty": 1, "unit": 140, "note": "Chianti ↔ Val d'Orcia loop"},
                {"item": "ZTL/parking", "qty": 7, "unit": 12, "note": "Town parking + ZTL care"}]},
            {"title": "4. Food", "items": [
                {"item": "Breakfasts (in stays)", "qty": 8, "unit": 0, "note": "Included"},
                {"item": "Lunches", "qty": 8, "unit": 60, "note": "Family, casual"},
                {"item": "Dinners", "qty": 8, "unit": 95, "note": "Trattoria avg"}]},
            {"title": "5. Activities", "items": [
                {"item": "Verrazzano winery tour + tasting", "qty": 2, "unit": 35, "note": "Adults; kids free"},
                {"item": "Siena Duomo timed entry", "qty": 4, "unit": 16, "note": "Book ahead"},
                {"item": "Pecorino tasting", "qty": 4, "unit": 12, "note": "Pienza"}]},
        ],
    },
    "costs_remarks": [
        ["How to read this budget", "h"],
        "All figures are planning estimates in EUR for a family of 4 (2 adults, 2 children). "
        "Totals are live formulas — change any Quantity or Unit Cost and the sheet recomputes.",
        ["Where the money goes", "h"],
        "Accommodation and food dominate a Tuscany week; the car is unavoidable for the hill "
        "towns but a single compact SUV covers the whole loop. A 10% contingency is added at the bottom.",
        ["Easy savings", "h"],
        "Agriturismo breakfasts are included, lunches at enotecas are cheaper than dinners, and most "
        "panoramas (Val d'Orcia, Bagno Vignoni piazza) are free.",
    ],
    "notes": [
        ["Heat & kids", "h"],
        "July midday tops 34–37 °C. Front-load sightseeing to the morning, reserve the afternoon for "
        "the agriturismo pool, and carry water — the engine already reserved a mid-stay pool day.",
        ["Driving in Tuscany", "h"],
        "Hill-town centres are ZTL (limited-traffic) zones — park outside the walls and walk in. "
        "Return the car with a full tank near the airport.",
        ["Book ahead", "h"],
        "Siena Duomo uses timed entry and the Verrazzano winery requires a reservation — both flagged "
        "in the warnings below.",
    ],
    "prompt": [
        "Plan a balanced 8-day Tuscany family trip (2 adults + 2 kids, ages 10 & 13), 22–29 Jul 2026, "
        "flying TLV→Florence, two bases (Chianti then Val d'Orcia), interests history/art/food/wine/"
        "scenery/shopping, heat-aware with pool days, max ~120 min drive/day. Build the itinerary, a "
        "scored target bank, a budget workbook and a printable brochure.",
    ],
    "warnings": plan["warnings"],
}

(HERE / "tuscany-bundle.json").write_text(json.dumps(bundle, indent=2, default=str))
generate_workbook.build(bundle, str(HERE / "tuscany-workbook.xlsx"))
generate_brochure.build(bundle, str(HERE / "tuscany-brochure.html"))
print("wrote tuscany-bundle.json, tuscany-workbook.xlsx, tuscany-brochure.html")
print(f"warnings: {len(bundle['warnings'])} -> " +
      "; ".join(w["code"] for w in bundle["warnings"]))
