'use client';

import { useAuthStore } from '@/store/auth-store';

export default function AdminPage() {
  const { user } = useAuthStore();
  
  if (user?.role !== 'ops_admin' && user?.role !== 'sys_admin') {
    return <div className="p-6 text-red-600">Access Denied: Admin privileges required.</div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Admin Dashboard</h2>
      <div className="bg-white p-6 rounded-lg shadow text-center py-20">
        <p className="text-gray-500">Admin controls will appear here.</p>
      </div>
    </div>
  );
}
