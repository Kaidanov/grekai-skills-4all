# Sentinel KQL catalog

Run these in **Microsoft Sentinel → Logs**. The first is auto-filled for you by
`scripts/enrich.py` (`out/sentinel_filled.kql`) with your confirmed suspect
entities already injected; the others are manual helpers.

---

## S1 — Blast radius (every machine + user that touched a confirmed IOC)

`enrich.py` writes this with `SuspectIocs`, `SuspectDevices`, and `SuspectUsers`
populated from the VirusTotal-confirmed rows. Template:

```kusto
let LookBack = {time_window_days}d;
let SuspectIocs    = dynamic([ ...confirmed IOCs... ]);
let SuspectDevices = dynamic([ ...suspect device names... ]);
let SuspectUsers   = dynamic([ ...suspect users... ]);
let Net =
    DeviceNetworkEvents
    | where Timestamp > ago(LookBack)
    | where RemoteUrl has_any (SuspectIocs) or RemoteIP in (SuspectIocs)
    | project Timestamp, Device = DeviceName, User = InitiatingProcessAccountName,
              Ioc = coalesce(RemoteUrl, RemoteIP);
let Alerts =
    SecurityAlert
    | where TimeGenerated > ago(LookBack)
    | where Entities has_any (SuspectDevices) or Entities has_any (SuspectUsers)
    | project Timestamp = TimeGenerated, Device = CompromisedEntity, User = "",
              Ioc = AlertName;
union Net, Alerts
| where Device in (SuspectDevices) or User in (SuspectUsers)
     or Ioc has_any (SuspectIocs)
| summarize Hits = count(), FirstSeen = min(Timestamp), LastSeen = max(Timestamp),
            Iocs = make_set(Ioc, 20) by Device, User
| sort by Hits desc
```

> Table names vary by connector. If `DeviceNetworkEvents` isn't onboarded to your
> workspace, swap in `CommonSecurityLog` (`DestinationHostName`, `RequestURL`) or
> the M365 Defender `DeviceNetworkEvents` table via the Defender data connector.

---

## S2 — Map suspect entities → open incidents (for the close step)

Use this to find which incidents to close after you've confirmed the blast radius.

```kusto
let SuspectDevices = dynamic([ ...suspect device names... ]);
let SuspectUsers   = dynamic([ ...suspect users... ]);
SecurityIncident
| where Status != "Closed"
| where AlertIds has_any (
    SecurityAlert
    | where Entities has_any (SuspectDevices) or Entities has_any (SuspectUsers)
    | project SystemAlertId)
| project IncidentNumber, Title, Severity, Status, Owner, CreatedTime,
          IncidentUrl = Url
| sort by CreatedTime desc
```

---

## S3 — Closing incidents (HUMAN-CONFIRMED — do NOT automate)

`enrich.py` and the agent prepare the close package: the incident list from S2,
the classification from `config.closing` (e.g. `TruePositive` /
`SuspiciousActivity`), and a justification comment built from
`closing.comment_template`. **You** then, in the Sentinel UI:

1. Open each incident from S2.
2. Set **Status → Closed**, pick the classification + reason.
3. Paste the prepared comment.

Never bulk-close programmatically and never report incidents as closed until the
human confirms they clicked Close.
