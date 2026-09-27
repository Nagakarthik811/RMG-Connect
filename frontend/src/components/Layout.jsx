import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';

const titles = {'/admin':'Admin Dashboard','/associates':'Associates','/projects':'Projects','/interviews':'Interview Calls','/associate':'Associate Dashboard','/profile':'My Profile','/opportunities':'My Opportunities','/my-interviews':'My Interview Calls'};
export default function Layout({ role, children, onLogout }) {
 const { pathname } = useLocation();
 return <div className="app-shell"><Sidebar role={role} onLogout={onLogout}/><main className="main-area"><header className="topbar"><div><span className="eyebrow">RMG CONNECT / WORKSPACE</span><h1>{titles[pathname] || 'RMG Connect'}</h1></div><div className="top-user"><span className="online-dot"/> {role==='admin'?'RMG Admin':'ABC Associate'}</div></header><div className="page-content">{children}</div><footer>RMG Connect <span>•</span> Resource Management Group</footer></main></div>;
}
