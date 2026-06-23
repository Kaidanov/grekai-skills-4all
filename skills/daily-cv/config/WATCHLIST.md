# Watchlist — Sources and Companies to Monitor (v2)

---

## Primary Source A — techmap (Daily-Updated Israeli Tech Jobs)

The techmap project publishes fresh Israeli tech job CSVs to GitHub daily. Download and filter these first — they are the fastest, freshest source.

**Base URL:** `https://raw.githubusercontent.com/mluggy/techmap/main/jobs/`

| File | Best For | Filter |
|---|---|---|
| `software.csv` | VP R&D, VP Engineering, Head of R&D | `level=Executive`, `size in {m,l,xl}` |
| `product.csv` | VP Product, Director of Product | `level=Executive`, `size in {m,l,xl}` |
| `business.csv` | Head of Data, Director BI/AI | `level=Executive`, `size in {m,l,xl}` |
| `devops.csv` | Head of Platform, VP DevOps | `level=Executive`, `size in {m,l,xl}` |
| `security.csv` | CISO-adjacent R&D leadership | `level=Executive`, `size in {m,l,xl}` |

**CSV columns:** `company, category, size, title, level, city, url, updated`

**Size codes:** `xs`=<10, `s`=10-50, `m`=50-200, `l`=200-1000, `xl`=1000+

**Executive keywords to match in title:**
`vp r&d`, `vp engineering`, `cto`, `chief tech`, `head of r&d`, `head of engineering`,
`vp product`, `director of product`, `director r&d`, `vp devops`, `head of platform`,
`director of r&d`, `head of product`, `vp of r&d`, `vp of engineering`

**Recency filter:** `updated` field must be within 14 days of today (per R3 for techmap).

**Company name = None:** Fetch the `url` field to extract company name from the ATS page.

---

## Primary Source B — LinkedIn Jobs

For CTO/VP R&D roles not captured by techmap (per R24/R26). Search after techmap.

| Search Query | Filter |
|---|---|
| `"VP R&D" Israel Tel Aviv` | Last 30 days |
| `"VP Engineering" Israel Tel Aviv` | Last 30 days |
| `"CTO" Israel "Tel Aviv"` | Last 30 days |
| `"Head of R&D" Israel` | Last 30 days |

Use `site:linkedin.com/jobs` in WebSearch. Extract job IDs from results.

---

## Secondary Source — Greenhouse API (Israel Companies)

Scan these company slugs for Executive-level Israel roles.

```
monday, fiverr, riskified, jfrog, yotpo, tipalti, gong, bigid, aquasecurity,
forter, similarweb, armis, axonius, catonetworks, wiz, snyk, checkmarx,
cybereason, guardicore, illumio, orca, lacework, sysdig, torq, coralogix,
logz, datagen, lightricks, via, moovit, ironvest, payoneer, papaya, rapyd,
melio, lemonade, hippo, next-insurance, kape, expressvpn, ironnet,
sentinelone, cyberark, varonis, radware
```

**API pattern:** `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs`

**Title keywords:** `vp r&d`, `vp engineering`, `cto`, `head of r&d`, `director r&d`, `vp product`, `director of product`

**Location filter:** `israel` or `tel aviv` in location field.

**Note (R20):** Check both brand slug AND parent slug (e.g., `expressvpn` and `kape`).

---

## Priority: HIGH — GAMPA-Tier Companies with Israel Offices

| Company | Careers URL | ATS | Status |
|---|---|---|---|
| Microsoft Israel | `https://careers.microsoft.com` | direct | ACTIVE |
| Google Israel | `https://careers.google.com` | direct | ACTIVE |
| Amazon Israel (AWS) | `https://www.amazon.jobs` | direct | ACTIVE |
| Meta Israel | `https://www.metacareers.com` | direct | ACTIVE |
| NVIDIA Israel | `https://www.nvidia.com/en-us/about-nvidia/careers/` | direct | ACTIVE |
| Mobileye | `https://www.mobileye.com/careers/` | direct | ACTIVE |
| Palo Alto Networks Israel | `https://www.paloaltonetworks.com/company/careers` | direct | ACTIVE |
| Check Point | `https://www.checkpoint.com/careers/` | direct | ACTIVE |
| CrowdStrike Israel | `https://www.crowdstrike.com/careers/` | direct | ACTIVE |
| Wiz | `https://boards.greenhouse.io/wiz` | greenhouse | ACTIVE |
| Akamai Israel | `https://www.akamai.com/careers` | direct | ACTIVE |

---

## Priority: HIGH — Well-Known Israel Tech (Series B+ / Public)

