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

export default function Reports({ mode }) {
  const [reports, setReports] = useState(null);
  useEffect(() => {
    getReports(mode).then(setReports);
  }, [mode]);

  if (!reports) return <p className="text-sm text-slate-500">Insufficient data</p>;

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h3 className="font-semibold text-slate-100 mb-4">Compliance Trend</h3>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={reports.complianceTrend}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
            <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#10b981"
              fill="#10b98133"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h3 className="font-semibold text-slate-100 mb-4">Incident Trend</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={reports.incidentTrend}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
            <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
            <YAxis stroke="#64748b" fontSize={11} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey="ppe" fill="#8b5cf6" radius={3} />
            <Bar dataKey="fire" fill="#ef4444" radius={3} />
            <Bar dataKey="smoke" fill="#f59e0b" radius={3} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
