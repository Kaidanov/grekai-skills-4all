# Global AI usage dashboard — all CLI tools + per-project drill-down.
#  - Cross-tool totals / by-provider / by-model / daily  : from `ccusage` (Claude, Codex,
#    Gemini-CLI, Ollama, OpenClaw — every coding CLI ccusage detects).
#  - Per-project + drill-down (by model / day / session)  : scanned from ~/.claude/projects/
#    (Claude Code only — the one tool that records per-project transcripts locally).
#  - GitHub Copilot (VSCode) and Antigravity (Gemini IDE) report to their VENDOR accounts,
#    not local logs, so they can't be pulled here without vendor API tokens — a deep-link tile
#    is shown instead.
# Self-contained: Chart.js vendored locally, all dynamic strings HTML-escaped. No CDN, no keys.
#   Run:  powershell -NoProfile -ExecutionPolicy Bypass -File usage-dashboard.ps1 -Open
param([switch]$Open)
$ErrorActionPreference = 'SilentlyContinue'

$projectsDir = Join-Path $env:USERPROFILE '.claude\projects'
$outHtml     = Join-Path $env:USERPROFILE '.claude\usage-dashboard.html'

$PRICES = @{
    'opus'   = @{ in = 5.0; out = 25.0; cr = 0.5; cw5 = 6.25; cw1 = 10.0 }
    'sonnet' = @{ in = 3.0; out = 15.0; cr = 0.3; cw5 = 3.75; cw1 = 6.0  }
    'haiku'  = @{ in = 1.0; out = 5.0;  cr = 0.1; cw5 = 1.25; cw1 = 2.0  }
}
function Get-Price($label) { foreach ($k in $PRICES.Keys) { if ($label -like "*$k*") { return $PRICES[$k] } } return $PRICES['sonnet'] }
function Get-Num($obj, $name) { if ($obj -and ($obj.PSObject.Properties.Name -contains $name)) { return [double]$obj.$name } return 0 }
function Add-To($table, $key, $val) { $table[$key] = (Get-Num ([pscustomobject]$table) $key) + $val }
function To-Label($model) {
    if (-not $model) { return 'unknown' }
    $s = $model -replace '^claude-', ''; $s = $s -replace '-\d{8}$', ''; $s = $s -replace '-(\d+)$', '.$1'; return $s
}
function Get-Provider($model) {
    $m = "$model".ToLower()
    if ($m -match 'claude|opus|sonnet|haiku') { return 'Claude' }
    if ($m -match 'gpt|codex|^o\d') { return 'OpenAI / Codex' }
    if ($m -match 'gemini') { return 'Gemini' }
    if ($m -match 'llama|qwen|mistral|phi') { return 'Local / Ollama' }
    return 'Other'
}

# ---- 1. Cross-tool totals from ccusage -------------------------------------
$ccProvider = @{}; $ccModel = @{}; $ccDay = @{}; $ccTotal = 0.0; $ccTokens = 0.0; $tools = @{}
$cc = $null
try { $cc = (& ccusage daily --json 2>$null | Out-String | ConvertFrom-Json) } catch {}
if ($cc -and $cc.daily) {
    foreach ($d in $cc.daily) {
        $ccTotal += [double]$d.totalCost; $ccTokens += [double]$d.totalTokens
        if ($d.period) { Add-To $ccDay ([string]$d.period) ([double]$d.totalCost) }
        foreach ($a in $d.metadata.agents) { $tools["$a"] = $true }
        foreach ($mb in $d.modelBreakdowns) {
            $mn = [string]$mb.modelName
            if ($mn -match 'synthetic') { continue }
            Add-To $ccModel (To-Label $mn) ([double]$mb.cost)
            Add-To $ccProvider (Get-Provider $mn) ([double]$mb.cost)
        }
    }
}

