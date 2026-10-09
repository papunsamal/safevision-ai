/**
 * Maps AI labels to specific visual styles (Color + Icon/Text)
 */
const getStyleForLabel = label => {
  const l = label.toLowerCase();

  // CRITICAL / RED (Fire, No Helmet)
  if (['fire', 'no_helmet', 'none'].includes(l)) {
    return {
      border: 'border-red-500',
      text: 'text-red-400',
      bg: 'bg-red-900/80',
      displayLabel: l === 'none' ? 'NO HELMET ⚠️' : 'FIRE 🔥',
    };
  }

  // HIGH / ORANGE (Smoke, No Vest - Distinct from Helmet for clarity)
  if (['smoke', 'no_vest', 'without_vest'].includes(l)) {
    return {
      border: 'border-orange-500',
      text: 'text-orange-400',
      bg: 'bg-orange-900/80',
      displayLabel: l === 'smoke' ? 'SMOKE 💨' : 'NO VEST ⚠️',
    };
  }

  // MEDIUM / BLUE (No Gloves)
  if (['no_gloves'].includes(l)) {
    return {
      border: 'border-blue-500',
      text: 'text-blue-400',
      bg: 'bg-blue-900/80',
      displayLabel: 'NO GLOVES 🧤',
    };
  }

  // SAFE / GREEN (Helmet, Vest, Person)
  if (['helmet', 'vest', 'person'].includes(l)) {
    return {
      border: 'border-emerald-500',
      text: 'text-emerald-400',
      bg: 'bg-emerald-900/80',
      displayLabel: `${l.toUpperCase()} ✓`,
    };
  }

  // DEFAULT FALLBACK
  return {
    border: 'border-slate-500',
    text: 'text-slate-400',
    bg: 'bg-slate-800/80',
    displayLabel: label.toUpperCase(),
  };
};

export default function DetectionBox({ d }) {
  const style = getStyleForLabel(d.label);

  return (
    <div
      className={`absolute border-2 ${style.border} transition-all duration-200 ease-out hover:border-[3px]`}
      style={{
        left: `${d.x}%`,
        top: `${d.y}%`,
        width: `${d.w}%`,
        height: `${d.h}%`,
      }}
    >
      {/* Label Tag */}
      <span
        className={`absolute -top-6 left-0 text-[10px] font-bold px-1.5 py-0.5 rounded-t-sm whitespace-nowrap shadow-md backdrop-blur-sm ${style.bg} ${style.text}`}
      >
        {style.displayLabel} {Math.round(d.confidence * 100)}%
      </span>
    </div>
  );
}
