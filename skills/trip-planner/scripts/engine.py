"""
engine.py — deterministic itinerary engine for the trip-planner skill.

Pure Python, no AI, no required network. Turns a trip input (flights, stays,
prefs, targets) into a day-by-day plan bundle + conflict warnings.

Distance defaults to haversine; if a drive-time matrix is supplied (e.g. from
Google Distance Matrix via enrich.py) it is used instead. Everything here costs
zero LLM tokens.
"""
from __future__ import annotations
import math, datetime as dt
from typing import Any

AIRPORT_BUFFER_MIN = 180          # be at airport this long before an int'l flight
PACE_CAP = {"relaxed": 2, "balanced": 3, "packed": 4}
WINDOW_ORDER = {"morning": 0, "midday": 1, "afternoon": 2, "evening": 3, "any": 4}


# ---------- geo / distance ----------
def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    R = 6371.0
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    dphi = math.radians(la2 - la1)
    dl = math.radians(lo2 - lo1)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def drive_min(a: dict, b: dict, matrix: dict | None) -> float:
    """Drive-time minutes between two place dicts. Uses matrix if given, else
    estimates from haversine at ~70 km/h."""
    if matrix:
        key = f"{a.get('place_id') or a['name']}|{b.get('place_id') or b['name']}"
        if key in matrix:
            return matrix[key]
    km = haversine_km((a["lat"], a["lng"]), (b["lat"], b["lng"]))
    return km / 70.0 * 60.0


# ---------- S1: anchors ----------
def build_anchors(stays: list[dict]) -> list[dict]:
    """Each stay becomes a base with its inclusive night range."""
    bases = []
    for s in stays:
        ci = dt.date.fromisoformat(s["check_in"])
        co = dt.date.fromisoformat(s["check_out"])
        nights = [ci + dt.timedelta(days=i) for i in range((co - ci).days)]
        bases.append({**s, "nights": nights})
    return bases


def base_for_date(bases: list[dict], d: dt.date) -> dict | None:
    for b in bases:
        if d in b["nights"]:
            return b
    return None


# ---------- S3: cluster targets to nearest base ----------
def cluster(targets: list[dict], bases: list[dict], matrix=None,
            max_drive_min: float = 150) -> None:
    for t in targets:
        best, best_d = None, 1e9
        for b in bases:
            d = drive_min(t, b, matrix)
            if d < best_d:
                best, best_d = b, d
        t["region"] = best["name"] if best and best_d <= max_drive_min else "unassigned"
        t["_drive_from_base"] = round(best_d) if best else None


# ---------- S4: allocate targets to days ----------
def priority(t: dict) -> tuple:
    s = 0
    if t.get("state") == "embraced": s -= 100
    if "must_see" in t.get("tags", []): s -= 50
    s -= (t.get("votes", {}).get("up", 0) - t.get("votes", {}).get("down", 0)) * 5
    s -= float(t.get("stars", 0))
    return (s,)


