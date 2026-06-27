"""
generate_brochure.py — render a trip bundle into a single self-contained HTML
brochure (print-to-PDF ready). Destination-agnostic.

Usage:  python generate_brochure.py bundle.json out.html
"""
from __future__ import annotations
import json, sys, html

CSS = """
:root{--ink:#1f2d33;--accent:#1F4E5F;--soft:#eef4f6;--line:#d9e2e6}
*{box-sizing:border-box}body{margin:0;font-family:Georgia,'Times New Roman',serif;color:var(--ink);line-height:1.5}
.wrap{max-width:880px;margin:0 auto;padding:32px}
.cover{background:linear-gradient(135deg,#1F4E5F,#2e6f80);color:#fff;border-radius:16px;padding:40px;margin-bottom:28px}
.cover h1{font-size:38px;margin:0 0 8px}.cover p{margin:2px 0;opacity:.9;font-family:Helvetica,Arial,sans-serif}
h2{font-family:Helvetica,Arial,sans-serif;color:var(--accent);border-bottom:2px solid var(--line);padding-bottom:6px;margin-top:34px}
.day{background:var(--soft);border-left:4px solid var(--accent);border-radius:8px;padding:14px 18px;margin:12px 0}
.day .d{font-family:Helvetica,Arial,sans-serif;font-weight:700;color:var(--accent)}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.card{border:1px solid var(--line);border-radius:10px;padding:14px;font-family:Helvetica,Arial,sans-serif;font-size:14px}
.card h3{margin:0 0 4px;font-size:16px}.stars{color:#e0a106;font-weight:700}
.meta{color:#5b6b72;font-size:13px;margin:4px 0}.tag{display:inline-block;background:var(--soft);border-radius:20px;padding:2px 10px;font-size:12px;margin-right:6px}
.links a{font-size:12px;margin-right:10px;color:#1155CC;text-decoration:none}
.warn{background:#fff4f4;border:1px solid #e7b4b4;border-radius:8px;padding:10px 14px;margin:8px 0;font-family:Helvetica,Arial,sans-serif;font-size:14px}
.note{font-family:Helvetica,Arial,sans-serif;font-size:14px;margin:6px 0}
@media print{.cover{-webkit-print-color-adjust:exact;print-color-adjust:exact}.cards{grid-template-columns:1fr 1fr}}
"""


def _stars(v):
    try: f = float(str(v).split("/")[0])
    except Exception: return ""
    full = "★" * int(round(f)); return f'<span class="stars">{full} {v}</span>'


def _card(x, food=False):
    name = html.escape(str(x.get("name", "")))
    loc = html.escape(str(x.get("location", "")))
    rating = x.get("popularity") or x.get("reviews") or x.get("stars") or ""
    desc = html.escape(str(x.get("notes") or x.get("specialty") or x.get("highlights") or ""))
    price = html.escape(str(x.get("price") or x.get("cost") or ""))
    lk = x.get("links") or {}
    from urllib.parse import quote
    gm = lk.get("maps") or f"https://www.google.com/maps/search/?api=1&query={quote(name+' '+loc)}"
    ta = lk.get("tripadvisor") or f"https://www.tripadvisor.com/Search?q={quote(name+' '+loc)}"
    flag = "⭐ " if (x.get("importer_flag") or "⭐" in str(x.get("special", ""))) else ""
    dist = x.get("_drive_from_base")
    dist_html = f'<div class="meta">≈ {dist} min from base</div>' if dist else ""
    return f"""<div class="card"><h3>{flag}{name}</h3>
      <div class="meta">{loc} {('· '+price) if price else ''}</div>
      <div>{_stars(rating)}</div>{dist_html}
      <div class="meta">{desc}</div>
      <div class="links"><a href="{gm}">Map / Go ▸</a><a href="{ta}">Reviews ▸</a></div></div>"""


def build(bundle: dict, out: str):
    t = bundle.get("trip", {})
    tr = t.get("travelers") or {}
    who = f"{tr.get('adults','')} adults + {tr.get('children',0)} children" if tr else ""
    parts = [f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="wrap">']
    parts.append(f'<div class="cover"><h1>{html.escape(t.get("name","Trip"))}</h1>'
                 f'<p>{t.get("date_start","")} → {t.get("date_end","")}</p><p>{who}</p></div>')

    if bundle.get("warnings"):
        parts.append("<h2>Before you go</h2>")
        for w in bundle["warnings"]:
            parts.append(f'<div class="warn">⚠ {html.escape(w.get("msg", str(w)))}</div>')

    parts.append("<h2>Itinerary</h2>")
    for d in bundle.get("itinerary", []):
        parts.append(f'<div class="day"><span class="d">Day {d.get("day")} · {d.get("date")} · '
                     f'{html.escape(str(d.get("location","")))}</span>'
                     f'<div class="note">{html.escape(str(d.get("activities","")))}</div></div>')

    if bundle.get("attractions"):
        parts.append("<h2>Attractions</h2><div class='cards'>")
        parts += [_card(a) for a in bundle["attractions"]]
        parts.append("</div>")
    if bundle.get("foodies"):
        parts.append("<h2>Where to eat</h2><div class='cards'>")
        parts += [_card(f, food=True) for f in bundle["foodies"]]
        parts.append("</div>")
    notes = bundle.get("notes", [])
    if notes:
        parts.append("<h2>Notes &amp; tips</h2>")
        for n in notes:
            text = n[0] if isinstance(n, (list, tuple)) else n
            parts.append(f'<div class="note">{html.escape(str(text))}</div>')

    parts.append("</div></body></html>")
    open(out, "w", encoding="utf-8").write("\n".join(parts))
    return out


if __name__ == "__main__":
    bundle = json.load(open(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else "trip.html"
    print(build(bundle, out))
