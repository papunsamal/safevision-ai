import { ShieldCheck, TrendingUp } from 'lucide-react'; // Added TrendingUp for future scope or header

export default function ComplianceCard({ compliant, total }) {
  const percent = total ? Math.round((compliant / total) * 100) : 0;

  // Dynamic Styling based on Safety Thresholds
  const getBarColor = () => {
    if (percent >= 80) return 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.4)]'; // Glow effect
    if (percent >= 50) return 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.4)]';
    return 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.4)]';
  };

  const getTextClass = () => {
    if (percent >= 80) return 'text-emerald-400';
    if (percent >= 50) return 'text-amber-400';
    return 'text-red-400';
  };

  const getStatusLabel = () => {
    if (!total) return 'Awaiting Data';
    if (percent >= 80) return 'Excellent';
    if (percent >= 50) return 'Needs Attention';
    return 'Critical Risk';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 relative overflow-hidden group">
      {/* Subtle Background Gradient for Premium Feel */}
      <div
        className={`absolute inset-0 opacity-5 transition-opacity group-hover:opacity-10 ${getTextClass().replace('text-', 'bg-')}`}
      ></div>

      <div className="flex items-center justify-between mb-4 relative z-10">
        <p className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          Safety Compliance
        </p>
        <ShieldCheck className={`${getTextClass()} size-5`} />
      </div>

      <div className="relative z-10">
        <div className="flex items-baseline gap-2">
          <p className={`text-4xl font-bold ${getTextClass()}`}>{total ? `${percent}%` : '—'}</p>
          {total > 0 && (
            <span
              className={`text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800/50 border border-slate-700 ${getTextClass()}`}
            >
              {getStatusLabel()}
            </span>
          )}
        </div>

        <p className="text-xs text-slate-500 mt-1">Based on {total || 0} detected personnel</p>
      </div>

      {/* Progress Bar Container */}
      <div className="mt-4 h-2.5 rounded-full bg-slate-800 overflow-hidden relative z-10">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${getBarColor()}`}
          style={{ width: `${percent}%` }}
        />
      </div>

      {/* Footer Stats */}
      <div className="flex justify-between items-center mt-3 text-[10px] text-slate-500 font-mono relative z-10">
        <span>
          {compliant}/{total} Compliant
        </span>
        <span>{total - compliant} Violations</span>
      </div>
    </div>
  );
}
