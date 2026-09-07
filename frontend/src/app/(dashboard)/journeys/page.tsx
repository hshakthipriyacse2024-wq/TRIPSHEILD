'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useJourneyStore } from '@/store/journey-store';
import { formatDateTime, statusColors } from '@/lib/utils';
import { Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function JourneysPage() {
  const { journeys, fetchJourneys, loading } = useJourneyStore();

  useEffect(() => {
    fetchJourneys();
  }, [fetchJourneys]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">My Journeys</h2>
        <Link href="/journeys/new" className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
          <Plus className="-ml-1 mr-2 h-5 w-5" /> New Journey
        </Link>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : journeys.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No journeys found. Create one or load the demo.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {journeys.map((journey) => (
            <Link key={journey.id} href={`/journeys/${journey.id}`} className="block bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 truncate">{journey.title}</h3>
                    <p className="mt-1 text-sm text-gray-500">{journey.origin} &rarr; {journey.destination}</p>
                  </div>
                  <span className={cn('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', statusColors[journey.status] || 'bg-gray-100 text-gray-800')}>
                    {journey.status.replace('_', ' ')}
                  </span>
                </div>
                <div className="mt-4">
                  <p className="text-sm text-gray-500">Dates: {new Date(journey.start_date).toLocaleDateString()} - {new Date(journey.end_date).toLocaleDateString()}</p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-sm text-gray-500">{journey.nodes?.length || 0} items</span>
                    {journey.resilience_score !== null && (
                      <span className="text-sm font-medium text-indigo-600">Score: {journey.resilience_score}</span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
