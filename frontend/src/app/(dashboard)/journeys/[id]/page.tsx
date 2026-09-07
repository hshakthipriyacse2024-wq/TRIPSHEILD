'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useJourneyStore } from '@/store/journey-store';
import { formatDateTime, statusColors, nodeTypeIcons, cn } from '@/lib/utils';
import { Network } from 'lucide-react';

export default function JourneyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { currentJourney, fetchJourney, loading } = useJourneyStore();
  const [activeTab, setActiveTab] = useState('timeline');

  useEffect(() => {
    if (params.id) {
      fetchJourney(params.id as string);
    }
  }, [params.id, fetchJourney]);

  if (loading || !currentJourney) return <div>Loading...</div>;

  const sortedNodes = [...(currentJourney.nodes || [])].sort((a, b) => a.sequence_order - b.sequence_order);

  return (
    <div className="space-y-6">
      <div className={cn("p-4 rounded-lg flex justify-between items-center", statusColors[currentJourney.status] || 'bg-gray-100')}>
        <div>
          <h2 className="text-xl font-bold">{currentJourney.title}</h2>
          <p className="text-sm opacity-80">{currentJourney.origin} &rarr; {currentJourney.destination}</p>
        </div>
        <div className="flex space-x-4">
          <Link href={`/journeys/${currentJourney.id}/twin`} className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md bg-white text-gray-900 hover:bg-gray-50">
            <Network className="-ml-1 mr-2 h-5 w-5 text-indigo-600" /> View Digital Twin
          </Link>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            {['timeline', 'overview', 'dependencies'].map((tab) => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                className={cn(
                  activeTab === tab ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize'
                )}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
        <div className="p-6">
          {activeTab === 'timeline' && (
            <div className="space-y-8">
              {sortedNodes.map((node, idx) => (
                <div key={node.id} className="relative flex space-x-4">
                  {idx !== sortedNodes.length - 1 && <span className="absolute top-8 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />}
                  <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 ring-8 ring-white text-lg">
                    {nodeTypeIcons[node.type] || '📦'}
                  </div>
                  <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                    <div>
                      <p className="text-sm text-gray-500">
                        <span className="font-medium text-gray-900">{node.provider}</span> {node.type}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{node.location} &rarr; {node.destination_location || 'N/A'}</p>
                    </div>
                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                      <time dateTime={node.start_time}>{formatDateTime(node.start_time)}</time>
                      <div className="mt-1">
                        <span className={cn('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', statusColors[node.status] || 'bg-gray-100')}>
                          {node.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          {activeTab === 'overview' && (
            <div className="space-y-4 text-sm text-gray-700">
              <p><strong>Description:</strong> {currentJourney.description}</p>
              <p><strong>Resilience Score:</strong> {currentJourney.resilience_score ?? 'N/A'}</p>
            </div>
          )}
          {activeTab === 'dependencies' && (
            <div className="space-y-2">
              {currentJourney.dependencies?.map((dep) => (
                <div key={dep.id} className="p-3 bg-gray-50 rounded border">
                  {dep.relationship_type} | Buffer: {dep.buffer_minutes} min | Critical: {dep.is_critical ? 'Yes' : 'No'}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
