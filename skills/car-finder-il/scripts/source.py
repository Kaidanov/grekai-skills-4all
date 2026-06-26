"""
source.py — where listings come from.

Two adapters, one tiny interface: fetch_listings(criteria) -> [listing dict].

  apify : calls a Yad2-vehicles actor on Apify over plain HTTPS (no browser,
          no login, the actor handles the anti-bot IPs for you).
  mock  : reads examples/sample_listings.json so you can test the whole
          pipeline with zero tokens and zero network.

Stdlib only. Listings are normalised to a stable shape the scorer trusts:

  {id, title, make, model, year, km, hand, owner_type, price, photos, url, source}

Why Apify and not a raw scraper: Yad2 runs PerimeterX and flags datacenter
IPs hard. A maintained actor absorbs that. We never POST/login here — reads
only. To pick an actor: apify.com/store, search "yad2", copy its actor id
into APIFY_ACTOR_ID. The actor's own input schema varies, so you can pass a
raw `apify_input` block in your criteria to control it precisely.
"""
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

APIFY_BASE = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"


def fetch_listings(criteria, source="apify", timeout=180):
    if source == "mock":
        return _mock()
    if source == "apify":
        return _apify(criteria, timeout)
    raise ValueError("unknown source: %r (use apify|mock)" % source)


# --------------------------------------------------------------------------- #
def _apify(criteria, timeout):
    token = os.environ.get("APIFY_TOKEN")
    actor = os.environ.get("APIFY_ACTOR_ID")
    if not token:
        raise RuntimeError("APIFY_TOKEN not set — export it or use --source mock")
    if not actor:
        raise RuntimeError(
            "APIFY_ACTOR_ID not set — pick a Yad2 vehicles actor at "
            "apify.com/store (search 'yad2') and export its id"
        )
    body = criteria.get("apify_input") or _default_input(criteria)
    url = APIFY_BASE.format(actor=actor.replace("/", "~")) + "?token=" + token
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("Apify HTTP %s: %s" % (e.code, e.read()[:300]))
    return [_normalise(x) for x in raw if isinstance(x, dict)]


def _default_input(criteria):
    """A minimal, common-shape input. Override via criteria['apify_input']
    if your chosen actor expects something different."""
    inp = {}
    if criteria.get("make"):
        inp["manufacturer"] = criteria["make"]
    if criteria.get("model"):
        inp["model"] = criteria["model"]
    if criteria.get("year_min"):
        inp["yearMin"] = criteria["year_min"]
    if criteria.get("price_max"):
        inp["priceMax"] = criteria["price_max"]
    inp["maxItems"] = criteria.get("max_items", 120)
    return inp


# --------------------------------------------------------------------------- #
_FIELDS = {
    "id": ("id", "listingId", "adNumber", "token", "orderId"),
    "title": ("title", "name", "heading"),
    "make": ("make", "manufacturer", "manufacturerName", "brand"),
    "model": ("model", "modelName", "commercialNickname"),
    "year": ("year", "productionYear", "modelYear"),
    "km": ("km", "kilometers", "mileage", "kilometrage"),
    "hand": ("hand", "currentOwner", "ownerNumber", "yad"),
    "owner_type": ("ownerType", "previousOwner", "owner"),
    "price": ("price", "priceValue", "amount"),
    "url": ("url", "link", "adUrl", "permalink"),
}


def _normalise(x):
    out = {}
    for key, candidates in _FIELDS.items():
        out[key] = _first(x, candidates)
    out["price"] = _to_int(out.get("price"))
    out["year"] = _to_int(out.get("year"))
    out["km"] = _to_int(out.get("km"))
    out["hand"] = _to_int(out.get("hand"))
    out["photos"] = _photo_count(x)
    out["owner_type"] = _owner(out.get("owner_type"))
    out["source"] = "yad2"
    if not out.get("url") and out.get("id"):
        out["url"] = "https://www.yad2.co.il/item/%s" % out["id"]
    if not out.get("id"):
        out["id"] = out.get("url") or json.dumps(x, sort_keys=True)[:64]
    return out


def _first(d, keys):
    for k in keys:
        if k in d and d[k] not in (None, "", []):
            return d[k]
    return None


def _to_int(v):
    if v is None:
        return None
    try:
        return int(float(str(v).replace(",", "").replace("₪", "").strip()))
    except (ValueError, TypeError):
        return None


def _photo_count(x):
    for k in ("images", "photos", "imageUrls", "pictures"):
        v = x.get(k)
        if isinstance(v, list):
            return len(v)
    n = x.get("imagesCount") or x.get("photoCount")
    return _to_int(n) or 0


def _owner(v):
    if not v:
        return None
    s = str(v).lower()
    if any(t in s for t in ("private", "פרטי")):
        return "private"
    if any(t in s for t in ("company", "חברה", "ליסינג", "lease", "rental", "השכרה")):
        return "company"
    return s


def _mock():
    p = Path(__file__).resolve().parent.parent / "examples" / "sample_listings.json"
    raw = json.loads(p.read_text(encoding="utf-8"))
    return [_normalise(x) for x in raw]
