"use client";

import { useCallback } from 'react';
import ReactFlow, {
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    addEdge,
    Connection,
    Edge,
    Node,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface NetworkMapProps {
    initialNodes: Node[];
    initialEdges: Edge[];
}

export default function NetworkMap({ initialNodes, initialEdges }: NetworkMapProps) {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge(params, eds)),
        [setEdges],
    );

    return (
        <div className="h-[600px] w-full bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex justify-between items-center">
                <h3 className="text-lg font-semibold text-white">Topología de Red Global</h3>
                <span className="text-xs text-slate-400">Interactivo: Arrastrar y Zoom</span>
            </div>
            <div className="h-full w-full">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                    attributionPosition="bottom-right"
                >
                    <Controls style={{ fill: '#fff' }} />
                    <MiniMap style={{ height: 120 }} zoomable pannable />
                    <Background color="#334155" gap={16} />
                </ReactFlow>
            </div>
        </div>
    );
}
