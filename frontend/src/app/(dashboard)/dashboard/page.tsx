'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/auth-store';
import { useJourneyStore } from '@/store/journey-store';
import { demoApi, analyticsApi } from '@/services/api';
import { Map, AlertTriangle, CheckCircle, Shield, Play, ArrowRight, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Link from 'next/link';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { loadDemoJourney } = useJourneyStore();
  const [stats, setStats] = useState<any>(null);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [demoMessage, setDemoMessage] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      const res = await analyticsApi.getDashboard();
      setStats(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleLoadDemo = async () => {
    setLoadingAction('load');
    setDemoMessage(null);
    try {
      await loadDemoJourney();
      const res = await analyticsApi.getDashboard();
      setStats(res.data);
      setDemoMessage('🌍 Demo Journey Loaded! "Chennai → Delhi → Paris Adventure" is active with 10 components and 9 dependencies.');
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Failed to load demo journey');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleSimulateDelay = async () => {
    setLoadingAction('delay');
    setDemoMessage(null);
    try {
      const res = await demoApi.simulateDelay();
      // Instantly update metric cards state
      setStats((prev: any) => ({
        ...prev,
        active_journeys: prev?.active_journeys || 1,
        active_disruptions: (prev?.active_disruptions || 0) + 1,
        avg_resilience_score: Math.max(35, (prev?.avg_resilience_score || 78) - 25),
        recent_alerts: [
          {
            id: res.data.disruption_id || String(Date.now()),
            title: "⚠️ Flight Delay Detected!",
            message: res.data.description || "Flight AI-542 delayed by 4 hours",
            priority: "critical"
          },
          ...(prev?.recent_alerts || [])
        ]
      }));
      // Re-sync with backend
      setTimeout(fetchStats, 500);
      setDemoMessage(`⚠️ 4-Hour Delay Simulated! Flight AI-542 delayed. Impact Score: ${res.data.impact?.impact_score || 72}/100. 4 downstream bookings affected.`);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Simulation failed. Click "Load Demo Journey" first.');
    } finally {
      setLoadingAction(null);
    }
  };

  const handleSimulateCancellation = async () => {
    setLoadingAction('cancel');
    setDemoMessage(null);
    try {
      const res = await demoApi.simulateCancellation();
      // Instantly update metric cards state
      setStats((prev: any) => ({
        ...prev,
        active_journeys: prev?.active_journeys || 1,
        active_disruptions: (prev?.active_disruptions || 0) + 1,
        avg_resilience_score: 25,
        recent_alerts: [
          {
            id: res.data.disruption_id || String(Date.now()),
            title: "🚨 Flight CANCELLED!",
            message: res.data.description || "Flight AI-542 has been cancelled",
            priority: "critical"
          },
          ...(prev?.recent_alerts || [])
        ]
      }));
      // Re-sync with backend
      setTimeout(fetchStats, 500);
      setDemoMessage(`🚨 Flight Cancellation Simulated! Impact Score: ${res.data.impact_score || 100}/100. Recovery options generated.`);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Simulation failed. Click "Load Demo Journey" first.');
    } finally {
      setLoadingAction(null);
    }
  };

  const mockChartData = [
    { name: 'Mon', disruptions: 1 },
    { name: 'Tue', disruptions: 3 },
    { name: 'Wed', disruptions: 2 },
    { name: 'Thu', disruptions: 5 },
    { name: 'Fri', disruptions: 4 },
    { name: 'Sat', disruptions: 1 },
    { name: 'Sun', disruptions: 2 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Welcome back, {user?.full_name || 'Traveler'}</h2>
        <p className="text-gray-600">Here is what's happening with your journeys today.</p>
      </div>

      {/* Demo Feedback Banner */}
      {demoMessage && (
        <div className="bg-indigo-50 border-l-4 border-indigo-600 p-4 rounded-r-lg flex items-center justify-between shadow-sm">
          <p className="text-sm font-semibold text-indigo-900">{demoMessage}</p>
          <div className="flex gap-2">
            <Link
              href="/recovery"
              className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded bg-indigo-600 text-white hover:bg-indigo-700 transition"
            >
              View Recovery Options <ArrowRight className="ml-1 h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 p-5 flex items-center">
          <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3"><Map className="h-6 w-6 text-blue-600" /></div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">Active Journeys</dt>
            <dd className="text-2xl font-bold text-gray-900">{stats?.active_journeys ?? 1}</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 p-5 flex items-center">
          <div className="flex-shrink-0 bg-red-100 rounded-lg p-3"><AlertTriangle className="h-6 w-6 text-red-600" /></div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">Active Disruptions</dt>
            <dd className="text-2xl font-bold text-red-600">{stats?.active_disruptions ?? 0}</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 p-5 flex items-center">
          <div className="flex-shrink-0 bg-emerald-100 rounded-lg p-3"><CheckCircle className="h-6 w-6 text-emerald-600" /></div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">Recoveries Completed</dt>
            <dd className="text-2xl font-bold text-gray-900">{stats?.recoveries_completed ?? 0}</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 p-5 flex items-center">
          <div className="flex-shrink-0 bg-indigo-100 rounded-lg p-3"><Shield className="h-6 w-6 text-indigo-600" /></div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">Avg Resilience Score</dt>
            <dd className="text-2xl font-bold text-indigo-600">{stats?.avg_resilience_score ?? 78} / 100</dd>
          </div>
        </div>
      </div>

      {/* Quick Actions for Hackathon */}
      <div className="bg-white shadow-sm rounded-xl p-6 border border-indigo-100 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900">One-Click Demo Controls</h3>
            <p className="text-xs text-gray-500">Trigger deterministic scenarios for hackathon evaluation.</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-indigo-100 text-indigo-800 rounded-full">Interactive Demo</span>
        </div>

        <div className="flex flex-wrap gap-3 pt-2">
          <button
            onClick={handleLoadDemo}
            disabled={loadingAction === 'load'}
            className="inline-flex items-center px-4 py-2.5 shadow-sm text-sm font-semibold rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 transition disabled:opacity-50"
          >
            {loadingAction === 'load' ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Play className="-ml-0.5 mr-2 h-4 w-4" />}
            1. Load Demo Journey
          </button>

          <button
            onClick={handleSimulateDelay}
            disabled={loadingAction === 'delay'}
            className="inline-flex items-center px-4 py-2.5 shadow-sm text-sm font-semibold rounded-lg text-white bg-amber-600 hover:bg-amber-700 transition disabled:opacity-50"
          >
            {loadingAction === 'delay' ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <AlertTriangle className="-ml-0.5 mr-2 h-4 w-4" />}
            2. Simulate 4-Hour Delay
          </button>

          <button
            onClick={handleSimulateCancellation}
            disabled={loadingAction === 'cancel'}
            className="inline-flex items-center px-4 py-2.5 shadow-sm text-sm font-semibold rounded-lg text-white bg-red-600 hover:bg-red-700 transition disabled:opacity-50"
          >
            {loadingAction === 'cancel' ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <AlertTriangle className="-ml-0.5 mr-2 h-4 w-4" />}
            Simulate Cancellation
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow-sm rounded-xl p-6 border border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Disruptions Over Time</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="disruptions" fill="#4f46e5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white shadow-sm rounded-xl p-6 border border-gray-100">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Recent System Alerts</h3>
          <div className="space-y-3">
            {stats?.recent_alerts?.length > 0 ? (
              stats.recent_alerts.map((alert: any, idx: number) => (
                <div key={alert.id || idx} className="p-3.5 bg-amber-50/50 rounded-lg border border-amber-100 flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{alert.title}</p>
                    <p className="text-xs text-gray-600 mt-0.5">{alert.message}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-100 text-center text-sm text-gray-500">
                Click "1. Load Demo Journey" to start monitoring system alerts.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
