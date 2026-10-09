import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { LayoutDashboard, Video, Bell, BarChart3, ShieldCheck } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Monitoring from './pages/Monitoring';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';

const nav = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/monitoring', label: 'Monitoring', icon: Video },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/reports', label: 'Reports', icon: BarChart3 },
];

export default function App() {
  const [mode, setMode] = useState(() => localStorage.getItem('sv_mode') || 'DEMO');

  const changeMode = m => {
    localStorage.setItem('sv_mode', m);
    setMode(m);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950 text-slate-100">
        {/* Sidebar */}
        <aside className="fixed top-0 left-0 h-full w-60 bg-slate-900 border-r border-slate-800 hidden md:flex flex-col">
          <div className="flex items-center gap-2 px-5 h-16 border-b border-slate-800">
            <ShieldCheck className="text-emerald-400" size={24} />
            <div>
              <p className="font-bold leading-none">SafeVision AI</p>
              <p className="text-[10px] text-slate-400 mt-1">
                See Risks. Detect Violations. Respond Faster.
              </p>
            </div>
          </div>
          <nav className="flex-1 p-3 space-y-1">
            {nav.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                    isActive
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : 'text-slate-400 hover:bg-slate-800'
                  }`
                }
              >
                <Icon size={18} /> {label}
              </NavLink>
            ))}
          </nav>
          <p className="p-4 text-[10px] text-slate-500 border-t border-slate-800">
            SafeVision AI • v1.0
          </p>
        </aside>

        <div className="md:pl-60">
          {/* Header with clearly active mode badge */}
          <header className="h-14 flex items-center justify-between px-5 bg-slate-900/80 border-b border-slate-800 sticky top-0 z-30">
            <p className="font-semibold">SafeVision AI</p>

            <div className="flex items-center gap-3">
              {/* Active Mode Indicator */}
              <span
                className={`text-xs font-bold px-3 py-1.5 rounded-full border ${
                  mode === 'REAL'
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                    : 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                }`}
              >
                {mode === 'REAL' ? '● REAL AI MODE' : '● DEMO MODE'}
              </span>

              {/* Mode Toggle */}
              <div className="flex rounded-lg border border-slate-700 overflow-hidden">
                <button
                  onClick={() => changeMode('DEMO')}
                  className={`px-3 py-1.5 text-xs font-semibold transition-colors ${
                    mode === 'DEMO'
                      ? 'bg-amber-500 text-slate-900'
                      : 'text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  DEMO
                </button>
                <button
                  onClick={() => changeMode('REAL')}
                  className={`px-3 py-1.5 text-xs font-semibold transition-colors ${
                    mode === 'REAL'
                      ? 'bg-emerald-500 text-slate-900'
                      : 'text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  REAL
                </button>
              </div>
            </div>
          </header>

          {/* DEMO Warning Banner */}
          {mode === 'DEMO' && (
            <div className="mx-5 mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-xs text-amber-300">
              ⚠️ DEMO MODE — Sample data for demonstration only. Not real AI detections.
            </div>
          )}

          <main className="p-5">
            <Routes>
              <Route path="/" element={<Dashboard mode={mode} />} />
              <Route path="/monitoring" element={<Monitoring mode={mode} />} />
              <Route path="/alerts" element={<Alerts mode={mode} />} />
              <Route path="/reports" element={<Reports mode={mode} />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
