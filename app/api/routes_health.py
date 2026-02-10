from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter(tags=["health"])


@router.get("/")
def root(request: Request):
    """Serve browser UI for HTML clients and JSON status for API clients."""
    accept = (request.headers.get("accept") or "").lower()
    if "text/html" in accept:
        return HTMLResponse(_html_app())

    return JSONResponse(
        {
            "status": "ok",
            "service": "ecoflow-sizing-v13",
            "health": "/health",
            "metadata": "/metadata",
            "analyze": "/analyze",
            "export_xlsx": "/export/xlsx",
            "docs": "/docs",
        }
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _html_app() -> str:
    return """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Green Energy Predictive Advisor</title>
  <style>
    :root{--bg:#f5f7fb;--card:rgba(255,255,255,.7);--text:#122039;--muted:#5f6b85;--accent:#0a84ff;--border:rgba(255,255,255,.55)}
    @media (prefers-color-scheme: dark){:root{--bg:#0d111a;--card:rgba(24,30,44,.62);--text:#edf0fa;--muted:#9ba5c0;--accent:#4ba3ff;--border:rgba(255,255,255,.15)}}
    *{box-sizing:border-box} body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 20% 10%, rgba(88,141,255,.26), transparent 45%),var(--bg);color:var(--text)}
    .shell{max-width:1200px;margin:20px auto;padding:0 16px;display:grid;gap:14px}
    .card{background:var(--card);border:1px solid var(--border);backdrop-filter:blur(16px) saturate(130%);-webkit-backdrop-filter:blur(16px) saturate(130%);border-radius:18px;padding:14px;box-shadow:0 10px 36px rgba(0,0,0,.12)}
    .hero{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
    h1,h2,h3{margin:.1rem 0}.muted{color:var(--muted)}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
    label{display:grid;gap:4px;font-size:12px;color:var(--muted)}
    input,select,button{border:1px solid var(--border);border-radius:10px;padding:10px;background:rgba(255,255,255,.75);color:var(--text)}
    @media (prefers-color-scheme: dark){input,select,button{background:rgba(24,30,44,.86)}}
    button{cursor:pointer;font-weight:600}
    button.primary{background:linear-gradient(135deg,var(--accent),#63b1ff);color:#fff;border:none}
    .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}
    .kpi{padding:10px;border-radius:12px;border:1px solid var(--border);background:rgba(255,255,255,.25)}
    .kpi b{font-size:24px}
    .hidden{display:none}
    pre{white-space:pre-wrap;word-break:break-word;font-size:12px;max-height:320px;overflow:auto;margin:0}
    .hint{font-size:12px;color:var(--muted)}
  </style>
</head>
<body>
  <main class=\"shell\">
    <section class=\"card hero\">
      <div>
        <h1>Green Energy Predictive Advisor</h1>
        <div class=\"muted\">B2B-ready deterministic sizing for EcoFlow PowerOcean / STREAM</div>
      </div>
      <div class=\"hint\">API Docs: <a href=\"/docs\">/docs</a></div>
    </section>

    <section class=\"card\">
      <h2>Inputs</h2>
      <div class=\"grid\">
        <label>System Family
          <select id=\"system_family\"><option value=\"powerocean\">powerocean</option><option value=\"stream\">stream</option></select>
        </label>
        <label>City
          <select id=\"city\"></select>
        </label>
        <label>PV (kWp) <input id=\"pv_kwp\" type=\"number\" value=\"6\" step=\"0.1\" /></label>
        <label>Tariff TL/kWh <input id=\"tariff\" type=\"number\" value=\"3.2\" step=\"0.01\" /></label>
        <label>Daily kWh <input id=\"daily_kwh\" type=\"number\" value=\"24\" step=\"0.1\" /></label>
        <label>Avg kW (optional) <input id=\"avg_kw\" type=\"number\" /></label>
        <label>Peak kW (optional) <input id=\"peak_kw\" type=\"number\" /></label>
        <label>PowerOcean Phase
          <select id=\"phase\"><option value=\"1P\">1P</option><option value=\"3P\">3P</option></select>
        </label>
        <label>3P Class
          <select id=\"cls\"><option value=\"\">(none)</option><option value=\"3P\">3P</option><option value=\"3P_PLUS\">3P_PLUS</option></select>
        </label>
      </div>

      <div style=\"margin-top:10px\">
        <label>Expert Load Templates (multi-select)
          <select id=\"expert_loads\" multiple size=\"8\"></select>
        </label>
      </div>
      <div class=\"hint\">Use Ctrl/Cmd click for multiple load packs. Manual values remain dominant and load packs are aggregated as hints.</div>

      <div style=\"margin-top:12px;display:flex;gap:10px;flex-wrap:wrap\">
        <button class=\"primary\" onclick=\"runAnalyze()\">Calculate</button>
        <button onclick=\"resetForm()\">Reset</button>
      </div>
    </section>

    <section class=\"card\" id=\"resultCard\">
      <h2>Results</h2>
      <div id=\"resultState\" class=\"muted\">Run calculation to see B2B analysis summary.</div>

      <div id=\"kpiPanel\" class=\"kpis hidden\">
        <div class=\"kpi\"><div class=\"muted\">Coverage</div><b id=\"kpiCoverage\">-</b></div>
        <div class=\"kpi\"><div class=\"muted\">Annual Savings</div><b id=\"kpiSavings\">-</b></div>
        <div class=\"kpi\"><div class=\"muted\">Simple Payback</div><b id=\"kpiPayback\">-</b></div>
        <div class=\"kpi\"><div class=\"muted\">CO₂ Saved</div><b id=\"kpiCo2\">-</b></div>
      </div>

      <h3 style=\"margin-top:12px\">Technical JSON</h3>
      <pre id=\"resultJson\" class=\"muted\">No analysis yet.</pre>

      <div id=\"exportSection\" class=\"hidden\" style=\"margin-top:12px\">
        <button onclick=\"downloadXlsx()\">Export XLSX</button>
      </div>
    </section>
  </main>

  <script>
    let latestAnalysis = null;

    function numOrNull(id){ const v=document.getElementById(id).value; return v==='' ? null : Number(v); }
    function selectedOptions(id){ return Array.from(document.getElementById(id).selectedOptions).map(o=>o.value); }
    function asTry(v){ return (v ?? 0).toLocaleString('tr-TR'); }

    async function loadMetadata(){
      const citySel = document.getElementById('city');
      const expertSel = document.getElementById('expert_loads');
      citySel.innerHTML = '<option>Loading...</option>';
      expertSel.innerHTML = '';

      const res = await fetch('/metadata');
      const meta = await res.json();

      citySel.innerHTML = '';
      for(const c of meta.cities){
        const o = document.createElement('option'); o.value = c; o.textContent = c; citySel.appendChild(o);
      }
      citySel.value = 'Adana';

      for(const id of meta.expert_load_templates){
        const o = document.createElement('option'); o.value = id; o.textContent = id; expertSel.appendChild(o);
      }
    }

    function buildPayload(){
      const family = document.getElementById('system_family').value;
      const phase = family === 'powerocean' ? document.getElementById('phase').value : null;
      let cls = family === 'powerocean' && phase === '3P' ? document.getElementById('cls').value : null;
      if (cls === '') cls = null;

      return {
        system_family: family,
        city: document.getElementById('city').value,
        pv_kwp: Number(document.getElementById('pv_kwp').value),
        tariff_tl_per_kwh: Number(document.getElementById('tariff').value),
        daily_kwh: Number(document.getElementById('daily_kwh').value),
        avg_kw: numOrNull('avg_kw'),
        peak_kw: numOrNull('peak_kw'),
        powerocean_phase: phase,
        powerocean_3p_class: cls,
        expert_loads: selectedOptions('expert_loads'),
      };
    }

    function showAnalysis(a){
      latestAnalysis = a;
      document.getElementById('resultState').textContent = `Confidence: ${a.confidence.peak_kw} | Warnings: ${a.warnings.length}`;
      document.getElementById('kpiCoverage').textContent = `${(a.performance.coverage_ratio_typical*100).toFixed(1)}%`;
      document.getElementById('kpiSavings').textContent = `${asTry(a.economics.annual_savings_try)} TL`;
      document.getElementById('kpiPayback').textContent = `${a.economics.payback_simple_years ?? '-'} yr`;
      document.getElementById('kpiCo2').textContent = `${asTry(a.co2.co2_saved_kg_per_year)} kg/y`;
      document.getElementById('kpiPanel').classList.remove('hidden');
      document.getElementById('resultJson').textContent = JSON.stringify(a, null, 2);
      document.getElementById('exportSection').classList.remove('hidden');
    }

    function showError(e){
      document.getElementById('resultState').textContent = 'Error';
      document.getElementById('resultJson').textContent = String(e);
      document.getElementById('kpiPanel').classList.add('hidden');
      document.getElementById('exportSection').classList.add('hidden');
    }

    async function runAnalyze(){
      document.getElementById('resultState').textContent = 'Calculating...';
      try {
        const res = await fetch('/analyze', { method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(buildPayload()) });
        const data = await res.json();
        if(!res.ok){ throw new Error(JSON.stringify(data)); }
        showAnalysis(data);
      } catch(err){
        showError(err);
      }
    }

    async function downloadXlsx(){
      if(!latestAnalysis){ return; }
      const res = await fetch('/export/xlsx', { method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(buildPayload()) });
      if(!res.ok){
        const j = await res.json();
        showError(JSON.stringify(j, null, 2));
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = 'ecoflow_analysis.xlsx'; a.click();
      URL.revokeObjectURL(url);
    }

    function resetForm(){
      document.getElementById('system_family').value = 'powerocean';
      document.getElementById('pv_kwp').value = '6';
      document.getElementById('tariff').value = '3.2';
      document.getElementById('daily_kwh').value = '24';
      document.getElementById('avg_kw').value = '';
      document.getElementById('peak_kw').value = '';
      document.getElementById('phase').value = '1P';
      document.getElementById('cls').value = '';
      Array.from(document.getElementById('expert_loads').options).forEach(o => { o.selected = false; });
      latestAnalysis = null;
      document.getElementById('resultState').textContent = 'Run calculation to see B2B analysis summary.';
      document.getElementById('resultJson').textContent = 'No analysis yet.';
      document.getElementById('kpiPanel').classList.add('hidden');
      document.getElementById('exportSection').classList.add('hidden');
    }

    loadMetadata().catch(showError);
  </script>
</body>
</html>"""
