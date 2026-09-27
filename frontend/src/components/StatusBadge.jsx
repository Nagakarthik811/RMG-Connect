export default function StatusBadge({ children, status }) {
  const value = status || children || '';
  const cls = String(value).toLowerCase().replaceAll(' ', '-');
  return <span className={`badge badge-${cls}`}>{value}</span>;
}
