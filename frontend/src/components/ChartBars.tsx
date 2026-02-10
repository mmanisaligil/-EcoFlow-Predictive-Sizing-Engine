export function ChartBars({ load, solar, offset }: { load: number; solar: number; offset: number }) {
  const max = Math.max(load, solar, offset, 1);
  const bar = (value: number) => `${(value / max) * 100}%`;
  return (
    <div style={{ display: 'grid', gap: 'var(--space-2)' }}>
      {[['Load', load], ['Solar', solar], ['Offset', offset]].map(([name, value]) => (
        <div key={String(name)}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--muted)' }}>
            <span>{name}</span><span>{Number(value).toFixed(2)} kWh/day</span>
          </div>
          <div style={{ height: 12, borderRadius: 999, background: 'rgba(127,127,127,0.2)', overflow: 'hidden' }}>
            <div style={{ width: bar(Number(value)), height: '100%', background: 'linear-gradient(90deg, #4ba3ff, #72f0ff)' }} />
          </div>
        </div>
      ))}
    </div>
  );
}