# ---- 2. Per-project + drill-down (Claude Code transcripts) ------------------
function Measure-Transcript([string[]]$files) {
    # returns cost/tokens/last/byModel for a set of jsonl files, de-duped by message id
    $seen = New-Object 'System.Collections.Generic.HashSet[string]'
    $r = @{ cost = 0.0; tokens = 0.0; last = ''; byModel = @{}; byDay = @{} }
    foreach ($f in $files) {
        foreach ($line in [System.IO.File]::ReadLines($f)) {
            if ($line -notlike '*"usage"*') { continue }
            try { $o = $line | ConvertFrom-Json } catch { continue }
            $u = $o.message.usage; if (-not $u) { continue }
            $label = To-Label $o.message.model
            if ($label -match 'synthetic') { continue }
            if ($o.message -and ($o.message.PSObject.Properties.Name -contains 'id') -and $o.message.id) {
                if (-not $seen.Add([string]$o.message.id)) { continue }
            }
            $p = Get-Price $label
            $inT = Get-Num $u 'input_tokens'; $outT = Get-Num $u 'output_tokens'
            $crT = Get-Num $u 'cache_read_input_tokens'; $ccT = Get-Num $u 'cache_creation_input_tokens'
            $c5 = 0; $c1 = 0
            if (($u.PSObject.Properties.Name -contains 'cache_creation') -and $u.cache_creation) {
                $c5 = Get-Num $u.cache_creation 'ephemeral_5m_input_tokens'; $c1 = Get-Num $u.cache_creation 'ephemeral_1h_input_tokens'
            }
            if (($c5 + $c1) -le 0 -and $ccT -gt 0) { $c1 = $ccT }
            $cost = ($inT * $p.in + $outT * $p.out + $crT * $p.cr + $c5 * $p.cw5 + $c1 * $p.cw1) / 1e6
            $tok = $inT + $outT + $crT + $c5 + $c1
            $r.cost += $cost; $r.tokens += $tok
            Add-To $r.byModel $label $cost
            $ts = [string]$o.timestamp
            if ($ts.Length -ge 10) { Add-To $r.byDay ($ts.Substring(0, 10)) $cost; if ($ts -gt $r.last) { $r.last = $ts } }
        }
    }
    return $r
}
function ToPairs($table, $keyName, $valName) {
    @($table.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
        $h = @{}; $h[$keyName] = $_.Key; $h[$valName] = [math]::Round($_.Value, 2); [pscustomobject]$h })
}

