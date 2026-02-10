import { GlassCard, Pill } from '@/components/Glass';
import { KpiRow } from '@/components/KpiRow';

export default function ShowcasePage() {
  return (
    <main style={{ padding: 24, display: 'grid', gap: 16 }}>
      <GlassCard title="Glass Primitives">
        <div style={{ display: 'flex', gap: 8 }}><Pill label="Primary" /><Pill label="Secondary" /><Pill label="Subtle" /></div>
      </GlassCard>
      <KpiRow items={[{ label: 'Token Radius', value: '24px' }, { label: 'Blur', value: '18px' }, { label: 'Contrast', value: 'WCAG-aware' }]} />
      <GlassCard title="Motion Example">
        <div style={{ transition: 'transform .25s ease, opacity .25s ease', padding: 12 }}>
          Hover-ready cards and smooth reveal states can be layered here for Storybook parity.
        </div>
      </GlassCard>
    </main>
  );
}
