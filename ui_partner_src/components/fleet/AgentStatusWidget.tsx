
import React, { useState } from 'react';
import { AgentStatus } from '../../lib/api/fleet';
import { Server, AlertTriangle } from 'lucide-react';
import { AgentListModal } from './AgentListModal';

interface AgentStatusWidgetProps {
    agents: AgentStatus[];
    onNavigateToAgent: (agentId: string) => void;
}

export const AgentStatusWidget: React.FC<AgentStatusWidgetProps> = ({ agents, onNavigateToAgent }) => {
    const total = agents.length;
    const healthy = agents.filter(a => a.health_state === 'healthy').length;
    const warning = agents.filter(a => a.health_state === 'warning').length;
    const critical = agents.filter(a => a.health_state === 'critical').length;

    const [selectedStatus, setSelectedStatus] = useState<'healthy' | 'warning' | 'critical' | null>(null);

    return (
        <>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-gray-500 text-sm font-medium uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Server size={16} /> Agent Status
                </h3>

                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <span className="text-gray-600">Active</span>
                        <span className="font-bold text-gray-900 bg-gray-100 px-2 py-0.5 rounded">{total}</span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 text-center text-xs">
                        <div
                            onClick={() => setSelectedStatus('healthy')}
                            className="bg-green-50 p-2 rounded text-green-700 font-medium cursor-pointer hover:bg-green-100 transition-colors border border-transparent hover:border-green-200"
                        >
                            {healthy} Healthy
                        </div>
                        <div
                            onClick={() => setSelectedStatus('warning')}
                            className="bg-yellow-50 p-2 rounded text-yellow-700 font-medium cursor-pointer hover:bg-yellow-100 transition-colors border border-transparent hover:border-yellow-200"
                        >
                            {warning} Warning
                        </div>
                        <div
                            onClick={() => setSelectedStatus('critical')}
                            className="bg-red-50 p-2 rounded text-red-700 font-medium cursor-pointer hover:bg-red-100 transition-colors border border-transparent hover:border-red-200"
                        >
                            {critical} Critical
                        </div>
                    </div>

                    {critical > 0 && (
                        <div
                            onClick={() => setSelectedStatus('critical')}
                            className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded border border-red-100 flex items-start gap-2 cursor-pointer hover:bg-red-100/80 transition-colors"
                        >
                            <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                            Some agents require attention.
                        </div>
                    )}
                </div>
            </div>

            <AgentListModal
                isOpen={!!selectedStatus}
                status={selectedStatus}
                onClose={() => setSelectedStatus(null)}
                agents={agents}
                onNavigateToAgent={(id) => {
                    setSelectedStatus(null);
                    onNavigateToAgent(id);
                }}
            />
        </>
    );
};
