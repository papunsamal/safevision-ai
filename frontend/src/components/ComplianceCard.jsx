import { ShieldCheck } from 'lucide-react';

export default function ComplianceCard({ compliant, total }) {
  const percent = total ? Math.round((compliant / total) * 100) : 0;
  const bar = percent >= 80 ? 'bg-emerald-500' : percent >= 50 ? 'bg-amber-500' : 'bg-red-500';
  const text =
    percent >= 80 ? 'text-emerald-400' : percent >= 50 ? 'text-amber-400' : 'text-red-400';

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">Safety Compliance</p>
        <ShieldCheck className={text} size={20} />
      </div>
      <p className={`text-3xl font-bold mt-2 ${total ? text : 'text-slate-500'}`}>
        {total ? `${percent}%` : '—'}
      </p>
      <div className="mt-3 h-2 rounded-full bg-slate-800">
        <div className={`h-2 rounded-full ${bar}`} style={{ width: `${percent}%` }} />
      </div>
      <p className="text-xs text-slate-500 mt-2">
        {total ? `${compliant}/${total} workers compliant` : 'Insufficient data'}
      </p>
    </div>
  );
}
