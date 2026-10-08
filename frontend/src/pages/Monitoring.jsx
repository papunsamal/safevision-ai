import { useEffect, useState } from 'react';
import CameraFeed from '../components/CameraFeed';
import { getDetections, getAlerts } from '../services/api';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Monitoring({ mode }) {
  const [scenario, setScenario] = useState('compliant');
  const [detections, setDetections] = useState([]);
  const [timeline, setTimeline] = useState(null);
  const [stats, setStats] = useState(null);
  const [liveIncidents, setLiveIncidents] = useState([]);

  useEffect(() => {
    setDetections([]);
    setTimeline(null);
    setStats(null);
    if (scenario === 'live') return;
    getDetections(mode, scenario)
      .then(res => {
        const list = Array.isArray(res) ? res : (res?.detections ?? []);
        setDetections(list);
        setTimeline(!Array.isArray(res) ? (res?.timeline ?? null) : null);
        setStats(!Array.isArray(res) ? (res?.stats ?? null) : null);
      })
      .catch(err => {
        console.error('Detection failed:', err);
        setDetections([]);
        setTimeline(null);
        setStats(null);
      });
  }, [mode, scenario]);

  // Live incidents poll (sirf live mode mein)
  useEffect(() => {
    if (scenario !== 'live') {
      setLiveIncidents([]);
      return;
    }
    const poll = setInterval(() => {
      getAlerts('REAL')
        .then(a => setLiveIncidents(a.slice(0, 5)))
        .catch(() => {});
    }, 3000);
    return () => clearInterval(poll);
  }, [scenario]);

  const risks = detections.filter(
    d =>
      d.label === 'no_helmet' ||
      d.label.toLowerCase() === 'fire' ||
      d.label.toLowerCase() === 'smoke'
  );

  // FIX: CURRENT visible persons gin (aggregate 10 nahi)
  const personsDetected = detections.filter(
    d => d.label.toLowerCase() === 'person' || d.label === 'Person'
  ).length;

  const videoUrl = mode === 'REAL' && scenario !== 'live' ? `${API}/videos/${scenario}.mp4` : null;

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
            timeline={timeline}
            demo={mode === 'DEMO'}
          />
        )}
      </div>

      <div className="space-y-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-sm text-slate-400">Persons Detected</p>
          <p className="text-2xl font-bold text-slate-100">{personsDetected}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-sm text-slate-400 mb-2">Active Risks</p>
          {scenario === 'live' ? (
            <div className="space-y-2">
              {liveIncidents.length === 0 ? (
                <p className="text-sm text-emerald-400">No active violations ✓</p>
              ) : (
                liveIncidents.map(v => (
                  <p key={v.id} className="text-sm text-red-400">
                    ⚠ {v.message} ({v.time})
                  </p>
                ))
              )}
            </div>
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
