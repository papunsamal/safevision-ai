import { useEffect, useState } from 'react';
import CameraFeed from '../components/CameraFeed';
import { getDetections, getAlerts } from '../services/api';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper for Right Panel Text
const getStatusText = label => {
  const l = label.toLowerCase();
  if (['no_helmet', 'none'].includes(l)) return 'No Helmet Detected';
  if (['no_vest', 'without_vest'].includes(l)) return 'No Vest Detected'; // ADDED THIS LINE
  if (l === 'fire') return 'Fire Hazard!';
  if (l === 'smoke') return 'Smoke Alert!';
  if (l === 'helmet') return 'Helmet OK';
  if (l === 'vest') return 'Vest OK';
  return label;
};

export default function Monitoring({ mode }) {
  const [scenario, setScenario] = useState('compliant');
  const [detections, setDetections] = useState([]);
  const [timeline, setTimeline] = useState(null);
  const [stats, setStats] = useState(null);
  const [liveIncidents, setLiveIncidents] = useState([]);

  // Fetch Detections when scenario or mode changes
  useEffect(() => {
    setDetections([]);
    setTimeline(null);
    setStats(null);

    if (scenario === 'live') return; // Skip API call for live stream (handled by MJPEG img tag)

    getDetections(mode, scenario)
      .then(res => {
        // Handle both array response (old format) and object response (new format with timeline/stats)
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

  // Poll Alerts for Live Mode
  useEffect(() => {
    if (scenario !== 'live') {
      setLiveIncidents([]);
      return;
    }

    const poll = setInterval(() => {
      getAlerts('REAL') // Always fetch REAL alerts even if UI says LIVE (assuming backend pushes to DB)
        .then(a => setLiveIncidents(a.slice(0, 5))) // Show top 5 recent
        .catch(() => {});
    }, 3000);

    return () => clearInterval(poll);
  }, [scenario]);

  // Filter Risks for Sidebar Display
  const risks = detections.filter(
    d => ['no_helmet', 'none', 'no_vest', 'fire', 'smoke'].includes(d.label.toLowerCase()) // Added 'no_vest' here too
  );

  // Count Persons accurately
  const personsDetected = detections.filter(d => d.label.toLowerCase() === 'person').length;

  // Determine Video URL
  const videoUrl = mode === 'REAL' && scenario !== 'live' ? `${API}/videos/${scenario}.mp4` : null;

  return (
    <div className="grid lg:grid-cols-3 gap-6 p-6 max-w-7xl mx-auto">
      {/* LEFT COLUMN: Video Player & Controls */}
      <div className="lg:col-span-2 space-y-4">
        {/* Scenario Selector */}
        <div className="flex items-center justify-between bg-slate-800/50 p-3 rounded-lg border border-slate-700">
          <select
            value={scenario}
            onChange={e => setScenario(e.target.value)}
            className="bg-slate-900 border border-slate-600 text-white rounded-md px-3 py-2 focus:ring-2 focus:ring-emerald-500 outline-none min-w-[200px]"
          >
            <option value="compliant">✅ Compliant Video</option>
            <option value="violation">⚠️ Violation Video</option>
            <option value="fire_smoke">🔥 Fire / Smoke Video</option>
            <option value="live">🔴 Live Webcam (REAL)</option>
          </select>

          <span className="text-xs text-slate-400 font-mono">
            Mode:{' '}
            <span
              className={
                mode === 'REAL' ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'
              }
            >
              {mode}
            </span>
          </span>
        </div>

        {/* Video Component */}
        {scenario === 'live' ? (
          <div className="relative w-full aspect-video bg-black rounded-xl overflow-hidden border border-slate-700 shadow-lg">
            <img
              src={`${API}/api/live/stream`}
              alt="Live Stream"
              className="w-full h-full object-contain"
            />
            {/* Overlay for Live Status */}
            <div className="absolute top-2 right-2 flex items-center gap-2 bg-red-600/80 px-2 py-1 rounded-full">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
              <span className="text-xs font-bold text-white">LIVE FEED</span>
            </div>
          </div>
        ) : (
          <CameraFeed
            title={`Factory Cam — ${scenario.replace('_', ' ').toUpperCase()}`}
            videoUrl={videoUrl}
            detections={detections}
            timeline={timeline}
            demo={mode === 'DEMO'}
          />
        )}
      </div>

      {/* RIGHT COLUMN: Stats & Risks */}
      <div className="space-y-4">
        {/* Total Persons Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <p className="text-sm text-slate-400 mb-1">Visible in Current Frame</p>
          <p className="text-4xl font-bold text-slate-100">{personsDetected}</p>
        </div>

        {/* Active Risks List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm min-h-[200px]">
          <p className="text-sm text-slate-400 mb-3 font-semibold uppercase tracking-wide">
            Active Risks
          </p>

          {scenario === 'live' ? (
            /* For Live Mode: Show Recent DB Alerts */
            liveIncidents.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-32 text-emerald-400">
                <span className="text-2xl mb-2">✓</span>
                <p className="text-sm">No active violations</p>
              </div>
            ) : (
              <ul className="space-y-2">
                {liveIncidents.map(v => (
                  <li
                    key={v.id}
                    className="flex items-start gap-2 p-2 bg-red-900/20 border-l-2 border-red-500 rounded-r text-sm"
                  >
                    <span className="text-red-400 mt-0.5">⚠</span>
                    <div>
                      <p className="text-red-300 font-medium">{v.message}</p>
                      <p className="text-xs text-slate-500">
                        {v.time} • {v.zone}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            )
          ) : /* For Recorded Video: Show Current Frame Detections */
          risks.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-emerald-400">
              <span className="text-2xl mb-2">✓</span>
              <p className="text-sm">All workers compliant</p>
            </div>
          ) : (
            <ul className="space-y-2">
              {risks.map((r, i) => (
                <li
                  key={i}
                  className={`flex items-center justify-between p-2 rounded border ${
                    ['fire', 'smoke'].includes(r.label.toLowerCase())
                      ? 'bg-red-900/30 border-red-800 text-red-300'
                      : 'bg-orange-900/30 border-orange-800 text-orange-300'
                  }`}
                >
                  <span className="font-medium text-sm">{getStatusText(r.label)}</span>
                  <span className="text-xs opacity-70">{Math.round(r.confidence * 100)}%</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Quick Stats Footer (Optional but nice) */}
        {stats && scenario !== 'live' && (
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
            <p className="text-xs text-slate-500 mb-2">Session Summary</p>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-slate-300">
                Total Workers: <span className="font-bold text-white">{stats.totalWorkers}</span>
              </div>
              <div className="text-slate-300">
                Compliant:{' '}
                <span className="font-bold text-emerald-400">{stats.compliantWorkers}</span>
              </div>
              <div className="text-slate-300">
                Violations: <span className="font-bold text-red-400">{stats.ppeViolations}</span>
              </div>
              <div className="text-slate-300">
                Hazards:{' '}
                <span className="font-bold text-orange-400">
                  {stats.fireIncidents + stats.smokeIncidents}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
