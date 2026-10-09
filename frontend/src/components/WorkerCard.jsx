import { ShieldCheck, AlertTriangle } from 'lucide-react';

export default function WorkerCard({ id, helmet, vest, gloves }) {
  // HONESTY LOGIC: Status sirf helmet par depend karta hai
  // kyunki dataset mein reliable 'no_vest' detection nahi hai.
  const isCompliant = !!helmet;

  return (
    <div
      className={`relative rounded-xl border p-4 transition-all duration-300 hover:shadow-lg ${
        isCompliant
          ? 'border-emerald-500/30 bg-emerald-900/10 hover:border-emerald-500/50'
          : 'border-red-500/40 bg-red-900/10 hover:border-red-500/60 shadow-md'
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-bold text-slate-200 flex items-center gap-2">
          Worker #{id}
          {!isCompliant && <AlertTriangle size={14} className="text-red-400 animate-pulse" />}
        </p>
        <span
          className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
            isCompliant
              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
              : 'bg-red-500/20 text-red-400 border-red-500/30'
          }`}
        >
          {isCompliant ? 'COMPLIANT' : 'VIOLATION'}
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        <Chip ok={!!helmet} label="Helmet" type="critical" />
        {/* HONEST LABEL: "Not Checked" instead of "Vest (info)" */}
        {vest !== undefined && <Chip ok={!!vest} label={vest ? 'Vest' : 'Vest: N/A'} type="info" />}
        {gloves !== undefined && <Chip ok={!!gloves} label="Gloves" type="secondary" />}
      </div>

      {!isCompliant && (
        <div className="absolute inset-0 pointer-events-none rounded-xl ring-1 ring-inset ring-red-500/20"></div>
      )}
    </div>
  );
}

function Chip({ ok, label, type = 'default' }) {
  let toneClasses = '';

  if (type === 'critical') {
    toneClasses = ok
      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
      : 'bg-red-500/20 text-red-400 border-red-500/30';
  } else if (type === 'info') {
    toneClasses = ok
      ? 'bg-slate-700/50 text-slate-300 border-slate-600'
      : 'bg-slate-800/50 text-slate-500 border-slate-700 italic';
  } else {
    toneClasses = ok
      ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
      : 'bg-orange-500/10 text-orange-400 border-orange-500/20';
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-[10px] font-semibold border backdrop-blur-sm ${toneClasses}`}
    >
      <span className="text-xs">{ok ? '✓' : '–'}</span>
      {label}
    </span>
  );
}
