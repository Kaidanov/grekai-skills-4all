"""
score.py — the actual value of this skill.

Yad2's own saved-search alerts ping you on EVERYTHING that matches crude
filters. This scorer only surfaces cars that are genuinely good: priced below
their own peer cohort, low hand, sane km, private owner where you asked for it.

No מחירון API exists, so we don't pretend to have one. Instead we benchmark
each car against ITS OWN cohort — same make+model, year within ±1 — pulled in
the same fetch. "12% under the median of comparable listings" is honest,
self-contained, and needs no external price feed.

Pure functions. The CLI handles I/O and EN/HE rendering of the reason codes.
"""
import statistics


def apply(listings, criteria):
    """Filter by hard rules, then score. Returns a list sorted best-first,
    each item: {listing, score, reasons:[(code, value)], cohort_median}."""
    kept = [l for l in listings if _passes(l, criteria)]
    cohorts = _cohorts(kept)
    weights = _weights(criteria)
    scored = []
    for l in kept:
        med = cohorts.get(_cohort_key(l))
        s, reasons = _score_one(l, criteria, med, weights)
        scored.append({"listing": l, "score": s, "reasons": reasons,
                       "cohort_median": med})
    scored.sort(key=lambda r: r["score"], reverse=True)
    floor = criteria.get("min_score", 0)
    return [r for r in scored if r["score"] >= floor]


# --------------------------------------------------------------------------- #
def _passes(l, c):
    if c.get("price_max") and (l["price"] or 10**9) > c["price_max"]:
        return False
    if c.get("price_min") and (l["price"] or 0) < c["price_min"]:
        return False
    if c.get("year_min") and (l["year"] or 0) < c["year_min"]:
        return False
    if c.get("km_max") and (l["km"] or 10**9) > c["km_max"]:
        return False
    if c.get("hand_max") and (l["hand"] or 99) > c["hand_max"]:
        return False
    if c.get("owner_type") and l.get("owner_type") and \
            l["owner_type"] not in c["owner_type"]:
        return False
    if c.get("make") and not _match(l.get("make"), c["make"]):
        return False
    if c.get("model") and not _match(l.get("model"), c["model"]):
        return False
    return True


def _match(value, wanted):
    if not value:
        return True  # don't drop on missing data
    v = str(value).lower()
    return any(str(w).lower() in v or v in str(w).lower() for w in wanted)


def _cohort_key(l):
    return (str(l.get("make") or "").lower(),
            str(l.get("model") or "").lower(),
            (l.get("year") or 0) // 2)


def _cohorts(listings):
    buckets = {}
    for l in listings:
        if l.get("price"):
            buckets.setdefault(_cohort_key(l), []).append(l["price"])
    return {k: statistics.median(v) for k, v in buckets.items() if len(v) >= 3}


def _weights(c):
    base = {"price_value": 0.40, "hand": 0.15, "owner": 0.15,
            "km": 0.15, "photos": 0.05, "fresh": 0.10}
    base.update(c.get("weights") or {})
    return base


def _score_one(l, c, median, w):
    parts, reasons = {}, []

    # price vs cohort (the heavy one)
    if median and l.get("price"):
        delta = (median - l["price"]) / median  # +ve = cheaper than peers
        parts["price_value"] = _clamp(0.5 + delta * 2.5)
        pct = round(delta * 100)
        if pct >= 3:
            reasons.append(("under_peers", pct))
        elif pct <= -3:
            reasons.append(("over_peers", -pct))
    else:
        parts["price_value"] = 0.5  # no cohort → neutral, not penalised

    # hand
    h = l.get("hand")
    if h is not None:
        parts["hand"] = _clamp(1 - (h - 1) * 0.25)
        if h <= 1:
            reasons.append(("first_hand", h))
    else:
        parts["hand"] = 0.5

    # owner type
    if l.get("owner_type") == "private":
        parts["owner"] = 1.0
        reasons.append(("private_owner", None))
    elif l.get("owner_type") == "company":
        parts["owner"] = 0.3
        reasons.append(("company_owner", None))
    else:
        parts["owner"] = 0.5

    # km per year
    parts["km"] = _km_score(l, reasons)

    # photos
    pc = l.get("photos") or 0
    parts["photos"] = _clamp(pc / 8.0)
    if pc < 3:
        reasons.append(("few_photos", pc))

    # freshness — unknown at fetch time, neutral; the runner flags NEW separately
    parts["fresh"] = 0.5

    total = sum(parts[k] * w.get(k, 0) for k in parts)
    denom = sum(w.get(k, 0) for k in parts) or 1
    return round(100 * total / denom), reasons


def _km_score(l, reasons):
    if not (l.get("km") and l.get("year")):
        return 0.5
    age = max(1, 2026 - l["year"])
    per_year = l["km"] / age
    if per_year <= 12000:
        reasons.append(("low_km", round(per_year)))
        return 1.0
    if per_year >= 25000:
        reasons.append(("high_km", round(per_year)))
        return 0.2
    return _clamp(1 - (per_year - 12000) / 13000)


def _clamp(x):
    return max(0.0, min(1.0, x))
