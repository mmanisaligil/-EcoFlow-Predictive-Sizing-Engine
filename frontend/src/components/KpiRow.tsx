export function KpiRow({ items }: { items: Array<{ label: string; value: string }> }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(170px,1fr))', gap: 'var(--space-3)' }}>
      {items.map((item) => (
        <div key={item.label} className="glass" style={{ borderRadius: 'var(--radius-md)', padding: 'var(--space-3)' }}>
          <div style={{ color: 'var(--muted)', fontSize: 13 }}>{item.label}</div>
          <strong style={{ fontSize: 24 }}>{item.value}</strong>
        </div>
      ))}
    </div>
  );
}
