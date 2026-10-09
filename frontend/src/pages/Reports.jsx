import { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import { getReports } from '../services/api';
import { Activity, AlertCircle, Database } from 'lucide-react'; // Icons for status

// Custom Tooltip Component for better readability
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs">
        <p className="text-slate-400 mb-1 font-semibold uppercase">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="font-bold">
            {entry.name}: {entry.value}
            {entry.dataKey === 'value' ? '%' : ''}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function Reports({ mode }) {
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    getReports(mode)
      .then(data => {
        setReports(data);
        setError(null);
      })
      .catch(err => {
        console.error('Report fetch failed:', err);
        setError('Unable to load historical trends. Check database connection.');
      })
      .finally(() => setLoading(false));
  }, [mode]);

  // Loading Skeleton
  if (loading) {
    return (
      <div className="grid lg:grid-cols-2 gap-6 animate-pulse">
        {[1, 2].map(i => (
          <div key={i} className="h-80 bg-slate-800/50 rounded-xl border border-slate-700"></div>
        ))}
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-red-400 space-y-2">
        <AlertCircle size={48} className="opacity-50" />
        <p className="font-semibold">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 text-sm mt-2"
        >
          Retry
        </button>
      </div>
    );
  }

  const empty =
    !reports ||
    ((reports.complianceTrend?.length || 0) === 0 && (reports.incidentTrend?.length || 0) === 0);

  if (empty) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-500 space-y-3 bg-slate-900/30 rounded-xl border border-dashed border-slate-700">
        <Database size={48} className="opacity-20" />
        <p className="text-sm font-medium">No historical data available yet.</p>
        <p className="text-xs opacity-60 max-w-md text-center">
          Real analyses ke baad trends yahan MySQL se automatically populate honge. Run a few video
          sessions or check live feed to generate data points.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-200 flex items-center gap-2">
          <Activity size={18} className="text-emerald-400" />
          Historical Analytics
        </h2>
        <span className="text-xs text-slate-500 font-mono bg-slate-800/50 px-2 py-1 rounded border border-slate-700">
          Source: MySQL Daily Stats
        </span>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Compliance Trend Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group">
          {/* Subtle Glow */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 blur-3xl rounded-full -mr-16 -mt-16 pointer-events-none"></div>

          <h3 className="font-semibold text-slate-100 mb-4 relative z-10">
            Safety Compliance Over Time
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={reports.complianceTrend}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis
                dataKey="day"
                stroke="#94a3b8"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#94a3b8"
                fontSize={12}
                domain={[0, 100]}
                tickFormatter={val => `${val}%`}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#475569', strokeWidth: 1 }} />
              <Area
                type="monotone"
                dataKey="value"
                name="Compliance %"
                stroke="#10b981"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorValue)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Incident Trend Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group">
          {/* Subtle Glow */}
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-purple-500/5 blur-3xl rounded-full -ml-16 -mb-16 pointer-events-none"></div>

          <h3 className="font-semibold text-slate-100 mb-4 relative z-10">
            Incident Breakdown (PPE vs Hazards)
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={reports.incidentTrend} barSize={20}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis
                dataKey="day"
                stroke="#94a3b8"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#94a3b8"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                allowDecimals={false}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: '#334155', opacity: 0.2 }} />
              <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }} iconType="circle" />
              <Bar dataKey="ppe" name="PPE Violations" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="fire" name="Fire Incidents" fill="#ef4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="smoke" name="Smoke Alerts" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
