import { useEffect, useRef, useState } from 'react';
import { Video } from 'lucide-react';
import DetectionBox from './DetectionBox';

export default function CameraFeed({
  title,
  status = 'ONLINE',
  videoUrl,
  detections = [],
  timeline = null,
  demo,
}) {
  const videoRef = useRef(null);
  const [synced, setSynced] = useState(detections);

  // Static/DEMO: boxes jaisi hain waisi
  useEffect(() => {
    if (!timeline) setSynced(detections);
  }, [detections, timeline]);

  // REAL: video ke CURRENT time ke matching analyzed frame ki detections
  const onTimeUpdate = () => {
    if (!timeline || !videoRef.current || !videoRef.current.duration) return;
    const pct = (videoRef.current.currentTime / videoRef.current.duration) * 100;
    let cur = [];
    for (const entry of timeline) {
      if (entry.t <= pct + 1) cur = entry.detections;
      else break;
    }
    setSynced(cur);
  };

  return (
    <div className="rounded-xl overflow-hidden border border-slate-800 bg-slate-950">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900 border-b border-slate-800">
        <p className="text-sm text-slate-200">{title}</p>
        <span
          className={`text-[10px] font-bold px-2 py-0.5 rounded ${status === 'ONLINE' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}
        >
          {status}
        </span>
      </div>
      <div className="relative aspect-video bg-gradient-to-br from-slate-800 via-slate-900 to-slate-950">
        {videoUrl ? (
          <video
            ref={videoRef}
            onTimeUpdate={onTimeUpdate}
            src={videoUrl}
            controls
            autoPlay
            muted
            loop
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-slate-600">
            <Video size={40} />
          </div>
        )}
        {synced.map((d, i) => (
          <DetectionBox key={i} d={d} />
        ))}
        {demo && (
          <span className="absolute top-2 left-2 text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500 text-slate-900">
            DEMO MODE
          </span>
        )}
      </div>
    </div>
  );
}