def allocate(targets: list[dict], bases: list[dict], prefs: dict) -> dict:
    cap = PACE_CAP.get(prefs.get("pace", "balanced"), 3)
    pool = sorted([t for t in targets if t.get("state") != "dismissed"], key=priority)
    buckets: dict[dt.date, list[dict]] = {}
    for b in bases:
        for n in b["nights"]:
            buckets[n] = []
    pool_days = set()
    if prefs.get("pool_days"):
        # reserve every Nth day as a light/pool day at multi-night bases
        for b in bases:
            if len(b["nights"]) >= 4:
                pool_days.add(b["nights"][len(b["nights"]) // 2])
    for t in pool:
        cand = [d for d in buckets
                if base_for_date(bases, d) and base_for_date(bases, d)["name"] == t.get("region")
                and len(buckets[d]) < cap and d not in pool_days
                and _open_on(t, d)]
        if cand:
            cand.sort(key=lambda d: len(buckets[d]))   # spread load
            buckets[cand[0]].append(t)
        else:
            t["state"] = t.get("state") or "overflow"
    return buckets


def _open_on(t: dict, d: dt.date) -> bool:
    oh = t.get("opening_hours")
    if not oh:
        return True
    wd = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][d.weekday()]
    return str(oh.get(wd, "")).lower() != "closed"


# ---------- S5: order a day's stops (nearest-neighbour + 2-opt) ----------
def _route_len(order: list[dict], start: dict, matrix) -> float:
    tot, cur = 0.0, start
    for n in order:
        tot += drive_min(cur, n, matrix); cur = n
    return tot


def route_day(items: list[dict], base: dict, matrix=None) -> list[dict]:
    if not items:
        return []
    unvisited = items[:]
    order, cur = [], base
    while unvisited:
        nxt = min(unvisited, key=lambda n: drive_min(cur, n, matrix))
        order.append(nxt); unvisited.remove(nxt); cur = nxt
    improved = True
    while improved:
        improved = False
        for i in range(len(order) - 1):
            for j in range(i + 1, len(order)):
                new = order[:i] + order[i:j + 1][::-1] + order[j + 1:]
                if _route_len(new, base, matrix) + 1e-6 < _route_len(order, base, matrix):
                    order, improved = new, True
    return order


# ---------- S6: schedule clock times ----------
def schedule(order: list[dict], base: dict, day: dt.date, matrix=None,
             start_hour: int = 9) -> list[dict]:
    t = dt.datetime.combine(day, dt.time(start_hour, 0))
    cur, out = base, []
    for stop in order:
        t += dt.timedelta(minutes=drive_min(cur, stop, matrix))
        dur = stop.get("typical_duration_min", 90)
        out.append({**stop, "start": t.strftime("%H:%M"),
                    "end": (t + dt.timedelta(minutes=dur)).strftime("%H:%M")})
        t += dt.timedelta(minutes=dur + 15)   # +buffer
        cur = stop
    return out


# ---------- S7: conflict checks (declarative rules) ----------
def check_conflicts(trip: dict, bases: list[dict]) -> list[dict]:
    w: list[dict] = []
    car = trip.get("car") or {}
    flights = trip.get("flights", [])
    # the homebound flight: dir == "in", else the latest-departing flight
    home_flight = next((f for f in flights if f.get("dir") == "in"), None)
    if not home_flight and flights:
        home_flight = max(flights, key=lambda f: f.get("depart", ""))
    if car.get("return") and home_flight and home_flight.get("depart"):
        ret = dt.datetime.fromisoformat(car["return"])
        dep = dt.datetime.fromisoformat(home_flight["depart"])
        if ret > dep - dt.timedelta(minutes=AIRPORT_BUFFER_MIN):
            w.append({"code": "CAR_AFTER_FLIGHT",
                      "msg": f"Car return {ret:%Y-%m-%d %H:%M} is too close to homebound "
                             f"flight {dep:%Y-%m-%d %H:%M} (need {AIRPORT_BUFFER_MIN//60}h buffer)."})
    ds = dt.date.fromisoformat(trip["date_start"])
    de = dt.date.fromisoformat(trip["date_end"])
    night = ds
    while night < de:
        if not base_for_date(bases, night):
            w.append({"code": "NO_LODGING", "msg": f"No accommodation for night of {night}."})
        night += dt.timedelta(days=1)
    for t in trip.get("targets", []):
        if "needs_booking" in t.get("tags", []) and not t.get("booked"):
            w.append({"code": "BOOK_AHEAD", "msg": f"{t['name']} needs advance booking."})
    return w


# ---------- top-level ----------
def generate_plan(trip: dict, matrix: dict | None = None) -> dict:
    """trip: see assets/trip_template.json. Returns a plan bundle (itinerary +
    warnings) ready for generate_workbook / generate_brochure."""
    prefs = trip.get("prefs", {})
    bases = build_anchors(trip["stays"])
    targets = trip.get("targets", [])
    if targets:
        cluster(targets, bases, matrix, prefs.get("max_radius_min", 150))
        buckets = allocate(targets, bases, prefs)
    else:
        buckets = {n: [] for b in bases for n in b["nights"]}

    itinerary = []
    day_num = 0
    d = dt.date.fromisoformat(trip["date_start"])
    end = dt.date.fromisoformat(trip["date_end"])
    while d <= end:
        day_num += 1
        base = base_for_date(bases, d)
        stops = route_day(buckets.get(d, []), base or {"lat": 0, "lng": 0, "name": "-"}, matrix)
        timed = schedule(stops, base or {"lat": 0, "lng": 0}, d, matrix) if base else []
        acts = "; ".join(f"{s['start']} {s['name']}" for s in timed) or "Open / travel day"
        itinerary.append({
            "date": d.isoformat(), "day": day_num,
            "location": (base or {}).get("name", "—"),
            "activities": acts,
            "accommodation": (base or {}).get("name", "—"),
            "notes": "",
        })
        d += dt.timedelta(days=1)

    return {
        "trip": {k: trip.get(k) for k in ("name", "currency", "travelers",
                                          "date_start", "date_end")},
        "itinerary": itinerary,
        "warnings": check_conflicts(trip, bases),
        "targets": targets,
    }


if __name__ == "__main__":
    import json, sys
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.load(sys.stdin)
    print(json.dumps(generate_plan(data), indent=2, default=str))
