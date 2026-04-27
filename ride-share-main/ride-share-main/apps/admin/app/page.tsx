'use client';

import { useEffect, useState } from 'react';
import { SharedButton } from '@repo/ui/button';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3005/api';

export default function AppDashboard() {
  const [stats, setStats] = useState([]);
  const APP_NAME = 'Admin App';

  const fetchStats = async () => {
    const res = await fetch(`${API_URL}/clicks`);
    setStats(await res.json());
  };

  useEffect(() => { fetchStats(); }, []);

  const handleClick = async () => {
    alert(`Clicked from ${APP_NAME}!`)
    await fetch(`${API_URL}/clicks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ appName: APP_NAME }),
    });
    fetchStats();
  };

  return (
    <div className="p-8 max-w-2xl mx-auto font-sans">
      <h1 className="text-2xl font-bold mb-6">{APP_NAME} Dashboard</h1>

      <div className="mb-8">
        <SharedButton appName={APP_NAME} onClick={handleClick}>
          Trigger Central Action
        </SharedButton>
      </div>

      <div className="border p-4 rounded-md bg-gray-50 text-gray-900">
        <h2 className="text-lg font-semibold mb-4">System-Wide Telemetry</h2>
        <ul>
          {stats.map((stat: any) => (
            <li key={stat.appName} className="flex justify-between py-2 border-b last:border-0">
              <span>{stat.appName}</span>
              <span className="font-mono">{stat.clicks} clicks</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}