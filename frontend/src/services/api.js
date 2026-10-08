import axios from 'axios';

// Python backend (port 8000)
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const http = axios.create({ baseURL: API, timeout: 60000 });

/* ----------------- DEMO DATA (sirf DEMO MODE ke liye, clearly labeled) ---------- */

const demoStats = {
  totalWorkers: 25,
  compliantWorkers: 22,
  ppeViolations: 3,
  fireIncidents: 1,
  smokeIncidents: 2,
};

const demoWorkers = [
  { id: 1, helmet: true, vest: true, gloves: true },
  { id: 2, helmet: false, vest: true },
  { id: 3, helmet: true, vest: false },
  { id: 4, helmet: true, vest: true },
];

const demoAlerts = [
  {
    id: 1,
    type: 'PPE',
    severity: 'HIGH',
    message: 'No Helmet Detected',
    camera: 'CAM-01',
    zone: 'Production Area',
    time: '10:41 AM',
  },
  {
    id: 2,
    type: 'FIRE',
    severity: 'CRITICAL',
    message: 'Fire Detected',
    camera: 'CAM-02',
    zone: 'Warehouse',
    time: '10:38 AM',
  },
  {
    id: 3,
    type: 'SMOKE',
    severity: 'HIGH',
    message: 'Smoke Detected',
    camera: 'CAM-03',
    zone: 'Boiler Area',
    time: '10:31 AM',
  },
];

const demoDetections = {
  compliant: [
    { label: 'person', confidence: 0.96, x: 10, y: 15, w: 22, h: 70 },
    { label: 'helmet', confidence: 0.93, x: 12, y: 15, w: 8, h: 10 },
    { label: 'vest', confidence: 0.91, x: 12, y: 35, w: 16, h: 25 },
    { label: 'person', confidence: 0.94, x: 55, y: 20, w: 22, h: 68 },
    { label: 'helmet', confidence: 0.9, x: 57, y: 20, w: 8, h: 10 },
  ],
  violation: [
    { label: 'person', confidence: 0.95, x: 15, y: 18, w: 22, h: 68 },
    { label: 'no_helmet', confidence: 0.89, x: 17, y: 18, w: 8, h: 10 },
    { label: 'person', confidence: 0.93, x: 60, y: 22, w: 20, h: 66 },
    { label: 'helmet', confidence: 0.92, x: 62, y: 22, w: 8, h: 10 },
  ],
  fire_smoke: [
    { label: 'fire', confidence: 0.91, x: 40, y: 55, w: 18, h: 25 },
    { label: 'smoke', confidence: 0.87, x: 38, y: 20, w: 26, h: 35 },
  ],
};

const demoReports = {
  complianceTrend: [
    { day: 'Mon', value: 72 },
    { day: 'Tue', value: 75 },
    { day: 'Wed', value: 71 },
    { day: 'Thu', value: 80 },
    { day: 'Fri', value: 84 },
    { day: 'Sat', value: 82 },
    { day: 'Sun', value: 88 },
  ],
  incidentTrend: [
    { day: 'Mon', ppe: 4, fire: 1, smoke: 2 },
    { day: 'Tue', ppe: 3, fire: 0, smoke: 1 },
    { day: 'Wed', ppe: 6, fire: 2, smoke: 2 },
    { day: 'Thu', ppe: 2, fire: 0, smoke: 1 },
    { day: 'Fri', ppe: 5, fire: 1, smoke: 3 },
    { day: 'Sat', ppe: 3, fire: 0, smoke: 0 },
    { day: 'Sun', ppe: 1, fire: 0, smoke: 1 },
  ],
};

/* ----------------- FAIL-SAFE FETCH ----------
 * DEMO mode  -> frontend demo data (UI mein amber "DEMO MODE" banner)
 * REAL mode  -> backend se asli data; error par KHALI (null/[]) —
 *               kabhi bhi demo data REAL mein nahi dikhta (no fake AI)
 */
async function fetchOrDemo(mode, path, demo, fallback) {
  if (mode === 'DEMO') return demo;
  try {
    const r = await http.get(path);
    return r.data ?? fallback;
  } catch {
    return fallback;
  }
}

/* ----------------- API FUNCTIONS ----------
 * mode backend ko bheja jata hai (?mode=...) taaki backend
 * REAL mein kabhi demo data return na kare.
 */

export const getStats = mode => fetchOrDemo(mode, `/api/stats?mode=${mode}`, demoStats, null);

export const getWorkers = mode => fetchOrDemo(mode, `/api/workers?mode=${mode}`, demoWorkers, []);

export const getAlerts = mode => fetchOrDemo(mode, `/api/alerts?mode=${mode}`, demoAlerts, []);

export const getReports = mode => fetchOrDemo(mode, `/api/reports?mode=${mode}`, demoReports, null);

/* Videos jo backend ke videos/ folder mein ASAL mein maujood hain
 * (frontend dropdown inhi se banta hai — 404/"video not found" fix) */
export const getVideos = async () => {
  try {
    const r = await http.get('/api/videos');
    return r.data || [];
  } catch {
    return [];
  }
};

/* REAL: { detections, timeline } — timeline = per-frame synced boxes
 * DEMO: static boxes (timeline null) */
export const getDetections = async (mode, scenario) => {
  if (mode === 'DEMO') {
    return { detections: demoDetections[scenario] || [], timeline: null };
  }
  try {
    const r = await http.get(`/api/detections?video=${scenario}&mode=${mode}`);
    return r.data;
  } catch {
    return { detections: [], timeline: null };
  }
};
