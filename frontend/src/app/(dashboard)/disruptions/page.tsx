'use client';

import { useEffect, useState } from 'react';
import { disruptionApi, demoApi } from '@/services/api';
import { 
  AlertTriangle, Clock, Activity, RefreshCw, Network, 
  ArrowRight, ShieldAlert, Zap, Layers, AlertCircle, Bot
} from 'lucide-react';
import { cn, severityColors, formatDateTime } from '@/lib/utils';
import Link from 'next/link';

export default function DisruptionsPage() {
  const [disruptions, setDisruptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const loadDisruptions = async () => {
    try {
      setLoading(true);
      const res = await disruptionApi.list();
      setDisruptions(res.data);
    } catch (e) {
      console.error('Failed to fetch disruptions', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDisruptions();
  }, []);

  const handleSimulateDelay = async () => {
    setActionLoading('delay');
    setMessage(null);
    try {
      const res = await demoApi.simulateDelay();
      setMessage(`✅ 4-Hour Flight Delay Simulated! Impact Score: ${res.data.impact?.impact_score || 'High'}`);
      await loadDisruptions();
    } catch (e: any) {
      setMessage(`❌ Simulation Error: ${e.response?.data?.detail || e.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleSimulateCancellation = async () => {
    setActionLoading('cancellation');
    setMessage(null);
    try {
      const res = await demoApi.simulateCancellation();
      setMessage(`🚨 Flight Cancellation Simulated! Impact Score: ${res.data.impact_score || 'Critical'}`);
      await loadDisruptions();
    } catch (e: any) {
      setMessage(`❌ Simulation Error: ${e.response?.data?.detail || e.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleLoadDemo = async () => {
    setActionLoading('demo');
    setMessage(null);
    try {
      await demoApi.loadDemoJourney();
      setMessage('🌍 Demo Journey (Chennai → Delhi → Paris) loaded successfully!');
      await loadDisruptions();
    } catch (e: any) {
      setMessage(`❌ Load Error: ${e.response?.data?.detail || e.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  // Stats calculation
  const totalDisruptions = disruptions.length;
  const highSeverityCount = disruptions.filter(d => ['high', 'severe', 'critical'].includes(d.severity?.toLowerCase())).length;
  const totalFinancialExposure = disruptions.reduce((acc, d) => acc + (d.impact_analysis?.financial_exposure || 0), 0);
  const totalTimeImpactMinutes = disruptions.reduce((acc, d) => acc + (d.impact_analysis?.time_impact_minutes || d.delay_minutes || 0), 0);

  if (loading && disruptions.length === 0) {
    return (
      <div className="flex items-center justify-center py-20 text-gray-500">
        <RefreshCw className="h-6 w-6 animate-spin mr-2 text-indigo-600" />
        <span>Loading disruption intelligence...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Banner & Demo Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div>
          <h2 className="text-2xl font-extrabold text-gray-900 flex items-center gap-2">
            <AlertTriangle className="h-7 w-7 text-amber-500" />
            Disruption Control Center
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Real-time cascading ripple impact monitoring, node breakdown analysis, and direct recovery triggers.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleLoadDemo}
            disabled={actionLoading !== null}
            className="px-3.5 py-2 text-xs font-semibold rounded-lg border border-gray-200 bg-gray-50 hover:bg-gray-100 text-gray-700 transition flex items-center gap-1.5 disabled:opacity-50"
          >
            {actionLoading === 'demo' ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Layers className="w-3.5 h-3.5 text-indigo-600" />}
            Reset Demo Journey
          </button>

          <button
            onClick={handleSimulateDelay}
            disabled={actionLoading !== null}
            className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-amber-500 hover:bg-amber-600 text-white transition flex items-center gap-1.5 shadow-sm disabled:opacity-50"
          >
            {actionLoading === 'delay' ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5 text-yellow-100" />}
            Simulate 4h Flight Delay
          </button>

          <button
            onClick={handleSimulateCancellation}
            disabled={actionLoading !== null}
            className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-red-600 hover:bg-red-700 text-white transition flex items-center gap-1.5 shadow-sm disabled:opacity-50"
          >
            {actionLoading === 'cancellation' ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldAlert className="w-3.5 h-3.5 text-red-100" />}
            Simulate Cancellation
          </button>
        </div>
      </div>

      {/* Notification Toast */}
      {message && (
        <div className={`p-4 rounded-lg text-sm font-medium transition ${message.startsWith('❌') ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-emerald-50 text-emerald-800 border border-emerald-200'}`}>
          {message}
        </div>
      )}

      {/* Stats Summary Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-medium text-gray-500">Active Disruptions</p>
          <p className="text-2xl font-black text-gray-900 mt-1">{totalDisruptions}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-medium text-gray-500">Critical / High Severity</p>
          <p className="text-2xl font-black text-red-600 mt-1">{highSeverityCount}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-medium text-gray-500">Financial Risk</p>
          <p className="text-2xl font-black text-amber-600 mt-1">₹{totalFinancialExposure.toLocaleString()}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
          <p className="text-xs font-medium text-gray-500">Total Time Delay</p>
          <p className="text-2xl font-black text-indigo-600 mt-1">{Math.floor(totalTimeImpactMinutes / 60)}h {totalTimeImpactMinutes % 60}m</p>
        </div>
      </div>

      {/* Main Content List */}
      {disruptions.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100 space-y-4 max-w-lg mx-auto">
          <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
            <Activity className="h-8 w-8" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">No Active Disruptions Detected</h3>
            <p className="mt-1 text-sm text-gray-500">
              All active journey nodes are running on schedule. Click below to simulate a disruption and test the TripShield AI ripple impact engine.
            </p>
          </div>
          <div className="pt-2 flex justify-center gap-3">
            <button
              onClick={handleSimulateDelay}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg transition"
            >
              Simulate 4h Flight Delay
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {disruptions.map((d) => {
            const impactScore = d.impact_analysis?.impact_score ?? (d.severity === 'critical' ? 90 : d.severity === 'high' ? 70 : 40);
            const scoreColor = impactScore > 60 ? 'bg-red-500 text-white' : impactScore > 30 ? 'bg-amber-500 text-white' : 'bg-emerald-500 text-white';

            return (
              <div key={d.id} className="bg-white shadow-sm rounded-xl border border-gray-200 overflow-hidden hover:border-indigo-300 transition">
                {/* Disruption Header */}
                <div className="p-6 border-b border-gray-100 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-50/50">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                      <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100">
                        {d.journey_title || 'Journey Disruption'}
                      </span>
                      <h3 className="text-lg font-bold text-gray-900">
                        {d.type.replace('_', ' ').toUpperCase()}
                      </h3>
                      <span className={cn('px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wide', severityColors[d.severity] || 'bg-gray-100 text-gray-800')}>
                        {d.severity || 'Detected'}
                      </span>
                      <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-200 text-gray-700 capitalize">
                        Status: {d.status.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-gray-700 pt-1">{d.description}</p>
                  </div>

                  <div className="text-right text-xs text-gray-500 flex flex-col items-start md:items-end flex-shrink-0">
                    <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-gray-400" /> Detected:</span>
                    <span className="font-semibold text-gray-800 mt-0.5">{formatDateTime(d.detected_at)}</span>
                  </div>
                </div>

                {/* Impact Analysis Details */}
                <div className="p-6 space-y-6">
                  {d.impact_analysis ? (
                    <>
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
                            <Activity className="w-4 h-4 text-indigo-600" /> Ripple Impact Severity Analysis
                          </h4>
                          <span className={`text-xs font-bold px-2 py-0.5 rounded ${scoreColor}`}>
                            Impact Score: {impactScore} / 100 ({d.impact_analysis.severity_class?.toUpperCase()})
                          </span>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                          <div
                            className={cn('h-2.5 rounded-full transition-all duration-500', impactScore > 60 ? 'bg-red-600' : impactScore > 30 ? 'bg-amber-500' : 'bg-emerald-500')}
                            style={{ width: `${Math.min(100, Math.max(5, impactScore))}%` }}
                          />
                        </div>
                      </div>

                      {/* 4 Impact Stat Cards */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-red-50/50 p-3.5 rounded-lg border border-red-100">
                          <p className="text-xs text-red-600 font-semibold">Impact Score</p>
                          <p className="text-xl font-black text-red-700 mt-0.5">{d.impact_analysis.impact_score}/100</p>
                        </div>
                        <div className="bg-amber-50/50 p-3.5 rounded-lg border border-amber-100">
                          <p className="text-xs text-amber-700 font-semibold">Nodes Affected</p>
                          <p className="text-xl font-black text-amber-800 mt-0.5">{d.impact_analysis.nodes_affected} Component(s)</p>
                        </div>
                        <div className="bg-gray-50 p-3.5 rounded-lg border border-gray-200">
                          <p className="text-xs text-gray-600 font-semibold">Financial Exposure</p>
                          <p className="text-xl font-black text-gray-900 mt-0.5">₹{d.impact_analysis.financial_exposure.toLocaleString()}</p>
                        </div>
                        <div className="bg-indigo-50/50 p-3.5 rounded-lg border border-indigo-100">
                          <p className="text-xs text-indigo-600 font-semibold">Time Impact</p>
                          <p className="text-xl font-black text-indigo-900 mt-0.5">{d.impact_analysis.time_impact_minutes} minutes</p>
                        </div>
                      </div>

                      {/* Affected Nodes Detail Breakdown */}
                      {d.impact_analysis.affected_nodes_detail && d.impact_analysis.affected_nodes_detail.length > 0 && (
                        <div className="space-y-2 pt-2">
                          <p className="text-xs font-bold text-gray-700 uppercase tracking-wider">Cascading Affected Itinerary Nodes</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {d.impact_analysis.affected_nodes_detail.map((node: any, idx: number) => (
                              <div key={idx} className="p-2.5 bg-gray-50 border rounded-lg flex items-center justify-between text-xs">
                                <div className="flex items-center space-x-2">
                                  <AlertCircle className={cn("w-4 h-4 flex-shrink-0", node.impact_type === 'direct' ? 'text-red-500' : 'text-amber-500')} />
                                  <div>
                                    <span className="font-semibold text-gray-900">{node.provider || 'Node'} ({node.node_type || 'Component'})</span>
                                    <p className="text-gray-500 text-[11px]">{node.reason || 'Impacted by delay cascade'}</p>
                                  </div>
                                </div>
                                <span className={cn('px-2 py-0.5 rounded text-[10px] font-bold uppercase', node.impact_type === 'direct' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700')}>
                                  {node.impact_type}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-600">
                      Disruption recorded. Automated impact analysis will process downstream dependencies.
                    </div>
                  )}

                  {/* Actions Footer */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-gray-100">
                    <div className="flex items-center space-x-2">
                      <Link
                        href={`/journeys/${d.journey_id}/twin`}
                        className="inline-flex items-center px-3.5 py-2 border border-gray-300 text-xs font-semibold rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition"
                      >
                        <Network className="w-3.5 h-3.5 mr-1.5 text-indigo-600" /> Digital Twin Graph
                      </Link>

                      <Link
                        href="/guardian"
                        className="inline-flex items-center px-3.5 py-2 border border-gray-300 text-xs font-semibold rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition"
                      >
                        <Bot className="w-3.5 h-3.5 mr-1.5 text-indigo-600" /> Ask Guardian AI
                      </Link>
                    </div>

                    <Link
                      href="/recovery"
                      className="inline-flex items-center px-5 py-2.5 text-sm font-bold rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 transition shadow-sm"
                    >
                      View AI Recovery Options <ArrowRight className="w-4 h-4 ml-2" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
