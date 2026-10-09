import { useEffect, useRef } from 'react';

/**
 * Helper to convert raw AI labels into human-readable status for Judges
 */
const getDisplayLabel = label => {
  const l = label.toLowerCase();

  // Helmet Logic
  if (l === 'helmet') return 'HELMET ✓';
  if (l === 'no_helmet' || l === 'none') return 'NO HELMET ⚠️';

  // Vest Logic (UPDATED FOR YOUR REQUEST)
  if (l === 'vest') return 'VEST ✓';
  if (l === 'no_vest' || l === 'without_vest') return 'NO VEST ⚠️';

  // Hazards
  if (l === 'fire') return 'FIRE 🔥';
  if (l === 'smoke') return 'SMOKE 💨';

  // Person
  if (l === 'person' || l === 'Person') return 'PERSON 👤';

  // Fallback
  return label.toUpperCase();
};

/**
 * Get Color based on severity/status
 */
const getColorClass = label => {
  const l = label.toLowerCase();
  // Red for Critical/Helmet Missing/Fire
  if (['no_helmet', 'none', 'fire'].includes(l)) return 'border-red-500 text-red-400 bg-red-900/30';
  // Orange for Medium/Vest Missing/Smoke
  if (['no_vest', 'smoke'].includes(l)) return 'border-orange-500 text-orange-400 bg-orange-900/30';
  // Green for Compliant Gear
  if (['helmet', 'vest'].includes(l))
    return 'border-emerald-500 text-emerald-400 bg-emerald-900/30';
  // Blue for Persons
  if (['person'].includes(l)) return 'border-blue-500 text-blue-400 bg-blue-900/30';

  return 'border-slate-500 text-slate-400 bg-slate-800/50';
};

export default function CameraFeed({ title, videoUrl, detections, timeline, demo }) {
  const containerRef = useRef(null);

  // Auto-play video when URL changes or new data arrives
  useEffect(() => {
    if (!videoUrl) return;

    const timer = setTimeout(() => {
      const vid = document.querySelector(`video[src="${videoUrl}"]`);
      if (vid) {
        vid.play().catch(e => console.log('Autoplay blocked:', e));
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [videoUrl]);

  return (
    <div className="relative w-full aspect-video bg-black rounded-xl overflow-hidden border border-slate-700 shadow-lg group">
      {/* Header Badge */}
      <div className="absolute top-2 left-2 z-20 flex items-center gap-2">
        <span
          className={`px-2 py-1 rounded-md text-xs font-bold uppercase tracking-wider ${demo ? 'bg-amber-600 text-white' : 'bg-emerald-600 text-white'}`}
        >
          {demo ? 'DEMO MODE' : 'REAL AI'}
        </span>
        <span className="text-xs text-slate-400 font-mono">{title}</span>
      </div>

      {/* Video Element */}
      {videoUrl && (
        <video
          src={videoUrl}
          controls={!demo}
          autoPlay
          muted
          loop
          playsInline
          className="w-full h-full object-contain"
        />
      )}

      {!videoUrl && !detections?.length && (
        <div className="flex items-center justify-center h-full text-slate-500">
          Select a video source...
        </div>
      )}

      {/* Bounding Boxes Overlay */}
      {detections && detections.length > 0 && (
        <div className="absolute inset-0 pointer-events-none z-10">
          {detections.map((det, idx) => {
            // Calculate percentage positions for responsive overlay
            const style = {
              left: `${det.x}%`,
              top: `${det.y}%`,
              width: `${det.w}%`,
              height: `${det.h}%`,
            };

            const displayLabel = getDisplayLabel(det.label);
            const colorClasses = getColorClass(det.label);

            return (
              <div
                key={idx}
                className={`absolute border-2 transition-all duration-200 ease-out hover:border-[3px] ${colorClasses}`}
                style={style}
              >
                {/* Label Tag */}
                <div
                  className={`absolute -top-6 left-0 px-2 py-0.5 rounded-t-sm text-[10px] font-bold whitespace-nowrap shadow-md backdrop-blur-sm ${colorClasses.split(' ')[1]} bg-opacity-90`}
                >
                  {displayLabel} {Math.round(det.confidence * 100)}%
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Live Indicator Dot (if applicable) */}
      {title.includes('Live') && (
        <div className="absolute top-2 right-2 flex items-center gap-1 bg-red-600/80 px-2 py-1 rounded-full">
          <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
          <span className="text-[10px] font-bold text-white">LIVE</span>
        </div>
      )}
    </div>
  );
}
