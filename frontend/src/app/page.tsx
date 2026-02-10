'use client';

import { type CSSProperties, type ReactNode, useMemo, useState } from 'react';
import { ChartBars } from '@/components/ChartBars';
import { GlassCard, Pill } from '@/components/Glass';
import { KpiRow } from '@/components/KpiRow';

type AnalyzePayload = {
  system_family: 'powerocean' | 'stream';
  city: string;
  pv_kwp: number;
  tariff_tl_per_kwh: number;
  daily_kwh: number;
  avg_kw: number | null;
  peak_kw: number | null;
  powerocean_phase: '1P' | '3P' | null;
  powerocean_3p_class: '3P' | '3P_PLUS' | null;
  expert_loads: string[];
};

const API = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export default function HomePage() {
  const [payload, setPayload] = useState<AnalyzePayload>({
    system_family: 'powerocean', city: 'Adana', pv_kwp: 6, tariff_tl_per_kwh: 3.2, daily_kwh: 24, avg_kw: null, peak_kw: null,
    powerocean_phase: '1P', powerocean_3p_class: null, expert_loads: []
  });
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const supports3PClass = payload.system_family === 'powerocean' && payload.powerocean_phase === '3P';

  async function runAnalysis() {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API}/analyze`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Analyze failed');
      setAnalysis(data);
    } catch (e: any) {
      setError(e.message);
    } finally { setLoading(false); }
  }



  async function downloadXlsx() {
    const res = await fetch(`${API}/export/xlsx`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) { setError('Export failed'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ecoflow_analysis.xlsx';
    a.click();
    URL.revokeObjectURL(url);
  }

  const kpis = useMemo(() => analysis ? [
    { label: 'Coverage', value: `${(analysis.performance.coverage_ratio_typical * 100).toFixed(1)}%` },
    { label: 'Annual Savings', value: `${analysis.economics.annual_savings_try.toLocaleString()} TL` },
    { label: 'Simple Payback', value: `${analysis.economics.payback_simple_years ?? '-'} yrs` },
    { label: 'CO₂ Saved', value: `${analysis.co2.co2_saved_kg_per_year.toLocaleString()} kg/yr` }
  ] : [], [analysis]);

  return (
    <main className="page">
      <aside className="glass" style={{ margin: 16, borderRadius: 24, padding: 16, position: 'sticky', top: 16, height: 'calc(100vh - 32px)' }}>
        <h2 style={{ marginTop: 0 }}>EcoFlow</h2>
        <p style={{ color: 'var(--muted)' }}>Predictive Sizing Engine</p>
        <div style={{ display: 'grid', gap: 10 }}>
          <Pill label="Dashboard" /><Pill label="Input Studio" /><Pill label="Analysis" /><Pill label="Export" />
        </div>
      </aside>
      <section style={{ padding: 16, display: 'grid', gap: 16 }}>
        <header className="glass" style={{ borderRadius: 24, padding: 16, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h1 style={{ margin: 0 }}>Sizing Dashboard</h1>
            <small style={{ color: 'var(--muted)' }}>Liquid Glass interface tuned for calm, auditable sizing flows.</small>
          </div>
          <button onClick={runAnalysis} disabled={loading} style={buttonStyle}>{loading ? 'Calculating…' : 'Run Analysis'}</button>
        </header>

        <GlassCard title="Manual + Expert Input Mode">
          <div style={gridStyle}>
            <Field label="Family"><select value={payload.system_family} onChange={(e)=>setPayload({...payload,system_family:e.target.value as any})}><option value="powerocean">PowerOcean</option><option value="stream">STREAM</option></select></Field>
            <Field label="City"><input value={payload.city} onChange={(e)=>setPayload({...payload,city:e.target.value})} /></Field>
            <Field label="PV (kWp)"><input type="number" value={payload.pv_kwp} onChange={(e)=>setPayload({...payload,pv_kwp:Number(e.target.value)})} /></Field>
            <Field label="Tariff (TL/kWh)"><input type="number" value={payload.tariff_tl_per_kwh} onChange={(e)=>setPayload({...payload,tariff_tl_per_kwh:Number(e.target.value)})} /></Field>
            <Field label="Daily kWh"><input type="number" value={payload.daily_kwh} onChange={(e)=>setPayload({...payload,daily_kwh:Number(e.target.value)})} /></Field>
            <Field label="Avg kW"><input type="number" value={payload.avg_kw ?? ''} onChange={(e)=>setPayload({...payload,avg_kw:e.target.value?Number(e.target.value):null})} /></Field>
            <Field label="Peak kW"><input type="number" value={payload.peak_kw ?? ''} onChange={(e)=>setPayload({...payload,peak_kw:e.target.value?Number(e.target.value):null})} /></Field>
            {payload.system_family === 'powerocean' ? <Field label="Phase"><select value={payload.powerocean_phase ?? '1P'} onChange={(e)=>setPayload({...payload,powerocean_phase:e.target.value as any,powerocean_3p_class:null})}><option value="1P">1P</option><option value="3P">3P</option></select></Field> : null}
            {supports3PClass ? <Field label="3P Class"><select value={payload.powerocean_3p_class ?? '3P'} onChange={(e)=>setPayload({...payload,powerocean_3p_class:e.target.value as any})}><option value="3P">3P</option><option value="3P_PLUS">3P_PLUS</option></select></Field> : null}
          </div>
          <p style={{ color: 'var(--muted)', marginBottom: 0 }}>Inline validation is provided by backend schema and deterministic engine constraints.</p>
        </GlassCard>

        {error ? <GlassCard><p style={{ color: '#ff4d4f', margin: 0 }}>{error}</p></GlassCard> : null}

        {analysis ? <>
          <KpiRow items={kpis} />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <GlassCard title="Load vs Solar KPI View">
              <ChartBars load={analysis.profiles.consumption.daily_kwh_band[1]} solar={analysis.profiles.solar.daily_avg_kwh} offset={analysis.performance.offset_kwh_per_day_typical} />
            </GlassCard>
            <GlassCard title="System Recommendation Cards">
              {analysis.sizing.scenarios.map((s: any)=> <div key={s.id} className="glass" style={{ padding: 12, borderRadius: 14, marginBottom: 10 }}>
                <strong>{s.id} · {s.name}</strong>
                <div style={{ fontSize: 13, color: 'var(--muted)' }}>{s.battery_nominal_kwh_required} kWh nominal • {s.feasible ? 'Feasible' : 'Infeasible'}</div>
              </div>)}
            </GlassCard>
          </div>
          <GlassCard title="Export / Download">
            <button onClick={downloadXlsx} style={buttonStyle}>Download XLSX</button>
          </GlassCard>
        </> : null}
      </section>
    </main>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return <label style={{ display: 'grid', gap: 6, fontSize: 13, color: 'var(--muted)' }}>{label}<div>{children}</div></label>;
}

const gridStyle: CSSProperties = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 12 };
const buttonStyle: CSSProperties = { border: '1px solid var(--border)', borderRadius: 14, padding: '10px 14px', background: 'var(--surface-strong)', color: 'var(--text)', cursor: 'pointer' };