$projects = @()
if (Test-Path $projectsDir) {
    foreach ($folder in (Get-ChildItem $projectsDir -Directory)) {
        $sessionFiles = @(Get-ChildItem $folder.FullName -File -Filter *.jsonl)
        if ($sessionFiles.Count -eq 0) { continue }
        # real path from any cwd line
        $cwd = $null
        foreach ($f in ($sessionFiles | Sort-Object LastWriteTime -Descending)) {
            foreach ($line in [System.IO.File]::ReadLines($f.FullName)) {
                if ($line -notlike '*"cwd"*') { continue }
                try { $o = $line | ConvertFrom-Json } catch { continue }
                if ($o.cwd) { $cwd = [string]$o.cwd; break }
            }
            if ($cwd) { break }
        }
        $pCost = 0.0; $pTok = 0.0; $pLast = ''; $pByModel = @{}; $pByDay = @{}; $sessions = @()
        foreach ($sf in $sessionFiles) {
            $sid = [System.IO.Path]::GetFileNameWithoutExtension($sf.Name)
            $subDir = Join-Path $folder.FullName "$sid\subagents"
            $files = @($sf.FullName)
            if (Test-Path $subDir) { $files += @(Get-ChildItem $subDir -Recurse -Filter *.jsonl -File).FullName }
            $m = Measure-Transcript $files
            if ($m.tokens -le 0) { continue }
            $pCost += $m.cost; $pTok += $m.tokens
            if ($m.last -gt $pLast) { $pLast = $m.last }
            foreach ($k in $m.byModel.Keys) { Add-To $pByModel $k $m.byModel[$k] }
            foreach ($k in $m.byDay.Keys) { Add-To $pByDay $k $m.byDay[$k] }
            $topModel = ($m.byModel.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
            $sessions += [pscustomobject]@{ id = $sid.Substring(0, [Math]::Min(8, $sid.Length)); cost = [math]::Round($m.cost, 2); tokens = [long]$m.tokens; model = $topModel; last = if ($m.last.Length -ge 10) { $m.last.Substring(0, 10) } else { '' } }
        }
        if ($pTok -le 0) { continue }
        $projects += [pscustomobject]@{
            name = if ($cwd) { Split-Path -Leaf $cwd } else { $folder.Name }
            path = if ($cwd) { $cwd } else { $folder.Name }
            cost = [math]::Round($pCost, 2); tokens = [long]$pTok
            last = if ($pLast.Length -ge 10) { $pLast.Substring(0, 10) } else { '' }
            byModel = @(ToPairs $pByModel 'label' 'cost')
            byDay = @($pByDay.GetEnumerator() | Sort-Object Name | ForEach-Object { [pscustomobject]@{ day = $_.Key; cost = [math]::Round($_.Value, 2) } })
            sessions = @($sessions | Sort-Object cost -Descending)
        }
    }
}
$projects = @($projects | Sort-Object cost -Descending)

# Normalize per-project cost estimates to ccusage's authoritative Claude total (the scan's
# cache-tier pricing over-counts; this keeps proportions but makes the totals consistent).
$claudeTotal = (Get-Num ([pscustomobject]$ccProvider) 'Claude')
$scanSum = ($projects | Measure-Object cost -Sum).Sum
if ($claudeTotal -gt 0 -and $scanSum -gt 0) {
    $factor = $claudeTotal / $scanSum
    foreach ($p in $projects) {
        $p.cost = [math]::Round($p.cost * $factor, 2)
        foreach ($mm in $p.byModel) { $mm.cost = [math]::Round($mm.cost * $factor, 2) }
        foreach ($dd in $p.byDay) { $dd.cost = [math]::Round($dd.cost * $factor, 2) }
        foreach ($ss in $p.sessions) { $ss.cost = [math]::Round($ss.cost * $factor, 2) }
    }
    $projects = @($projects | Sort-Object cost -Descending)
}

$data = @{
    generated = (Get-Date).ToString('yyyy-MM-dd HH:mm')
    ccTotal = [math]::Round($ccTotal, 2); ccTokens = [long]$ccTokens
    toolCount = ($tools.Keys).Count; projectCount = $projects.Count
    byProvider = @(ToPairs $ccProvider 'label' 'cost')
    byModel = @(ToPairs $ccModel 'label' 'cost')
    byDay = @($ccDay.GetEnumerator() | Sort-Object Name | ForEach-Object { [pscustomobject]@{ day = $_.Key; cost = [math]::Round($_.Value, 2) } })
    projects = $projects
} | ConvertTo-Json -Depth 8 -Compress

# Vendor Chart.js locally (no CDN / no SRI; works offline). One-time download.
$chartJs = Join-Path $env:USERPROFILE '.claude\chart.umd.min.js'
if (-not (Test-Path $chartJs)) {
    try { Invoke-WebRequest -Uri 'https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js' -OutFile $chartJs -UseBasicParsing -TimeoutSec 30 } catch {}
}

$html = @'
<!doctype html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AI Usage Dashboard</title>
<script src="chart.umd.min.js"></script>
<style>
 :root{--bg:#0f1116;--card:#181b22;--fg:#e6e6e6;--muted:#9aa4b2;--accent:#4ea1ff}
 *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,Segoe UI,Roboto,sans-serif}
 header{padding:20px 24px;border-bottom:1px solid #262b35}h1{margin:0 0 4px;font-size:18px}.sub{color:var(--muted);font-size:12px}
 .kpis{display:flex;gap:16px;flex-wrap:wrap;padding:16px 24px}
 .kpi{background:var(--card);border:1px solid #262b35;border-radius:10px;padding:12px 16px;min-width:130px}
 .kpi .v{font-size:22px;font-weight:600}.kpi .l{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.04em}
 .grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;padding:0 24px 24px}
 .card{background:var(--card);border:1px solid #262b35;border-radius:10px;padding:16px}
 .card h2{margin:0 0 12px;font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
 .full{grid-column:1/4}.half{grid-column:1/3}
 table{width:100%;border-collapse:collapse;font-size:13px}
 th,td{text-align:left;padding:7px 10px;border-bottom:1px solid #262b35}
 th{color:var(--muted);font-weight:500}td.n{text-align:right;font-variant-numeric:tabular-nums}
 tr.click{cursor:pointer}tr.click:hover{background:#1f2530}
 .path{color:var(--muted);font-size:11px}.pill{display:inline-block;background:#222834;border:1px solid #2c3340;border-radius:20px;padding:1px 8px;font-size:11px;color:#cbd5e1;margin:1px}
 a{color:var(--accent)}#drill{display:none}.muted{color:var(--muted)}
 .tile{display:flex;justify-content:space-between;align-items:center;gap:12px}
</style></head><body>
<header><h1>AI Usage Dashboard</h1><div class="sub" id="sub"></div></header>
<div class="kpis" id="kpis"></div>
<div class="grid">
 <div class="card"><h2>Cost by provider (all CLI tools)</h2><canvas id="provChart" height="200"></canvas></div>
 <div class="card"><h2>Cost by model</h2><canvas id="modelChart" height="200"></canvas></div>
 <div class="card"><h2>GitHub Copilot &middot; Antigravity</h2>
   <div class="tile"><div class="muted" style="font-size:12px">IDE tools report to their vendor, not local logs.</div></div>
   <p style="margin:10px 0 4px"><a href="https://github.com/settings/copilot/usage" target="_blank">Open Copilot usage &rarr;</a></p>
   <p style="margin:4px 0"><a href="https://aistudio.google.com/usage" target="_blank">Open Gemini/Google usage &rarr;</a></p>
   <p class="muted" style="font-size:11px;margin-top:10px">Auto-pull needs a GitHub token with <code>user</code>/billing scope; individual Copilot has limited API.</p>
 </div>
 <div class="card full"><h2>Daily cost trend (all tools)</h2><canvas id="dayChart" height="90"></canvas></div>
 <div class="card full"><h2>Cost by project (Claude Code) &mdash; click a row to drill in</h2>
   <table id="ptbl"><thead><tr><th>Project</th><th class="n">Cost</th><th class="n">Tokens</th><th>Models</th><th>Last</th></tr></thead><tbody></tbody></table></div>
 <div class="card full" id="drill"><h2 id="drillTitle"></h2><div class="path" id="drillPath"></div>
   <div class="grid" style="padding:12px 0 0;grid-template-columns:1fr 1fr">
     <div><h2>By model</h2><canvas id="dModel" height="160"></canvas></div>
     <div><h2>Daily</h2><canvas id="dDay" height="160"></canvas></div>
   </div>
   <h2 style="margin-top:12px">Sessions</h2>
   <table id="dSess"><thead><tr><th>Session</th><th class="n">Cost</th><th class="n">Tokens</th><th>Top model</th><th>Last</th></tr></thead><tbody></tbody></table>
 </div>
</div>
<footer style="color:var(--muted);font-size:11px;padding:0 24px 24px">Cross-tool totals from <code>ccusage</code>; per-project from <code>~/.claude/projects/</code> (Claude Code). Cost = API-equivalent value, not your subscription bill. <code>&lt;synthetic&gt;</code> excluded. Refresh: re-run <code>usage-dashboard.ps1</code>.</footer>
<script>
const DATA = /*__DATA__*/{};
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmtTok=n=>n>=1e6?(n/1e6).toFixed(2)+'M':n>=1e3?(n/1e3).toFixed(1)+'K':n;
const pal=['#4ea1ff','#ff7a59','#43c59e','#f7c948','#a78bfa','#f471b5','#34d399','#fb923c','#60a5fa','#c084fc'];
$('#sub').textContent='Generated '+DATA.generated+' · '+DATA.toolCount+' tools · '+DATA.projectCount+' Claude projects';
$('#kpis').innerHTML=[['Total cost (API-equiv)','$'+DATA.ccTotal.toLocaleString()],['Total tokens',fmtTok(DATA.ccTokens)],['CLI tools',DATA.toolCount],['Claude projects',DATA.projectCount]]
 .map(k=>'<div class="kpi"><div class="v">'+esc(k[1])+'</div><div class="l">'+esc(k[0])+'</div></div>').join('');
const doughnut=(el,rows,kl,vl)=>window.Chart&&new Chart($(el),{type:'doughnut',data:{labels:rows.map(r=>r[kl]),datasets:[{data:rows.map(r=>r[vl]),backgroundColor:pal}]},options:{plugins:{legend:{position:'right',labels:{color:'#e6e6e6',boxWidth:12}}}}});
const barH=(el,rows,kl,vl)=>window.Chart&&new Chart($(el),{type:'bar',data:{labels:rows.map(r=>r[kl]),datasets:[{data:rows.map(r=>r[vl]),backgroundColor:'#4ea1ff'}]},options:{indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#9aa4b2'}},y:{ticks:{color:'#e6e6e6'}}}}});
const line=(el,rows)=>window.Chart&&new Chart($(el),{type:'line',data:{labels:rows.map(d=>d.day),datasets:[{data:rows.map(d=>d.cost),borderColor:'#43c59e',backgroundColor:'rgba(67,197,158,.15)',fill:true,tension:.25,pointRadius:0}]},options:{plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#9aa4b2',maxTicksLimit:12}},y:{ticks:{color:'#9aa4b2'}}}}});
doughnut('#provChart',DATA.byProvider,'label','cost');
barH('#modelChart',DATA.byModel,'label','cost');
line('#dayChart',DATA.byDay);
$('#ptbl tbody').innerHTML=DATA.projects.map((p,i)=>'<tr class="click" data-i="'+i+'"><td>'+esc(p.name)+'<div class="path">'+esc(p.path)+'</div></td><td class="n">$'+p.cost.toFixed(2)+'</td><td class="n">'+fmtTok(p.tokens)+'</td><td>'+p.byModel.map(m=>'<span class="pill">'+esc(m.label)+'</span>').join('')+'</td><td>'+esc(p.last)+'</td></tr>').join('');
let dm,dd;
function drill(i){const p=DATA.projects[i];if(!p)return;$('#drill').style.display='block';$('#drillTitle').textContent='Drill-down: '+p.name+'  ($'+p.cost.toFixed(2)+' · '+fmtTok(p.tokens)+' tokens)';$('#drillPath').textContent=p.path;
 if(dm)dm.destroy();if(dd)dd.destroy();if(window.Chart){dm=barH('#dModel',p.byModel,'label','cost');dd=line('#dDay',p.byDay);}
 $('#dSess tbody').innerHTML=p.sessions.map(s=>'<tr><td>'+esc(s.id)+'</td><td class="n">$'+s.cost.toFixed(2)+'</td><td class="n">'+fmtTok(s.tokens)+'</td><td>'+esc(s.model)+'</td><td>'+esc(s.last)+'</td></tr>').join('');
 $('#drill').scrollIntoView({behavior:'smooth'});}
document.querySelectorAll('#ptbl tbody tr').forEach(tr=>tr.onclick=()=>drill(+tr.dataset.i));
if(DATA.projects.length)drill(0);
</script></body></html>
'@
$html = $html.Replace('/*__DATA__*/{}', $data)
Set-Content -Path $outHtml -Value $html -Encoding UTF8
Write-Host "Wrote $outHtml  (tools=$(($tools.Keys).Count), projects=$($projects.Count), ccusage total=`$$([math]::Round($ccTotal,2)))"
if ($Open) { Start-Process $outHtml }
