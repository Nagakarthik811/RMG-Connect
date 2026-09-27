import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, BriefcaseBusiness, CalendarDays, UserRound, LogOut, Layers3 } from 'lucide-react';
import api from '../services/api';

export default function Sidebar({ role, onLogout }) {
  const links = role === 'admin' ? [['Dashboard','/admin',LayoutDashboard],['Associates','/associates',Users],['Projects','/projects',BriefcaseBusiness],['Interview Calls','/interviews',CalendarDays]] : [['Dashboard','/associate',LayoutDashboard],['My Profile','/profile',UserRound],['Opportunities','/opportunities',BriefcaseBusiness],['Interviews','/my-interviews',CalendarDays]];
  return <aside className="sidebar"><div className="brand"><div className="brand-mark"><Layers3 size={20}/></div><div><b>RMG Connect</b><small>RESOURCE MANAGEMENT</small></div></div><div className="nav-caption">WORKSPACE</div><nav>{links.map(([label,path,Icon])=><NavLink key={path} to={path} end className={({isActive})=>`nav-link ${isActive?'active':''}`}><Icon size={18}/>{label}</NavLink>)}</nav><div className="sidebar-bottom"><div className="user-chip"><span className="avatar">{role==='admin'?'RM':'AB'}</span><span><b>{role==='admin'?'RMG Admin':'ABC Associate'}</b><small>{role==='admin'?'Resource Manager':'ABC Employee'}</small></span></div><button className="nav-link logout" onClick={onLogout}><LogOut size={18}/>Log out</button></div></aside>;
}
