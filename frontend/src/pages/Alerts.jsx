import { useEffect, useState } from 'react';
import AlertCard from '../components/AlertCard';
import { getAlerts } from '../services/api';

export default function Alerts({ mode }) {
  const [alerts, setAlerts] = useState([]);
  useEffect(() => {
    getAlerts(mode).then(setAlerts);
  }, [mode]);

  return (
    <div className="space-y-4">
      {alerts.length ? (
        alerts.map(a => <AlertCard key={a.id} alert={a} />)
      ) : (
        <p className="text-sm text-slate-500">Insufficient data</p>
      )}
    </div>
  );
}
