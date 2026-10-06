import { useEffect, useState } from 'react';
import { Users, HardHat, Flame, Wind } from 'lucide-react';
import ComplianceCard from '../components/ComplianceCard';
import WorkerCard from '../components/WorkerCard';
import { getStats, getWorkers } from '../services/api';

function Card({ icon: Icon, label, value, tone }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">{label}</p>
        <Icon size={18} className={tone} />
      </div>
      <p className="text-3xl font-bold mt-2 text-slate-100">{value ?? '—'}</p>
    </div>
  );
}

export default function Dashboard({ mode }) {
  const [stats, setStats] = useState(null);
  const [workers, setWorkers] = useState([]);

  useEffect(() => {
    getStats(mode).then(setStats);
    getWorkers(mode).then(setWorkers);
  }, [mode]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card icon={Users} label="Total Workers" value={stats?.totalWorkers} tone="text-blue-400" />
        <Card
          icon={HardHat}
          label="PPE Violations"
          value={stats?.ppeViolations}
          tone="text-red-400"
        />
        <Card
          icon={Flame}
          label="Fire Incidents"
          value={stats?.fireIncidents}
          tone="text-red-400"
        />
        <Card
          icon={Wind}
          label="Smoke Incidents"
          value={stats?.smokeIncidents}
          tone="text-amber-400"
        />
      </div>
      <ComplianceCard compliant={stats?.compliantWorkers} total={stats?.totalWorkers} />
      <div>
        <h3 className="font-semibold text-slate-100 mb-3">Worker PPE Status</h3>
        <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {workers.length ? (
            workers.map(w => <WorkerCard key={w.id} {...w} />)
          ) : (
            <p className="text-sm text-slate-500">Insufficient data</p>
          )}
        </div>
      </div>
    </div>
  );
}
