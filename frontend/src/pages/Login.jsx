import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers3, ArrowRight, ShieldCheck } from 'lucide-react';
import api from '../services/api';

export default function Login({ onLogin }) {
 const [username,setUsername]=useState(''); const [password,setPassword]=useState(''); const [error,setError]=useState(''); const [busy,setBusy]=useState(false); const navigate=useNavigate();
 async function submit(e){e.preventDefault();setError('');setBusy(true);try{const {data}=await api.post('login/',{username,password});onLogin(data);navigate(data.role==='admin'?'/admin':'/associate');}catch(err){setError(err.message);}finally{setBusy(false);}}
 return <div className="login-page"><section className="login-visual"><div className="login-brand"><span><Layers3/></span> RMG Connect</div><div className="login-message"><div className="overline">RESOURCE MANAGEMENT GROUP</div><h1>Connect talent<br/>with opportunity.</h1><p>A focused workspace to manage unallocated talent, discover project matches, and move interviews forward.</p><div className="login-proof"><ShieldCheck size={17}/> Secure access for ABC associates and RMG teams</div></div><div className="visual-foot">ABC <span>•</span> INTERNAL WORKSPACE</div></section><section className="login-panel"><div className="login-box"><span className="login-icon"><Layers3 size={22}/></span><div className="eyebrow">WELCOME BACK</div><h2>Sign in to RMG Connect</h2><p className="muted">Use your account to continue to your workspace.</p>{error&&<div className="alert">{error}</div>}<form onSubmit={submit} className="form-stack"><label>Username<input value={username} onChange={e=>setUsername(e.target.value)} required autoComplete="username" placeholder="Enter your username"/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} required autoComplete="current-password" placeholder="Enter your password"/></label><button className="button primary full" disabled={busy}>{busy?'Signing in…':'Sign in'} <ArrowRight size={17}/></button></form>
 </div><div className="login-copyright">© 2026 RMG Connect</div></section></div>
}
