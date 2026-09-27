export default function DashboardCard({ label, value, icon: Icon, tone = '' }) {
  return <div className="metric-card"><div><span className="metric-label">{label}</span><strong>{value ?? '—'}</strong></div><span className={`metric-icon ${tone}`}>{Icon && <Icon size={20}/>}</span></div>;
}
