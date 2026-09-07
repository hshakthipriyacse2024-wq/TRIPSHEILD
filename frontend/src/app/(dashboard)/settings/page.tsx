'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/auth-store';
import { preferencesApi } from '@/services/api';
import { Settings as SettingsIcon, Save, User, Sliders, CheckCircle, Shield } from 'lucide-react';

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'preferences' | 'profile'>('preferences');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const [prefs, setPrefs] = useState({
    budget_priority: 50,
    speed_priority: 80,
    comfort_priority: 70,
    minimal_changes_priority: 60,
    preferred_airlines: 'Air India, IndiGo, Air France, Vistara',
    max_connections: 2,
    preferred_hotel_category: '4-Star Luxury',
  });

  const [profile, setProfile] = useState({
    full_name: user?.full_name || 'Harini Seenivasan',
    email: user?.email || 'harini@gmail.com',
    phone: user?.phone || '+91-9876543210',
  });

  useEffect(() => {
    preferencesApi.get().then(res => {
      if (res.data) {
        setPrefs({
          budget_priority: res.data.budget_priority ?? 50,
          speed_priority: res.data.speed_priority ?? 80,
          comfort_priority: res.data.comfort_priority ?? 70,
          minimal_changes_priority: res.data.minimal_changes_priority ?? 60,
          preferred_airlines: Array.isArray(res.data.preferred_airlines)
            ? res.data.preferred_airlines.join(', ')
            : 'Air India, IndiGo, Air France, Vistara',
          max_connections: res.data.max_connections ?? 2,
          preferred_hotel_category: res.data.preferred_hotel_category || '4-Star Luxury',
        });
      }
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleSavePreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      await preferencesApi.update({
        budget_priority: prefs.budget_priority,
        speed_priority: prefs.speed_priority,
        comfort_priority: prefs.comfort_priority,
        minimal_changes_priority: prefs.minimal_changes_priority,
        preferred_airlines: prefs.preferred_airlines.split(',').map(s => s.trim()).filter(Boolean),
        max_connections: prefs.max_connections,
        preferred_hotel_category: prefs.preferred_hotel_category,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      alert('Failed to update preferences');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <SettingsIcon className="h-7 w-7 text-indigo-600" /> Account & Recovery Settings
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Configure your traveler priorities to weight AI recovery strategy generation.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('preferences')}
          className={`py-3 px-5 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'preferences'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Sliders className="h-4 w-4" /> Traveler Priorities & AI Scoring
        </button>
        <button
          onClick={() => setActiveTab('profile')}
          className={`py-3 px-5 text-sm font-semibold border-b-2 transition flex items-center gap-2 ${
            activeTab === 'profile'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <User className="h-4 w-4" /> Profile Info
        </button>
      </div>

      {saved && (
        <div className="bg-emerald-50 border-l-4 border-emerald-600 p-4 rounded-r-lg flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-emerald-600" />
          <p className="text-sm font-semibold text-emerald-900">
            Traveler preferences saved! Recovery Optimizer will apply these weights to future disruption scoring.
          </p>
        </div>
      )}

      {/* Tab 1: Traveler Preferences */}
      {activeTab === 'preferences' && (
        <form onSubmit={handleSavePreferences} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-6">
          <div className="space-y-4">
            <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Shield className="h-5 w-5 text-indigo-600" /> Recovery Scoring Priority Weights
            </h3>
            <p className="text-xs text-gray-500">
              TripShield Recovery Engine uses these sliders to score and rank alternative options when disruptions occur.
            </p>

            {/* Slider 1: Speed */}
            <div className="bg-gray-50 p-4 rounded-lg border space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-gray-900">Speed / Arrival Priority</span>
                <span className="font-bold text-indigo-600">{prefs.speed_priority}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={prefs.speed_priority}
                onChange={e => setPrefs({...prefs, speed_priority: parseInt(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <p className="text-xs text-gray-500">Higher priority favors faster rebookings to minimize arrival delays.</p>
            </div>

            {/* Slider 2: Comfort */}
            <div className="bg-gray-50 p-4 rounded-lg border space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-gray-900">Comfort Priority</span>
                <span className="font-bold text-indigo-600">{prefs.comfort_priority}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={prefs.comfort_priority}
                onChange={e => setPrefs({...prefs, comfort_priority: parseInt(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <p className="text-xs text-gray-500">Favors premium airlines, direct transfers, and luxury hotel categories.</p>
            </div>

            {/* Slider 3: Minimal Changes */}
            <div className="bg-gray-50 p-4 rounded-lg border space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-gray-900">Minimal Changes Priority</span>
                <span className="font-bold text-indigo-600">{prefs.minimal_changes_priority}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={prefs.minimal_changes_priority}
                onChange={e => setPrefs({...prefs, minimal_changes_priority: parseInt(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <p className="text-xs text-gray-500">Favors changing only the disrupted leg rather than re-routing downstream connections.</p>
            </div>

            {/* Slider 4: Budget */}
            <div className="bg-gray-50 p-4 rounded-lg border space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="font-semibold text-gray-900">Budget Priority</span>
                <span className="font-bold text-indigo-600">{prefs.budget_priority}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={prefs.budget_priority}
                onChange={e => setPrefs({...prefs, budget_priority: parseInt(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <p className="text-xs text-gray-500">Favors cheapest rebooking options and low-cost alternative carriers.</p>
            </div>
          </div>

          <div className="pt-4 border-t space-y-4">
            <h3 className="text-base font-bold text-gray-900">Travel Preferences</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Preferred Airlines (Comma separated)</label>
                <input
                  type="text"
                  value={prefs.preferred_airlines}
                  onChange={e => setPrefs({...prefs, preferred_airlines: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Preferred Hotel Category</label>
                <select
                  value={prefs.preferred_hotel_category}
                  onChange={e => setPrefs({...prefs, preferred_hotel_category: e.target.value})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                >
                  <option value="5-Star Luxury">5-Star Luxury</option>
                  <option value="4-Star Luxury">4-Star Luxury</option>
                  <option value="3-Star Standard">3-Star Standard</option>
                  <option value="Boutique Hotel">Boutique Hotel</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Maximum Connections</label>
                <input
                  type="number"
                  min="0"
                  max="4"
                  value={prefs.max_connections}
                  onChange={e => setPrefs({...prefs, max_connections: parseInt(e.target.value) || 1})}
                  className="mt-1 block w-full border border-gray-300 rounded-lg py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                />
              </div>
            </div>
          </div>

          <div className="pt-4 border-t flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm rounded-lg shadow-sm transition flex items-center gap-2 disabled:opacity-50"
            >
              <Save className="h-4 w-4" /> {saving ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </form>
      )}

      {/* Tab 2: Profile */}
      {activeTab === 'profile' && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
          <h3 className="text-base font-bold text-gray-900">Profile Information</h3>
          <div className="space-y-4 max-w-md">
            <div>
              <label className="block text-sm font-medium text-gray-700">Full Name</label>
              <input
                type="text"
                disabled
                value={profile.full_name}
                className="mt-1 block w-full border border-gray-200 bg-gray-50 rounded-lg py-2 px-3 text-sm text-gray-700"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email Address</label>
              <input
                type="email"
                disabled
                value={profile.email}
                className="mt-1 block w-full border border-gray-200 bg-gray-50 rounded-lg py-2 px-3 text-sm text-gray-700"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Phone Number</label>
              <input
                type="text"
                disabled
                value={profile.phone}
                className="mt-1 block w-full border border-gray-200 bg-gray-50 rounded-lg py-2 px-3 text-sm text-gray-700"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Role</label>
              <span className="inline-block mt-1 px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs font-semibold">
                {user?.role?.toUpperCase() || 'TRAVELER'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
