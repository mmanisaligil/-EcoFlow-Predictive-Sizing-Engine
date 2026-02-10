import type { ReactNode } from 'react';

export function GlassCard({ title, children }: { title?: string; children: ReactNode }) {
  return (
    <section className="glass" style={{ borderRadius: 'var(--radius-lg)', padding: 'var(--space-4)' }}>
      {title ? <h3 style={{ marginTop: 0 }}>{title}</h3> : null}
      {children}
    </section>
  );
}

export function Pill({ label }: { label: string }) {
  return (
    <span
      className="glass"
      style={{ borderRadius: 999, padding: '6px 12px', display: 'inline-flex', fontSize: 12, color: 'var(--muted)' }}
    >
      {label}
    </span>
  );
}
