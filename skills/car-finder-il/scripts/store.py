"""
store.py — "have I already pinged the user about this car?"

A thin wrapper over Supabase PostgREST (stdlib urllib, no SDK). It lets the
scheduled run push ONLY on genuinely new listings or real price drops, instead
of re-spamming the same cars every few hours.

Needs SUPABASE_URL and SUPABASE_KEY (use the service_role key in the cron —
the seen_listings table is RLS-locked and not meant for the public anon key).

If those env vars are absent, store falls back to a local JSON file
(~/.car-finder-il/seen.json) so dedupe still works standalone across runs —
you just don't get the cloud copy or cross-machine sharing.
"""
import json
import os
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

TABLE = "seen_listings"
LOCAL = Path.home() / ".car-finder-il" / "seen.json"


class Store:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.live = bool(self.url and self.key)
        self._mem = {} if self.live else self._load_local()

    # -- local file fallback -------------------------------------------------
    def _load_local(self):
        try:
            return json.loads(LOCAL.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            return {}

    def _save_local(self):
        LOCAL.parent.mkdir(parents=True, exist_ok=True)
        LOCAL.write_text(json.dumps(self._mem, ensure_ascii=False), encoding="utf-8")

    # -- read ----------------------------------------------------------------
    def seen(self, criteria_id):
        """Return {listing_id: last_price} already on record."""
        if not self.live:
            return dict(self._mem.get(criteria_id, {}))
        q = ("%s/rest/v1/%s?criteria_id=eq.%s&select=listing_id,last_price"
             % (self.url.rstrip("/"), TABLE,
                urllib.parse.quote(criteria_id)))
        rows = self._get(q)
        return {r["listing_id"]: r.get("last_price") for r in rows}

    # -- write ---------------------------------------------------------------
    def remember(self, criteria_id, results):
        rows = []
        for r in results:
            l = r["listing"]
            rows.append({
                "criteria_id": criteria_id,
                "listing_id": str(l["id"]),
                "source": l.get("source", "yad2"),
                "title": l.get("title"),
                "url": l.get("url"),
                "price": l.get("price"),
                "last_price": l.get("price"),
                "score": r.get("score"),
                "last_seen": "now()",
            })
        if not rows:
            return
        if not self.live:
            store = self._mem.setdefault(criteria_id, {})
            for row in rows:
                store[row["listing_id"]] = row["last_price"]
            self._save_local()
            return
        self._upsert(rows)

    # -- diff ----------------------------------------------------------------
    @staticmethod
    def split_new(results, seen):
        """Partition scored results into (new, price_dropped) vs seen."""
        fresh, dropped = [], []
        for r in results:
            lid = str(r["listing"]["id"])
            price = r["listing"].get("price")
            if lid not in seen:
                fresh.append(r)
            elif price and seen[lid] and price < seen[lid]:
                r["dropped_from"] = seen[lid]
                dropped.append(r)
        return fresh, dropped

    # -- http ----------------------------------------------------------------
    def _headers(self, extra=None):
        h = {"apikey": self.key, "Authorization": "Bearer " + self.key,
             "Content-Type": "application/json"}
        if extra:
            h.update(extra)
        return h

    def _get(self, url):
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _upsert(self, rows):
        url = "%s/rest/v1/%s?on_conflict=criteria_id,listing_id" % (
            self.url.rstrip("/"), TABLE)
        req = urllib.request.Request(
            url, data=json.dumps(rows).encode("utf-8"),
            headers=self._headers({"Prefer": "resolution=merge-duplicates"}),
            method="POST")
        try:
            urllib.request.urlopen(req, timeout=30).read()
        except urllib.error.HTTPError as e:
            raise RuntimeError("Supabase upsert %s: %s" % (e.code, e.read()[:300]))
