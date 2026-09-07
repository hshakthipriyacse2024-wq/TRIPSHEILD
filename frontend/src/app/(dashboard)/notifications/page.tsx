'use client';

import { useEffect, useState } from 'react';
import { notificationApi } from '@/services/api';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    notificationApi.list().then(res => setNotifications(res.data)).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Notifications</h2>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {notifications.length === 0 ? (
          <div className="p-6 text-center text-gray-500">No new notifications</div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {notifications.map((n: any) => (
              <li key={n.id} className="p-4 hover:bg-gray-50">
                <p className="text-sm font-medium text-gray-900">{n.title}</p>
                <p className="text-sm text-gray-500">{n.message}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
