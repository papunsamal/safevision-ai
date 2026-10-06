function colorFor(label) {
  if (['fire', 'no_helmet', 'no_vest', 'no_gloves'].includes(label))
    return 'border-red-500 text-red-400';
  if (label === 'smoke') return 'border-amber-500 text-amber-400';
  return 'border-emerald-500 text-emerald-400';
}

export default function DetectionBox({ d }) {
  const tone = colorFor(d.label);
  return (
    <div
      className={`absolute border-2 ${tone.split(' ')[0]}`}
      style={{ left: `${d.x}%`, top: `${d.y}%`, width: `${d.w}%`, height: `${d.h}%` }}
    >
      <span
        className={`absolute -top-5 left-0 text-[10px] font-bold px-1 rounded bg-slate-950/90 ${tone.split(' ')[1]}`}
      >
        {d.label} {Math.round(d.confidence * 100)}%
      </span>
    </div>
  );
}
