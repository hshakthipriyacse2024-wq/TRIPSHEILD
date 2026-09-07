'use client';

import { useState, useEffect } from 'react';
import { journeyApi, simulatorApi } from '@/services/api';
import { formatCurrency } from '@/lib/utils';
import { AlertTriangle, CheckCircle, Shield, FlaskConical, ArrowRight } from 'lucide-react';

export default function SimulatorPage() {
  const [journeys, setJourneys] = useState<any[]>([]);
  const [form, setForm] = useState({ journey_id: '', disruption_type: 'flight_delay', delay_minutes: 120 });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    journeyApi.list().then(res => {
      setJourneys(res.data);
      if (res.data.length > 0) setForm(f => ({ ...f, journey_id: res.data[0].id }));
    }).catch(console.error);
  }, []);

  const handleSimulate = async () => {
    if (!form.journey_id) {
      alert('Please load or select a journey first (e.g. click "Load Demo Journey" on Dashboard).');
      return;
    }
    setLoading(true);
    setApplied(false);
    try {
      const res = await simulatorApi.simulate(form.journey_id, {
        disruption_type: form.disruption_type,
        parameters: { delay_minutes: form.delay_minutes }
      });
      setResult(res.data);
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Simulation failed. Ensure a journey with components is loaded.');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!result?.simulation_id) return;
    try {
      await simulatorApi.apply(result.simulation_id);
      setApplied(true);
    } catch (e) {
      alert('Failed to apply simulation');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <FlaskConical className="h-7 w-7 text-indigo-600" /> What-If Simulator
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Simulate hypothetical travel disruptions non-destructively before they happen.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 col-span-1 space-y-4">
          <h3 className="text-base font-semibold text-gray-900 border-b pb-2">Simulation Parameters</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Select Journey</label>
            <select
              className="mt-1 block w-full border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.journey_id}
              onChange={e => setForm({...form, journey_id: e.target.value})}
            >
              {journeys.length === 0 && <option value="">No journeys found (load demo journey first)</option>}
              {journeys.map(j => <option key={j.id} value={j.id}>{j.title}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Disruption Type</label>
            <select
              className="mt-1 block w-full border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.disruption_type}
              onChange={e => setForm({...form, disruption_type: e.target.value})}
            >
              <option value="flight_delay">Flight Delay</option>
              <option value="flight_cancellation">Flight Cancellation</option>
              <option value="train_delay">Train Delay</option>
              <option value="missed_connection">Missed Connection</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Delay Duration (minutes)</label>
            <input
              type="number"
              min="15"
              max="720"
              step="15"
              className="mt-1 block w-full border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={form.delay_minutes}
              onChange={e => setForm({...form, delay_minutes: parseInt(e.target.value) || 60})}
            />
          </div>

          <button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 px-4 rounded-lg shadow-sm transition flex items-center justify-center gap-2"
          >
            {loading ? 'Calculating Impact...' : 'Run Simulation'}
          </button>
        </div>

        {/* Results Panel */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 col-span-2">
          <h3 className="text-base font-semibold text-gray-900 border-b pb-2 mb-4">Simulation Results</h3>
          
          {result ? (
            <div className="space-y-6">
              {/* Resilience Score Change */}
              <div className="bg-indigo-50/50 p-4 rounded-lg border border-indigo-100 flex items-center justify-between">
                <div>
                  <span className="text-xs uppercase tracking-wider text-indigo-700 font-semibold">Resilience Score Impact</span>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-2xl font-bold text-gray-400 line-through">{result.resilience_score_before}</span>
                    <ArrowRight className="h-5 w-5 text-gray-400" />
                    <span className="text-3xl font-extrabold text-amber-600">{result.resilience_score_after} / 100</span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">
                    {result.impact?.severity_class?.toUpperCase() || 'MODERATE'} SEVERITY
                  </span>
                </div>
              </div>

              {/* Impact Breakdown Metrics */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg border">
                  <div className="text-xs text-gray-500">Impact Score</div>
                  <div className="text-xl font-bold text-red-600 mt-1">{result.impact?.impact_score} / 100</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg border">
                  <div className="text-xs text-gray-500">Affected Components</div>
                  <div className="text-xl font-bold text-gray-900 mt-1">{result.impact?.nodes_affected} Nodes</div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg border">
                  <div className="text-xs text-gray-500">Financial Exposure</div>
                  <div className="text-xl font-bold text-indigo-600 mt-1">{formatCurrency(result.impact?.financial_exposure || 0)}</div>
                </div>
              </div>

              {/* Generated Recovery Options Preview */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-2">Simulated Recovery Options ({result.recovery_options?.length || 0})</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {result.recovery_options?.map((opt: any, idx: number) => (
                    <div key={idx} className="p-3 border rounded-lg flex items-center justify-between text-sm hover:bg-gray-50">
                      <div>
                        <span className="font-semibold text-gray-900">{opt.title}</span>
                        <p className="text-xs text-gray-500 line-clamp-1">{opt.description}</p>
                      </div>
                      <div className="text-right">
                        <span className="font-bold text-indigo-600">{opt.overall_score} pts</span>
                        <div className="text-xs text-gray-500">{opt.additional_cost > 0 ? `+${formatCurrency(opt.additional_cost)}` : 'No Extra Cost'}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Apply or Discard Action */}
              <div className="pt-2 border-t flex items-center justify-between">
                <span className="text-xs text-gray-500">This simulation has not altered your live itinerary data.</span>
                <div className="flex gap-3">
                  <button
                    onClick={() => setResult(null)}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 font-medium"
                  >
                    Discard
                  </button>
                  <button
                    onClick={handleApply}
                    disabled={applied}
                    className="px-4 py-2 text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition flex items-center gap-1.5"
                  >
                    {applied ? <><CheckCircle className="h-4 w-4" /> Applied to Live Journey</> : 'Apply Disruption to Journey'}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-64 border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center text-gray-400">
              <FlaskConical className="h-10 w-10 mb-2 opacity-50" />
              <p className="text-sm font-medium">Select parameters and click "Run Simulation" to visualize ripple effects.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
