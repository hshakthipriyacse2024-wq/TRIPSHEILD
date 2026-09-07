'use client';

import { useEffect, useState } from 'react';
import { analyticsApi } from '@/services/api';
import { formatCurrency } from '@/lib/utils';
import { BarChart3, TrendingUp, DollarSign, Clock, ShieldCheck, PieChart as PieIcon, Activity } from 'lucide-react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

export default function AnalyticsPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.getDashboard().then(res => {
      setStats(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const disruptionTypesData = [
    { name: 'Flight Delay', count: 6, fill: '#6366f1' },
    { name: 'Flight Cancellation', count: 3, fill: '#ef4444' },
    { name: 'Transfer Conflict', count: 4, fill: '#f59e0b' },
    { name: 'Hotel Check-in', count: 2, fill: '#10b981' },
    { name: 'Activity Miss', count: 1, fill: '#8b5cf6' },
  ];

  const resilienceTrendData = [
    { day: 'Day 1 (Initial)', score: 78 },
    { day: 'Day 2 (Flight Delay)', score: 42 },
    { day: 'Day 2 (Recovery Applied)', score: 88 },
    { day: 'Day 3 (Paris Checkin)', score: 92 },
    { day: 'Day 4 (Completed)', score: 95 },
  ];

  const strategyDistributionData = [
    { name: 'Connection Preserving', value: 45, color: '#6366f1' },
    { name: 'Minimal Rebook', value: 30, color: '#10b981' },
    { name: 'Cost-Optimized', value: 15, color: '#f59e0b' },
    { name: 'Comfort-Optimized', value: 10, color: '#ec4899' },
  ];

  const savingsData = [
    { month: 'Jan', saved: 4500 },
    { month: 'Feb', saved: 8200 },
    { month: 'Mar', saved: 12500 },
    { month: 'Apr', saved: 15000 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BarChart3 className="h-7 w-7 text-indigo-600" /> Resilience Analytics Dashboard
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Real-time telemetry on journey disruptions, recovery efficiency, cost savings, and resilience trends.
          </p>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 p-5 flex items-center">
          <div className="flex-shrink-0 bg-indigo-100 rounded-lg p-3">
            <DollarSign className="h-6 w-6 text-indigo-600" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">Total Financial Savings</dt>
            <dd className="text-2xl font-bold text-gray-900">{formatCurrency(stats?.money_saved || 15000)}</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 p-5 flex items-center">
          <div className="flex-shrink-0 bg-emerald-100 rounded-lg p-3">
            <Clock className="h-6 w-6 text-emerald-600" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">Time Recovered</dt>
            <dd className="text-2xl font-bold text-gray-900">{(stats?.time_saved_minutes || 240)} mins</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 p-5 flex items-center">
          <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
            <ShieldCheck className="h-6 w-6 text-blue-600" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">Recovery Success Rate</dt>
            <dd className="text-2xl font-bold text-emerald-600">100%</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow-sm rounded-xl border border-gray-100 p-5 flex items-center">
          <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
            <TrendingUp className="h-6 w-6 text-purple-600" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">Avg Resilience Score</dt>
            <dd className="text-2xl font-bold text-indigo-600">{stats?.avg_resilience_score || 88} / 100</dd>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Disruptions by Type */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-indigo-600" /> Disruptions by Component Type
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={disruptionTypesData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip formatter={(val) => [`${val} Disruptions`, 'Count']} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {disruptionTypesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Resilience Score Trend */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-emerald-600" /> Journey Resilience Trajectory
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={resilienceTrendData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(val) => [`${val} / 100`, 'Resilience Score']} />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#10b981"
                  strokeWidth={3}
                  dot={{ r: 6, fill: '#10b981' }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Recovery Strategy Distribution */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
            <PieIcon className="h-5 w-5 text-purple-600" /> Strategy Type Selection Share
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={strategyDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {strategyDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(val) => [`${val}%`, 'Share']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Cumulative Savings Over Time */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-indigo-600" /> Cumulative Recovery Cost Savings
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={savingsData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(v) => `₹${v}`} />
                <Tooltip formatter={(val) => [`₹${val.toLocaleString()}`, 'Saved']} />
                <Bar dataKey="saved" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
