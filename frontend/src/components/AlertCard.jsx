import { Flame, Wind, HardHat, Info } from 'lucide-react';

const iconFor = { FIRE: Flame, SMOKE: Wind, PPE: HardHat };
const sevTone = {
  LOW: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  HIGH: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  CRITICAL: 'bg-red-500/10 text-red-400 border-red-500/30',
};

export default function AlertCard({ alert }) {
  const Icon = iconFor[alert.type] || Info;
  return (
    <div className="flex items-start gap-3 bg-slate-900 border border-slate-800 rounded-xl p-4">
      <span className="p-2 rounded-lg bg-slate-800 text-slate-300">
        <Icon size={18} />
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium text-slate-200 truncate">{alert.message}</p>
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${sevTone[alert.severity]}`}
          >
            {alert.severity}
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          {alert.camera} • {alert.zone} • {alert.time}
        </p>
      </div>
    </div>
  );
}
