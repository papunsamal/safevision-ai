import axios from 'axios';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const http = axios.create({ baseURL: API, timeout: 60000 });

// FIX: Removed all redundant DEMO data from frontend
// Now only fetches from backend, backend handles DEMO fallback

export const getStats = async mode => {
  try {
    const r = await http.get('/api/stats');
    return r.data;
  } catch (err) {
    console.error('Failed to fetch stats:', err);
    return null;
  }
};

export const getWorkers = async mode => {
  try {
    const r = await http.get('/api/workers');
    return r.data;
  } catch (err) {
    console.error('Failed to fetch workers:', err);
    return [];
  }
};

export const getAlerts = async mode => {
  try {
    const r = await http.get('/api/alerts');
    return r.data;
  } catch (err) {
    console.error('Failed to fetch alerts:', err);
    return [];
  }
};

export const getReports = async mode => {
  try {
    const r = await http.get('/api/reports');
    return r.data;
  } catch (err) {
    console.error('Failed to fetch reports:', err);
    return null;
  }
};

export const getDetections = async (mode, scenario) => {
  try {
    const r = await http.get(`/api/detections?video=${scenario}&mode=${mode}`);
    return r.data;
  } catch (err) {
    console.error('Failed to fetch detections:', err);
    return [];
  }
};
