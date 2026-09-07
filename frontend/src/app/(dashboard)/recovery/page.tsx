'use client';

import { useEffect, useState } from 'react';
import { disruptionApi, recoveryApi, journeyApi } from '@/services/api';
import { Check, X, ShieldAlert, AlertTriangle, ArrowRight, RefreshCw } from 'lucide-react';
import Link from 'next/link';

export default function RecoveryPage() {
  const [activeDisruption, setActiveDisruption] = useState<any>(null);
  const [options, setOptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [executed, setExecuted] = useState(false);

  useEffect(() => {
    const loadDisruptionAndOptions = async () => {
      try {
        const dRes = await disruptionApi.list();
        const disruptions = dRes.data;
        
        // Find latest disruption (status: detected, analyzing, recovery_generated, etc.)
        const latest = disruptions.length > 0 ? disruptions[0] : null;

        if (latest) {
          setActiveDisruption(latest);
          try {
            const optRes = await recoveryApi.getOptions(latest.journey_id);
            setOptions(optRes.data);
          } catch (e) {
            console.error('Error fetching options', e);
          }
        }
      } catch (e) {
        console.error('Error fetching disruptions', e);
      } finally {
        setLoading(false);
      }
    };

    loadDisruptionAndOptions();
  }, []);

  const handleApproveAndExecute = async (strategyId: string) => {
    setExecuting(true);
    try {
      await recoveryApi.approve(strategyId);
      await recoveryApi.execute(strategyId);
      setExecuted(true);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Execution failed');
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading recovery options...</div>;
  }

  if (executed) {
    return (
      <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-emerald-100 max-w-2xl mx-auto space-y-4">
        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto text-emerald-600">
          <Check className="h-8 w-8" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900">Recovery Executed Successfully! 🎉</h3>
        <p className="text-gray-600 text-sm max-w-md mx-auto">
          Your travel itinerary has been rebuilt in the database. Affected components have been updated to <strong>Recovered</strong> state.
        </p>
        <div className="pt-4 flex justify-center gap-4">
          <Link
            href="/dashboard"
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!activeDisruption) {
    return (
      <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100 max-w-xl mx-auto">
        <ShieldAlert className="mx-auto h-14 w-14 text-emerald-500 mb-3" />
        <h3 className="text-lg font-bold text-gray-900">No Active Disruptions</h3>
        <p className="mt-1 text-sm text-gray-500 max-w-md mx-auto">
          Your journey components are operating normally. To test disruption recovery, click <strong>"Simulate 4-Hour Delay"</strong> on the Dashboard.
        </p>
        <Link
          href="/dashboard"
          className="mt-6 inline-flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700"
        >
          Go to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Recovery Center</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Select and approve an AI-generated recovery strategy tailored to your travel preferences.
          </p>
        </div>
      </div>

      {/* Disruption Alert Summary */}
      <div className="p-4 bg-amber-50 border-l-4 border-amber-500 rounded-r-lg flex items-start gap-3">
        <AlertTriangle className="h-6 w-6 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-bold text-amber-900">Active Disruption Detected</h4>
          <p className="text-sm text-amber-800 mt-0.5">{activeDisruption.description}</p>
        </div>
      </div>

      {/* Strategy Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {options.map((opt: any, idx: number) => (
          <div
            key={opt.id || idx}
            className={`bg-white shadow-sm rounded-xl border-2 flex flex-col justify-between transition ${
              opt.is_recommended ? 'border-indigo-600 relative ring-2 ring-indigo-100' : 'border-gray-100'
            }`}
          >
            {opt.is_recommended && (
              <span className="absolute -top-3.5 left-1/2 transform -translate-x-1/2 bg-indigo-600 text-white px-3 py-1 rounded-full text-xs font-bold shadow-sm uppercase tracking-wider">
                ★ Recommended by TripShield
              </span>
            )}

            <div className="p-6 space-y-4">
              <div>
                <h3 className="text-lg font-bold text-gray-900 line-clamp-1">{opt.title}</h3>
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">{opt.description}</p>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
                <div>
                  <p className="text-xs text-gray-500">Overall Score</p>
                  <p className="text-2xl font-black text-indigo-600">{opt.overall_score} <span className="text-xs text-gray-400 font-normal">/ 100</span></p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-gray-900">
                    {opt.additional_cost > 0 ? `+₹${opt.additional_cost}` : opt.additional_cost < 0 ? `-₹${Math.abs(opt.additional_cost)}` : '₹0 Extra'}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {opt.time_saved_minutes > 0 ? `Saved ${opt.time_saved_minutes}m` : `Lost ${Math.abs(opt.time_saved_minutes)}m`}
                  </p>
                </div>
              </div>

              <p className="text-xs text-gray-700 bg-indigo-50/60 p-3 rounded-lg border border-indigo-100 italic">
                "{opt.explanation}"
              </p>

              <div className="space-y-2 pt-1 text-xs text-gray-500">
                <div className="flex justify-between">
                  <span>Feasibility Confidence</span>
                  <span className="font-semibold text-gray-900">{Math.round((opt.feasibility_score || 0.85) * 100)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Comfort Rating</span>
                  <span className="font-semibold text-gray-900">{Math.round((opt.comfort_score || 0.75) * 100)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Itinerary Changes</span>
                  <span className="font-semibold text-gray-900">{opt.num_changes || 1} component(s)</span>
                </div>
              </div>
            </div>

            <div className="p-6 pt-0 border-t border-gray-100 mt-auto flex gap-2">
              <button
                onClick={() => handleApproveAndExecute(opt.id)}
                disabled={executing}
                className="flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 transition flex items-center justify-center gap-1.5 shadow-sm disabled:opacity-50"
              >
                {executing ? <RefreshCw className="h-4 w-4 animate-spin" /> : <><Check className="w-4 h-4" /> Approve & Execute</>}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
