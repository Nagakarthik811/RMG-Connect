import { displayEmployeeId } from '../services/display';

export default function DataTable({ columns, rows, empty = 'No records found.' }) {
  return <div className="table-wrap"><table><thead><tr>{columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr></thead><tbody>{rows.length ? rows.map((row, i) => <tr key={row.id ?? i}>{columns.map((c) => <td key={c.key}>{c.render ? c.render(row) : c.key === 'employee_id' ? displayEmployeeId(row[c.key]) : row[c.key] ?? '—'}</td>)}</tr>) : <tr><td className="empty" colSpan={columns.length}>{empty}</td></tr>}</tbody></table></div>;
}