| Company | Careers URL | ATS | Status |
|---|---|---|---|
| monday.com | `https://boards.greenhouse.io/monday` | greenhouse | ACTIVE |
| Wix | `https://www.wix.com/jobs` | direct | ACTIVE |
| JFrog | `https://www.jfrog.com/careers/` | greenhouse | ACTIVE |
| Fiverr | `https://www.fiverr.com/about/careers` | greenhouse | ACTIVE |
| Riskified | `https://www.riskified.com/careers/` | greenhouse | ACTIVE |
| CyberArk | `https://www.cyberark.com/company/careers/` | direct | ACTIVE |
| Varonis | `https://www.varonis.com/careers` | direct | ACTIVE |
| SentinelOne | `https://www.sentinelone.com/jobs/` | greenhouse | ACTIVE |
| Gong | `https://www.gong.io/careers/` | greenhouse | ACTIVE |
| BigID | `https://bigid.com/company/careers/` | greenhouse | ACTIVE |
| Armis | `https://www.armis.com/careers/` | greenhouse | ACTIVE |
| Axonius | `https://www.axonius.com/company/careers` | greenhouse | ACTIVE |
| Cato Networks | `https://www.catonetworks.com/company/careers/` | greenhouse | ACTIVE |
| Snyk | `https://snyk.io/careers/` | greenhouse | ACTIVE |
| Coralogix | `https://coralogix.com/careers/` | greenhouse | ACTIVE |
| Lightricks | `https://www.lightricks.com/careers` | greenhouse | ACTIVE |
| Payoneer | `https://www.payoneer.com/about/careers/` | greenhouse | ACTIVE |
| Rapyd | `https://www.rapyd.net/company/careers/` | greenhouse | ACTIVE |
| Melio | `https://meliopayments.com/careers/` | greenhouse | ACTIVE |
| Tipalti | `https://tipalti.com/company/careers/` | greenhouse | ACTIVE |
| Yotpo | `https://www.yotpo.com/about/careers/` | greenhouse | ACTIVE |
| Similarweb | `https://www.similarweb.com/corp/careers/` | greenhouse | ACTIVE |
| Torq | `https://torq.io/careers/` | greenhouse | ACTIVE |
| Via | `https://ridewithvia.com/careers` | greenhouse | ACTIVE |

---

## Priority: MEDIUM — Niche and Secondary Boards

| Source | URL | Search | Status |
|---|---|---|---|
| Built In Israel | `https://builtin.com/jobs/mena/israel` | Filter VP/Director level | ACTIVE |
| Wellfound (AngelList) | `https://wellfound.com/role/l/vp-of-engineering/israel` | VP Engineering Israel | ACTIVE |
| TechAviv | `https://techaviv.com/` | VC portfolio jobs | ACTIVE |
| Viola Ventures portfolio | `https://www.viola-group.com/portfolio/` | Portfolio company careers | ACTIVE |
| Sequoia Israel | `https://www.sequoiacap.com/israel/` | Portfolio careers | ACTIVE |
| Bessemer Israel | `https://www.bvp.com/` | Portfolio careers | ACTIVE |
| Lightspeed Israel | `https://lsvp.com/` | Portfolio careers | ACTIVE |
| site:boards.greenhouse.io | `site:boards.greenhouse.io "vp r&d" OR "vp engineering" israel` | Google search | ACTIVE |
| site:jobs.lever.co | `site:jobs.lever.co "vp r&d" OR "head of r&d" israel` | Google search | ACTIVE |
| site:apply.workable.com | `site:apply.workable.com "vp engineering" israel` | Google search | ACTIVE |

---

## Custom Career Page Patterns (R23)

When a company's ATS slug returns 404, check these URL patterns:

- `careers.[company].com`
- `jobs.[company].com`
- `makers.[company].com`
- `[company].com/careers`
- `[company].com/jobs`

---

## Proactive Outreach Targets

Recently funded Israeli tech companies where the target role may not yet be posted.

| Company | Raised | Round | Geography | Why Relevant | Outreach Status |
|---|---|---|---|---|---|
| Add targets here as funding announcements are found | — | — | — | — | `not_contacted` |

**Outreach timing:** 2-6 weeks after funding announcement.

---

## Underground and Less-Visible Sources

| Source | URL / Query | What to Search | Status |
|---|---|---|---|
| IVC Online | `https://www.ivc-online.com/` | Recent Israel funding rounds | ACTIVE |
| Geektime Israel jobs | `https://www.geektime.com/jobs/` | Executive tech roles | ACTIVE |
| Startup Nation Central | `https://www.startupnationcentral.org/` | VC-backed company directory | ACTIVE |
| TechCrunch Israel | `site:techcrunch.com Israel funding 2025 2026` | Recent rounds | ACTIVE |
| Crunchbase | `https://www.crunchbase.com/` | Israel Series B+ companies | ACTIVE |

---

## How the Skill Uses This File

On each run:
1. Download all 5 techmap CSVs and filter for Executive-level, size m/l/xl, matching keywords, updated ≤ 14 days.
2. Search LinkedIn for CTO/VP R&D with last-30-days filter.
3. Scan Greenhouse API for listed company slugs.
4. Check HIGH priority watchlist company career pages directly.
5. Use MEDIUM sources if HIGH sources yield nothing qualifying.
6. Apply R1-R29 rules to every candidate before selection.
