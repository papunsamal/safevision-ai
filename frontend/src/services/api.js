import axios from 'axios';

// Python backend (port 8000)
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Axios Instance with Timeout & Interceptors
 * - Timeout: 60s (Video inference can be slow on CPU)
 * - Headers: JSON content type
 */
const http = axios.create({
  baseURL: API,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

/* ----------------- DEMO DATA (sirf DEMO MODE ke liye, clearly labeled) ----------
 * NOTE: Yeh data hardcoded hai UI demonstration ke liye.
 * REAL MODE mein yeh KABHI use nahi hoga.
 */

const demoStats = {
  totalWorkers: 25,
  compliantWorkers: 22,
  ppeViolations: 3,
  fireIncidents: 1,
  smokeIncidents: 2,
};

const demoWorkers = [
  { id: 1, helmet: true, vest: true, gloves: true },
  { id: 2, helmet: false, vest: true }, // Violation
  { id: 3, helmet: true, vest: false }, // Info only
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

/* ----------------- FAIL-SAFE FETCH WITH SMART RETRY ----------
 * Strategy:
 * 1. If mode === 'DEMO': Return hardcoded demo data immediately.
 * 2. If mode === 'REAL': Try fetching from backend.
 *    - On Network Error/Timeout: Retry up to 2 times with exponential backoff.
 *    - On Success: Return real data.
 *    - On Final Failure: Return fallback (null/[]) WITHOUT falling back to Demo Data.
 *      This ensures "No Fake AI" policy is maintained.
 */
async function fetchOrDemo(mode, path, demoData, fallbackValue, retries = 2) {
  if (mode === 'DEMO') {
    return demoData;
  }

  let attempt = 0;
  while (attempt <= retries) {
    try {
      const response = await http.get(path);
      return response.data ?? fallbackValue;
    } catch (error) {
      attempt++;

      // Check if it's a network error or timeout worth retrying
      const isRetryable =
        !error.response || error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK';

      if (isRetryable && attempt <= retries) {
        console.warn(`Attempt ${attempt} failed for ${path}. Retrying in ${attempt * 500}ms...`);
        await new Promise(resolve => setTimeout(resolve, attempt * 500)); // Exponential backoff
        continue;
      }

      // Permanent failure or max retries reached
      console.error(`Failed to fetch ${path} after ${attempt} attempts:`, error.message);
      return fallbackValue; // Return null/[], NOT demo data
    }
  }

  return fallbackValue;
}

/* ----------------- API FUNCTIONS ----------
 * All functions now support Smart Retry in REAL mode.
 */

export const getStats = mode => fetchOrDemo(mode, `/api/stats?mode=${mode}`, demoStats, null);

export const getWorkers = mode => fetchOrDemo(mode, `/api/workers?mode=${mode}`, demoWorkers, []);

export const getAlerts = mode => fetchOrDemo(mode, `/api/alerts?mode=${mode}`, demoAlerts, []);

export const getReports = mode => fetchOrDemo(mode, `/api/reports?mode=${mode}`, demoReports, null);

/* Videos list endpoint (dynamic dropdown population) */
export const getVideos = async () => {
  try {
    const r = await http.get('/api/videos');
    return r.data || [];
  } catch (err) {
    console.error('Failed to load video list:', err);
    return [];
  }
};

/* REAL: { detections, timeline } — timeline = per-frame synced boxes
 * DEMO: static boxes (timeline null)
 * Note: Detection errors are propagated so UI can show specific error states.
 */
export const getDetections = (mode, scenario) => {
  if (mode === 'DEMO') {
    return Promise.resolve(demoDetections[scenario] || []);
  }

  // REAL mode: Do NOT catch errors silently. Let the caller handle it.
  return http
    .get(`/api/detections?video=${scenario}&mode=${mode}`)
    .then(r => r.data)
    .catch(err => {
      console.error('REAL detection failed:', err);
      throw err; // Propagate error
    });
};
