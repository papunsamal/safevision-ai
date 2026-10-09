import { useEffect, useState } from 'react';
import { Users, HardHat, Flame, Wind, Activity } from 'lucide-react';
import ComplianceCard from '../components/ComplianceCard';
import WorkerCard from '../components/WorkerCard';
import { getStats, getWorkers } from '../services/api';

/**
 * Reusable Stat Card Component with subtle hover effects
 */
function StatCard({ icon: Icon, label, value, tone }) {
  return (
    <div className="group bg-slate-900 border border-slate-800 rounded-xl p-5 transition-all duration-300 hover:border-slate-700 hover:shadow-lg relative overflow-hidden">
      {/* Subtle Background Gradient on Hover */}
      <div
        className={`absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity ${tone.replace('text-', 'bg-')}`}
      ></div>

      <div className="flex items-center justify-between mb-2 relative z-10">
        <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</p>
        <Icon size={18} className={`${tone} group-hover:scale-110 transition-transform`} />
      </div>

      <p className="text-3xl font-bold mt-1 text-slate-100 relative z-10">{value ?? '—'}</p>
    </div>
  );
}

export default function Dashboard({ mode }) {
  const [stats, setStats] = useState(null);
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([getStats(mode), getWorkers(mode)])
      .then(([s, w]) => {
        setStats(s);
        setWorkers(w);
        setError(null);
      })
      .catch(err => {
        console.error('Dashboard fetch failed:', err);
        setError('Unable to load real-time data. Check backend connection.');
      })
      .finally(() => setLoading(false));
  }, [mode]);

  // Loading Skeleton
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-24 bg-slate-800/50 rounded-xl border border-slate-700"></div>
          ))}
        </div>
        <div className="h-32 bg-slate-800/50 rounded-xl border border-slate-700"></div>
        <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-32 bg-slate-800/50 rounded-xl border border-slate-700"></div>
          ))}
        </div>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-red-400 space-y-2">
        <Activity size={48} className="opacity-50" />
        <p className="font-semibold">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={Users}
          label="Total Unique Personnel (Session)"
          value={stats?.totalWorkers}
          tone="text-blue-400"
        />
        <StatCard
          icon={HardHat}
          label="PPE Violations"
          value={stats?.ppeViolations}
          tone="text-red-400"
        />
        <StatCard
          icon={Flame}
          label="Fire Incidents"
          value={stats?.fireIncidents}
          tone="text-orange-400"
        />
        <StatCard
          icon={Wind}
          label="Smoke Incidents"
          value={stats?.smokeIncidents}
          tone="text-amber-400"
        />
      </div>

      {/* Compliance Progress Bar */}
      <ComplianceCard compliant={stats?.compliantWorkers} total={stats?.totalWorkers} />

      {/* Worker Status Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-100 text-lg">Live Worker PPE Status</h3>
          <span className="text-xs text-slate-500 font-mono bg-slate-800/50 px-2 py-1 rounded border border-slate-700">
            {workers.length} Detected
          </span>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {workers.length ? (
            workers.map(w => <WorkerCard key={w.id} {...w} />)
          ) : (
            <div className="col-span-full flex flex-col items-center justify-center py-12 text-slate-500 bg-slate-900/50 rounded-xl border border-dashed border-slate-700">
              <Users size={32} className="mb-2 opacity-30" />
              <p>No active workers detected in current frame.</p>
              <p className="text-xs mt-1 opacity-60">Run a video analysis or check live feed.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
