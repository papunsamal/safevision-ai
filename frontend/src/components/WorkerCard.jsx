export default function WorkerCard({ id, helmet, vest, gloves }) {
  // HONESTY: status sirf helmet par (vest absence reliably detect nahi hota)
  const compliant = helmet;
  return (
    <div
      className={`rounded-xl border p-4 ${compliant ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-red-500/30 bg-red-500/5'}`}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-200">Worker #{id}</p>
        <span className={`text-xs font-bold ${compliant ? 'text-emerald-400' : 'text-red-400'}`}>
          {compliant ? 'COMPLIANT' : 'VIOLATION'}
        </span>
      </div>
      <div className="flex gap-2 mt-3">
        <Chip ok={helmet} label="Helmet" danger />
        {vest !== undefined && <Chip ok={vest} label="Vest (info)" />}
        {gloves !== undefined && <Chip ok={gloves} label="Gloves" danger />}
      </div>
    </div>
  );
}

function Chip({ ok, label, danger }) {
  const tone = ok
    ? 'bg-emerald-500/10 text-emerald-400'
    : danger
      ? 'bg-red-500/10 text-red-400'
      : 'bg-slate-700/40 text-slate-400';
  return (
    <span className={`px-2 py-1 rounded text-[10px] font-semibold ${tone}`}>
      {ok ? '✓' : '–'} {label}
    </span>
  );
}
