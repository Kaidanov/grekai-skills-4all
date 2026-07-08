"""
enrich.py — attach extensive data to targets and compute distances.

Two modes:
  * OFFLINE (default): always builds Google Maps / Tripadvisor / Google Reviews
    search links + a "Go" directions link. Zero cost, no key.
  * ONLINE (if GOOGLE_MAPS_API_KEY set): adds stars, review_count, photos,
    opening_hours, lat/lng via Places, and real drive-time via Distance Matrix.
    Results are cached on disk so each place/route is fetched at most once.

No LLM tokens are used here.
"""
from __future__ import annotations
import os, json, hashlib
from urllib.parse import quote
from pathlib import Path

CACHE = Path(os.environ.get("TRIP_CACHE", "/tmp/trip_cache")); CACHE.mkdir(parents=True, exist_ok=True)
KEY = os.environ.get("GOOGLE_MAPS_API_KEY")


def _cache(ns, k, producer):
    f = CACHE / f"{ns}_{hashlib.sha1(k.encode()).hexdigest()}.json"
    if f.exists():
        return json.loads(f.read_text())
    val = producer()
    f.write_text(json.dumps(val))
    return val


def links(name, city, lat=None, lng=None):
    q = quote(f"{name} {city}".strip())
    out = {
        "maps": f"https://www.google.com/maps/search/?api=1&query={q}",
        "tripadvisor": f"https://www.tripadvisor.com/Search?q={q}",
        "google_reviews": f"https://www.google.com/search?q={q}%20reviews",
    }
    if lat is not None and lng is not None:
        out["directions"] = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
    return out


def enrich(target: dict) -> dict:
    """Add links always; add Places facts if a key + requests are available."""
    name, city = target.get("name", ""), target.get("location", "")
    if KEY:
        try:
            import requests
            def fetch():
                r = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
                                 params={"input": f"{name} {city}", "inputtype": "textquery",
                                         "fields": "place_id,name,rating,user_ratings_total,"
                                                   "geometry,price_level,photos,opening_hours",
                                         "key": KEY}, timeout=10)
                return r.json()
            data = _cache("place", f"{name}|{city}", fetch)
            cand = (data.get("candidates") or [{}])[0]
            if cand:
                geo = cand.get("geometry", {}).get("location", {})
                target.setdefault("place_id", cand.get("place_id"))
                target.setdefault("lat", geo.get("lat")); target.setdefault("lng", geo.get("lng"))
                target.setdefault("stars", cand.get("rating"))
                target.setdefault("review_count", cand.get("user_ratings_total"))
                target.setdefault("price_level", cand.get("price_level"))
        except Exception:
            pass
    target["links"] = links(name, city, target.get("lat"), target.get("lng"))
    return target


def distance_matrix(origins: list[dict], dests: list[dict]) -> dict:
    """Return {f'{o_id}|{d_id}': drive_minutes}. Online if key, else haversine."""
    out = {}
    if KEY:
        try:
            import requests
            def oid(p): return p.get("place_id") or p["name"]
            def fetch():
                r = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json",
                                 params={"origins": "|".join(f"{o['lat']},{o['lng']}" for o in origins),
                                         "destinations": "|".join(f"{d['lat']},{d['lng']}" for d in dests),
                                         "key": KEY}, timeout=15)
                return r.json()
            data = _cache("matrix", json.dumps([[o.get("place_id", o["name"]) for o in origins],
                                                [d.get("place_id", d["name"]) for d in dests]]), fetch)
            for i, row in enumerate(data.get("rows", [])):
                for j, el in enumerate(row.get("elements", [])):
                    if el.get("status") == "OK":
                        out[f"{oid(origins[i])}|{oid(dests[j])}"] = el["duration"]["value"] / 60.0
            return out
        except Exception:
            pass
    # offline fallback
    from engine import haversine_km
    for o in origins:
        for d in dests:
            km = haversine_km((o["lat"], o["lng"]), (d["lat"], d["lng"]))
            out[f"{o.get('place_id', o['name'])}|{d.get('place_id', d['name'])}"] = km / 70.0 * 60.0
    return out


if __name__ == "__main__":
    import sys
    t = json.load(open(sys.argv[1]))
    print(json.dumps([enrich(x) for x in t], indent=2))
