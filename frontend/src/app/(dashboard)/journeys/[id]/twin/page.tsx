'use client';

import { useEffect, useState, useMemo } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ReactFlow, Background, Controls, MiniMap, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useJourneyStore } from '@/store/journey-store';
import { digitalTwinApi } from '@/services/api';
import { nodeTypeIcons, statusColors } from '@/lib/utils';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

const getStatusColor = (status: string) => {
  switch(status) {
    case 'confirmed': return '#10b981'; // emerald-500
    case 'at_risk': return '#f59e0b'; // amber-500
    case 'affected': return '#ef4444'; // red-500
    case 'recovered': return '#3b82f6'; // blue-500
    case 'cancelled': return '#6b7280'; // gray-500
    default: return '#9ca3af';
  }
};

export default function DigitalTwinPage() {
  const params = useParams();
  const journeyId = params.id as string;
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    digitalTwinApi.get(journeyId).then(res => {
      const data = res.data;
      
      const flowNodes: Node[] = data.nodes.map((node: any, idx: number) => ({
        id: node.id,
        position: { x: 250, y: idx * 150 }, // simple vertical layout
        data: {
          label: (
            <div className="flex flex-col items-center">
              <span className="text-2xl">{nodeTypeIcons[node.type] || '📦'}</span>
              <span className="font-bold text-sm mt-1">{node.provider}</span>
              <span className="text-xs">{new Date(node.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
          )
        },
        style: {
          background: '#fff',
          border: `2px solid ${getStatusColor(node.status)}`,
          borderRadius: '8px',
          padding: '10px',
          width: 150,
        }
      }));

      const flowEdges: Edge[] = data.dependencies.map((dep: any) => ({
        id: dep.id,
        source: dep.source_node_id,
        target: dep.target_node_id,
        label: dep.relationship_type,
        animated: dep.is_critical,
        style: { stroke: dep.is_critical ? '#ef4444' : '#9ca3af' },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    }).catch(console.error);
  }, [journeyId]);

  return (
    <div className="h-[calc(100vh-10rem)] w-full flex flex-col border border-gray-200 rounded-lg overflow-hidden bg-white">
      <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <div className="flex items-center">
          <Link href={`/journeys/${journeyId}`} className="mr-4 text-gray-500 hover:text-gray-900">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h2 className="text-lg font-bold text-gray-900">Digital Twin Visualization</h2>
        </div>
        <div className="flex space-x-4 text-xs font-medium">
          <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-emerald-500 mr-1"></span>Confirmed</div>
          <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-amber-500 mr-1"></span>At Risk</div>
          <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-red-500 mr-1"></span>Affected</div>
        </div>
      </div>
      <div className="flex-1 relative">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  );
}
