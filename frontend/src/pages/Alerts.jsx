import { useEffect, useState } from 'react';
import AlertCard from '../components/AlertCard';
import { getAlerts } from '../services/api';
import { Inbox } from 'lucide-react'; // For empty state icon

export default function Alerts({ mode }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getAlerts(mode)
      .then(data => {
        setAlerts(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch alerts:', err);
        setLoading(false);
      });
  }, [mode]);

  // Loading State
  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-24 bg-slate-800/50 rounded-xl border border-slate-700"></div>
        ))}
      </div>
    );
  }

  // Empty State
  if (!alerts.length) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-500 space-y-3">
        <Inbox size={48} className="opacity-20" />
        <p className="text-sm font-medium">No active incidents logged.</p>
        <p className="text-xs opacity-60">
          Run a video analysis or check live feed to generate alerts.
        </p>
      </div>
    );
  }

  // Success State
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-lg font-bold text-slate-200">Recent Incidents</h2>
        <span className="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded-md border border-slate-700">
          {alerts.length} Records
        </span>
      </div>

      {alerts.map(a => (
        <AlertCard key={a.id} alert={a} />
      ))}
    </div>
  );
}
