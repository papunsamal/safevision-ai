import { Video } from 'lucide-react';
import DetectionBox from './DetectionBox';

export default function CameraFeed({ title, status = 'ONLINE', videoUrl, detections = [], demo }) {
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
        {detections.map((d, i) => (
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
