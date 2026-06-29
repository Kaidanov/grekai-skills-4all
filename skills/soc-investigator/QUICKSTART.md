# SOC Investigator — Quickstart (one page)

Lazy is fine. Run these in order, top to bottom. ~10 minutes the first time, ~2 after.

> **Your folder (remember it):** keep everything in **`~/.claude/skills/soc-investigator/`**.
> `config.json` is your memory — your IOCs, machine groups and thresholds persist
> between runs. Defender exports go in `exports/defender/`, results land in `out/`.

### 0 · VirusTotal key — once
[virustotal.com](https://www.virustotal.com) → sign in → top-right avatar → **API key** → copy it, then:
```powershell
setx VT_API_KEY "PASTE_YOUR_KEY"      # Windows (reopen the terminal after)
```
```bash
export VT_API_KEY="PASTE_YOUR_KEY"    # macOS / Linux
```

### 1 · Your IOCs
```bash
cp assets/config.example.json config.json
```
Edit `config.json` → put what you're chasing in `iocs`, e.g.:
```json
"iocs": { "domains": ["bad-domain.example"], "urls": [], "hashes": ["44d88612fea8a8f36de82e1278abb02f"] }
```

### 2 · Make the Defender queries
```bash
python3 scripts/gen_queries.py --config config.json
```
→ one file per machine type in `out/queries/defender_*.kql`.

### 3 · Hunt in Defender  *(your browser)*
[security.microsoft.com](https://security.microsoft.com) → **Hunting → Advanced hunting** →
paste each `.kql` → **Run** → **Export → CSV** → save into **`exports/defender/`**.

### 4 · Enrich  *(makes the Sentinel file)*
```bash
python3 scripts/enrich.py --config config.json
```
You now have, in `out/`:
- **`report.md`** — who/what is malicious, which machines & users.
- **`sentinel_filled.kql`** ← **the ready-for-Sentinel file** (entities already filled in).
- `soc_report.csv` — upload to Threat Sentinel (soc-update.com).

### 5 · Sentinel  *(your browser)*
[portal.azure.com](https://portal.azure.com) → Microsoft Sentinel → **Logs** →
paste **`out/sentinel_filled.kql`** → **Run** → that's every affected machine + user.

### 6 · Approve & close
Skim `out/report.md`, then close those incidents in Sentinel with the classification +
comment from your `config.json` `closing` block. Done.

---

**Want it hands-off?** Once you have API keys, `scripts/run_local.py` runs steps 2–5
automatically and only stops for your approval before closing — see
[`references/local-automation.md`](./references/local-automation.md).
