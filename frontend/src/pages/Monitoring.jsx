import { useEffect, useState } from 'react';
import CameraFeed from '../components/CameraFeed';
import { getDetections } from '../services/api';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Monitoring({ mode }) {
  const [scenario, setScenario] = useState('compliant');
  const [detections, setDetections] = useState([]);

  useEffect(() => {
    if (scenario === 'live') {
      setDetections([]);
      return;
    }
    getDetections(mode, scenario).then(setDetections);
  }, [mode, scenario]);

  const persons = detections.filter(d => d.label.toLowerCase() === 'person').length;
  const risks = detections.filter(
    d =>
      d.label.startsWith('no_') ||
      d.label === 'none' ||
      d.label.toLowerCase() === 'fire' ||
      d.label.toLowerCase() === 'smoke'
  );

  const videoUrl = mode === 'REAL' ? `${API}/videos/${scenario}.mp4` : null;

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-4">
        <select
          value={scenario}
          onChange={e => setScenario(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm"
        >
          <option value="compliant">Compliant Video</option>
          <option value="violation">Violation Video</option>
          <option value="fire_smoke">Fire / Smoke Video</option>
          <option value="live">🔴 Live Webcam (REAL)</option>
        </select>

        {scenario === 'live' ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b border-slate-800">
              <p className="text-sm font-medium text-slate-200">Live Webcam — REAL AI Detection</p>
              <span className="text-[10px] font-bold text-red-400 animate-pulse">● LIVE</span>
            </div>
            <img src={`${API}/api/live/stream`} alt="live camera" className="w-full" />
          </div>
        ) : (
          <CameraFeed
            title={`Factory Cam — ${scenario}`}
            videoUrl={videoUrl}
            detections={detections}
            demo={mode === 'DEMO'}
          />
        )}
      </div>

      <div className="space-y-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-sm text-slate-400">Persons Detected</p>
          <p className="text-2xl font-bold text-slate-100">{scenario === 'live' ? '—' : persons}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-sm text-slate-400 mb-2">Active Risks</p>
          {scenario === 'live' ? (
            <p className="text-xs text-slate-500">
              Boxes live video par hi dikhte hain. Incidents → Alerts page + MySQL.
            </p>
          ) : risks.length === 0 ? (
            <p className="text-sm text-emerald-400">No violations ✓</p>
          ) : (
            risks.map((v, i) => (
              <p key={i} className="text-sm text-red-400">
                ⚠ {v.label} ({Math.round(v.confidence * 100)}%)
              </p>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
