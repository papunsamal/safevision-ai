import { Flame, Wind, HardHat, Shirt, Hand, Info } from 'lucide-react'; // Added Shirt & Hand icons

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Dynamic Icon Mapper based on Alert Type OR specific Rule/Message keywords
 */
const getIconAndColor = alert => {
  const msg = alert.message?.toLowerCase() || '';
  const rule = alert.rule?.toUpperCase() || '';

  // Fire Hazard
  if (alert.type === 'FIRE' || msg.includes('fire')) {
    return { Icon: Flame, color: 'text-red-400', bg: 'bg-red-900/20 border-red-800' };
  }

  // Smoke Hazard
  if (alert.type === 'SMOKE' || msg.includes('smoke')) {
    return { Icon: Wind, color: 'text-orange-400', bg: 'bg-orange-900/20 border-orange-800' };
  }

  // PPE Violations (Helmet, Vest, Gloves)
  if (alert.type === 'PPE') {
    // Specific Check for Helmet
    if (msg.includes('helmet') || rule === 'NO_HELMET') {
      return { Icon: HardHat, color: 'text-yellow-400', bg: 'bg-yellow-900/20 border-yellow-800' };
    }

    // Specific Check for Vest (Future-proofing your logic)
    if (msg.includes('vest') || rule === 'NO_VEST') {
      return { Icon: Shirt, color: 'text-purple-400', bg: 'bg-purple-900/20 border-purple-800' };
    }

    // Specific Check for Gloves
    if (msg.includes('glove') || rule === 'NO_GLOVES') {
      return { Icon: Hand, color: 'text-blue-400', bg: 'bg-blue-900/20 border-blue-800' };
    }

    // Default PPE (Generic Warning)
    return { Icon: HardHat, color: 'text-slate-300', bg: 'bg-slate-800 border-slate-700' };
  }

  // Fallback
  return { Icon: Info, color: 'text-slate-400', bg: 'bg-slate-800 border-slate-700' };
};

const sevTone = {
  LOW: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  HIGH: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
  CRITICAL: 'bg-red-500/10 text-red-400 border-red-500/30',
};

export default function AlertCard({ alert }) {
  const { Icon, color, bg } = getIconAndColor(alert);

  return (
    <div
      className={`flex items-start gap-3 rounded-xl p-4 border transition-all hover:shadow-md ${bg}`}
    >
      {/* Left: Icon Container */}
      <span className={`p-2 rounded-lg bg-black/20 backdrop-blur-sm ${color}`}>
        <Icon size={20} strokeWidth={2.5} />
      </span>

      {/* Middle: Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <p className="text-sm font-semibold text-slate-100 truncate">{alert.message}</p>

          {/* Severity Badge */}
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border whitespace-nowrap ${sevTone[alert.severity] || sevTone.MEDIUM}`}
          >
            {alert.severity}
          </span>
        </div>

        {/* Meta Info */}
        <p className="text-xs text-slate-400 flex items-center gap-2">
          <span className="font-mono opacity-70">{alert.camera}</span>
          <span>•</span>
          <span>{alert.zone}</span>
          <span>•</span>
          <span className="italic">{alert.time}</span>
        </p>

        {/* Evidence Snapshot */}
        {alert.frame_url && (
          <div className="mt-3 relative group cursor-pointer overflow-hidden rounded-lg border border-slate-700 w-fit max-w-full">
            <img
              src={`${API}${alert.frame_url}`}
              alt="Evidence"
              className="h-28 object-cover opacity-90 group-hover:opacity-100 transition-opacity"
            />
            <div className="absolute bottom-1 right-1 bg-black/60 px-1.5 py-0.5 rounded text-[9px] text-white uppercase tracking-wider">
              Evidence
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
