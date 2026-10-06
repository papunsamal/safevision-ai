export default function WorkerCard({ id, helmet, vest, gloves }) {
  const compliant = helmet && vest;
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
        <Chip ok={helmet} label="Helmet" />
        <Chip ok={vest} label="Vest" />
        {gloves !== undefined && <Chip ok={gloves} label="Gloves" />}
      </div>
    </div>
  );
}

function Chip({ ok, label }) {
  return (
    <span
      className={`px-2 py-1 rounded text-[10px] font-semibold ${ok ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}
    >
      {ok ? '✓' : '✗'} {label}
    </span>
  );
}
