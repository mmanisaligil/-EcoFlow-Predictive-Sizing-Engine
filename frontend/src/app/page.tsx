'use client';

import { useEffect, useMemo, useState } from 'react';
import { ChartBars } from '@/components/ChartBars';
import { GlassCard } from '@/components/Glass';
import { KpiRow } from '@/components/KpiRow';

type ScenarioId = 'S1' | 'S2' | 'S3';
type HoursMode = 'low' | 'medium' | 'high';

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const scenarioNames: Record<ScenarioId, string> = { S1: '2 days outage', S2: '1 day outage', S3: 'Night-only' };

export default function HomePage() {
  const [payload, setPayload] = useState<any>({
    system_family: 'powerocean', city: 'Adana', pv_kwp: 6, tariff_tl_per_kwh: 3.2, daily_kwh: 24, avg_kw: null, peak_kw: null,
    powerocean_phase: '1P', powerocean_3p_class: null,
    selected_scenario_id: 'S3', expert_mode: false, expert_hours_mode: 'medium', expert_loads: []
  });
  const [metadata, setMetadata] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [technicalOpen, setTechnicalOpen] = useState(false);
  const [technicalTab, setTechnicalTab] = useState<'summary'|'sizing'|'bom'|'economics'|'raw'>('summary');
  const [search, setSearch] = useState('');

  useEffect(() => { fetch(`${API}/metadata`).then(r=>r.json()).then(setMetadata).catch(()=>null); }, []);

  async function runAnalysis() {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API}/analyze`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Analyze failed');
      setAnalysis(data);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }

  async function downloadXlsx() {
    const res = await fetch(`${API}/export/xlsx`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) { setError('Export failed'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'ecoflow_analysis.xlsx'; a.click(); URL.revokeObjectURL(url);
  }

  const selectedScenario = analysis?.sizing?.selected_scenario_id ?? payload.selected_scenario_id;
  const kpis = useMemo(() => analysis ? [
    { label: 'Coverage %', value: `${(analysis.performance.coverage_ratio_typical * 100).toFixed(1)}%` },
    { label: 'Annual Savings TL', value: `${analysis.economics.selected.annual_savings_try.toLocaleString()} TL` },
    { label: 'Simple Payback years', value: `${analysis.economics.selected.payback_simple_years ?? '-'} yrs` },
    { label: 'CO2 saved kg/y', value: `${analysis.co2.co2_saved_kg_per_year.toLocaleString()} kg/y` }
  ] : [], [analysis]);

  const templateGroups = metadata?.expert_load_templates_grouped ?? {};
  const filteredGroups = Object.fromEntries(Object.entries(templateGroups).map(([group, items]: any) => [
    group,
    (items as string[]).filter((item) => item.toLowerCase().includes(search.toLowerCase()))
  ]));

  return (
    <main className="shell">
      <header className="hero glass"><h1>EcoFlow Predictive Sizing</h1><button className="button" onClick={runAnalysis}>{loading ? 'Calculating…' : 'Run Analysis'}</button></header>

      <GlassCard title="Inputs">
        <div className="grid">
          <label>Family<select value={payload.system_family} onChange={(e)=>setPayload({...payload, system_family: e.target.value})}><option value="powerocean">PowerOcean</option><option value="stream">STREAM</option></select></label>
          <label>City<input value={payload.city} onChange={(e)=>setPayload({...payload, city: e.target.value})} list="cities"/><datalist id="cities">{(metadata?.cities ?? []).map((c:string)=><option key={c} value={c}/>)}</datalist></label>
          <label>PV (kWp)<input type="number" value={payload.pv_kwp} onChange={(e)=>setPayload({...payload, pv_kwp: Number(e.target.value)})} /></label>
          <label>Tariff (TL/kWh)<input type="number" value={payload.tariff_tl_per_kwh} onChange={(e)=>setPayload({...payload, tariff_tl_per_kwh: Number(e.target.value)})} /></label>
          <label>Daily kWh<input type="number" value={payload.daily_kwh} onChange={(e)=>setPayload({...payload, daily_kwh: Number(e.target.value)})} /></label>
          <label>Peak kW<input type="number" value={payload.peak_kw ?? ''} onChange={(e)=>setPayload({...payload, peak_kw: e.target.value ? Number(e.target.value) : null})} /></label>
          {payload.system_family === 'powerocean' && <label>Phase<select value={payload.powerocean_phase ?? '1P'} onChange={(e)=>setPayload({...payload,powerocean_phase:e.target.value,powerocean_3p_class:null})}><option value="1P">1P</option><option value="3P">3P</option></select></label>}
          {payload.system_family === 'powerocean' && payload.powerocean_phase === '3P' && <label>3P Class<select value={payload.powerocean_3p_class ?? '3P'} onChange={(e)=>setPayload({...payload,powerocean_3p_class:e.target.value})}><option value="3P">3P</option><option value="3P_PLUS">3P_PLUS</option></select></label>}
        </div>
        <div className="segment">
          {(['S1','S2','S3'] as ScenarioId[]).map((sid)=> <button key={sid} className={payload.selected_scenario_id===sid?'active':''} onClick={()=>setPayload({...payload, selected_scenario_id: sid})}>{sid} · {scenarioNames[sid]}</button>)}
        </div>
        <div className="expertToggle"><label><input type="checkbox" checked={payload.expert_mode} onChange={(e)=>setPayload({...payload, expert_mode: e.target.checked, expert_loads: e.target.checked ? payload.expert_loads : []})}/> Expert Mode</label></div>

        {payload.expert_mode && <div className="expertBox">
          <div className="segment">{(['low','medium','high'] as HoursMode[]).map((mode)=><button key={mode} className={payload.expert_hours_mode===mode?'active':''} onClick={()=>setPayload({...payload, expert_hours_mode: mode})}>{mode}</button>)}</div>
          <input placeholder="Search templates" value={search} onChange={(e)=>setSearch(e.target.value)} />
          {Object.entries(filteredGroups).map(([group, items]: any)=><div key={group}><h4>{group}</h4>{(items as string[]).map((tpl)=><label key={tpl} className="checkbox"><input type="checkbox" checked={payload.expert_loads.includes(tpl)} onChange={(e)=>setPayload({...payload, expert_loads: e.target.checked ? [...payload.expert_loads, tpl] : payload.expert_loads.filter((x:string)=>x!==tpl)})}/>{tpl}</label>)}</div>)}
        </div>}
      </GlassCard>

      {error && <GlassCard><p className="error">{error}</p></GlassCard>}
      {analysis && <>
        <KpiRow items={kpis} />
        <GlassCard title={`Selected Scenario: ${selectedScenario} · ${scenarioNames[selectedScenario as ScenarioId]}`}>
          <div className="comparison">
            <table><thead><tr><th>Scenario</th><th>Capex</th><th>Annual Savings</th><th>Payback</th></tr></thead><tbody>{(['S1','S2','S3'] as ScenarioId[]).map((sid)=><tr key={sid}><td>{sid}</td><td>{analysis.economics.scenarios[sid].capex_try.toLocaleString()} TL</td><td>{analysis.economics.scenarios[sid].annual_savings_try.toLocaleString()} TL</td><td>{analysis.economics.scenarios[sid].payback_simple_years ?? '-'} y</td></tr>)}</tbody></table>
          </div>
        </GlassCard>
        <div className="twoCol">
          <GlassCard title="Load vs Solar"><ChartBars load={analysis.profiles.consumption.daily_kwh_band[1]} solar={analysis.profiles.solar.daily_avg_kwh} offset={analysis.performance.offset_kwh_per_day_typical} /></GlassCard>
          <GlassCard title="BOM (Selected)"><table><tbody>{analysis.bom.selected.items.map((item:any)=><tr key={item.id}><td>{item.name}</td><td>{item.qty}</td><td>{item.unit_price_try.toLocaleString()} TL</td></tr>)}</tbody></table><p>Total: {analysis.bom.selected.capex_try.toLocaleString()} TL</p></GlassCard>
        </div>
        <GlassCard title="Actions"><button className="button" onClick={downloadXlsx}>Download XLSX</button><button className="button" onClick={()=>setTechnicalOpen(true)}>View Technical Details</button></GlassCard>
      </>}

      {technicalOpen && analysis && <div className="modalWrap" onClick={()=>setTechnicalOpen(false)}><div className="modal glass" onClick={(e)=>e.stopPropagation()}>
        <div className="tabs">{(['summary','sizing','bom','economics','raw'] as const).map((tab)=><button key={tab} className={technicalTab===tab?'active':''} onClick={()=>setTechnicalTab(tab)}>{tab}</button>)}</div>
        {technicalTab==='summary' && <pre>{JSON.stringify({inputs: analysis.inputs, selected_scenario: analysis.sizing.selected_scenario_id, assumptions: analysis.assumptions}, null, 2)}</pre>}
        {technicalTab==='sizing' && <pre>{JSON.stringify(analysis.sizing, null, 2)}</pre>}
        {technicalTab==='bom' && <pre>{JSON.stringify(analysis.bom, null, 2)}</pre>}
        {technicalTab==='economics' && <pre>{JSON.stringify(analysis.economics, null, 2)}</pre>}
        {technicalTab==='raw' && <div><button className="button" onClick={()=>navigator.clipboard.writeText(JSON.stringify(analysis, null, 2))}>Copy JSON</button><a className="button" href={`data:application/json;charset=utf-8,${encodeURIComponent(JSON.stringify(analysis, null, 2))}`} download="analysis.json">Download JSON</a><details><summary>Raw JSON</summary><pre>{JSON.stringify(analysis, null, 2)}</pre></details></div>}
      </div></div>}
    </main>
  );
}
