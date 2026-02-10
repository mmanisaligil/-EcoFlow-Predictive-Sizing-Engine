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
  <title>EcoFlow Predictive Sizing Engine</title>
  <style>
    :root{--bg:#f5f7fb;--card:rgba(255,255,255,.65);--text:#122039;--muted:#5f6b85;--accent:#007aff;--border:rgba(255,255,255,.55)}
    @media (prefers-color-scheme: dark){:root{--bg:#0d111a;--card:rgba(24,30,44,.6);--text:#edf0fa;--muted:#9ba5c0;--accent:#4ba3ff;--border:rgba(255,255,255,.15)}}
    *{box-sizing:border-box} body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:radial-gradient(circle at 20% 10%, rgba(88,141,255,.26), transparent 45%),var(--bg);color:var(--text)}
    .shell{max-width:1100px;margin:24px auto;padding:0 16px;display:grid;gap:16px}
    .card{background:var(--card);border:1px solid var(--border);backdrop-filter:blur(16px) saturate(130%);-webkit-backdrop-filter:blur(16px) saturate(130%);border-radius:20px;padding:16px;box-shadow:0 10px 40px rgba(0,0,0,.12)}
    h1,h2{margin:.2rem 0} .muted{color:var(--muted)}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
    label{display:grid;gap:4px;font-size:12px;color:var(--muted)}
    input,select,button{border:1px solid var(--border);border-radius:12px;padding:10px;background:rgba(255,255,255,.65);color:var(--text)}
    @media (prefers-color-scheme: dark){input,select,button{background:rgba(24,30,44,.8)}}
    button{cursor:pointer;font-weight:600}
    pre{white-space:pre-wrap;word-break:break-word;font-size:12px;max-height:320px;overflow:auto}
    .row{display:flex;gap:10px;flex-wrap:wrap}
  </style>
</head>
<body>
  <main class=\"shell\">
    <section class=\"card\">
      <h1>EcoFlow Sizing Dashboard</h1>
      <p class=\"muted\">Single-container DigitalOcean UI for deterministic sizing. Use <code>/docs</code> for API explorer.</p>
    </section>

    <section class=\"card\">
      <h2>Manual Input</h2>
      <div class=\"grid\">
        <label>Family
          <select id=\"system_family\"><option value=\"powerocean\">powerocean</option><option value=\"stream\">stream</option></select>
        </label>
        <label>City <input id=\"city\" value=\"Adana\" /></label>
        <label>PV (kWp) <input id=\"pv_kwp\" type=\"number\" value=\"6\" step=\"0.1\" /></label>
        <label>Tariff TL/kWh <input id=\"tariff\" type=\"number\" value=\"3.2\" step=\"0.01\" /></label>
        <label>Daily kWh <input id=\"daily_kwh\" type=\"number\" value=\"24\" step=\"0.1\" /></label>
        <label>Avg kW (optional) <input id=\"avg_kw\" type=\"number\" /></label>
        <label>Peak kW (optional) <input id=\"peak_kw\" type=\"number\" /></label>
        <label>PowerOcean Phase
          <select id=\"phase\"><option value=\"1P\">1P</option><option value=\"3P\">3P</option></select>
        </label>
        <label>PowerOcean 3P Class
          <select id=\"cls\"><option value=\"\">(none)</option><option value=\"3P\">3P</option><option value=\"3P_PLUS\">3P_PLUS</option></select>
        </label>
      </div>
      <div class=\"row\" style=\"margin-top:10px\">
        <button onclick=\"runAnalyze()\">Run Analyze</button>
        <button onclick=\"downloadXlsx()\">Export XLSX</button>
      </div>
    </section>

    <section class=\"card\">
      <h2>Result</h2>
      <pre id=\"result\" class=\"muted\">No analysis run yet.</pre>
    </section>
  </main>
  <script>
    function val(id){return document.getElementById(id).value}
    function num(id){const v=val(id); return v===''?null:Number(v)}
    function payload(){
      const family = val('system_family');
      const phase = family==='powerocean'?val('phase'):null;
      let cls = family==='powerocean' && phase==='3P' ? val('cls') : null;
      if (cls === '') cls = null;
      return {
        system_family: family,
        city: val('city'),
        pv_kwp: Number(val('pv_kwp')),
        tariff_tl_per_kwh: Number(val('tariff')),
        daily_kwh: Number(val('daily_kwh')),
        avg_kw: num('avg_kw'),
        peak_kw: num('peak_kw'),
        powerocean_phase: phase,
        powerocean_3p_class: cls,
        expert_loads: []
      };
    }
    async function runAnalyze(){
      const out = document.getElementById('result'); out.textContent='Running...';
      try{
        const r = await fetch('/analyze',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload())});
        const j = await r.json();
        out.textContent = JSON.stringify(j, null, 2);
      }catch(e){ out.textContent='Error: '+e; }
    }
    async function downloadXlsx(){
      const r = await fetch('/export/xlsx',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload())});
      if(!r.ok){
        const j = await r.json();
        document.getElementById('result').textContent = JSON.stringify(j,null,2);
        return;
      }
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href=url; a.download='ecoflow_analysis.xlsx'; a.click();
      URL.revokeObjectURL(url);
    }
  </script>
</body>
</html>"""
