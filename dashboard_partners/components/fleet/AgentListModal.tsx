
import React from 'react';
import { AgentStatus } from '../../lib/api/fleet';
import { X, Server, Activity, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';

interface AgentListModalProps {
    isOpen: boolean;
    onClose: () => void;
    status: 'healthy' | 'warning' | 'critical' | 'unknown' | null;
    agents: AgentStatus[];
    onNavigateToAgent: (agentId: string) => void;
}

export const AgentListModal: React.FC<AgentListModalProps> = ({
    isOpen,
    onClose,
    status,
    agents,
    onNavigateToAgent
}) => {
    if (!isOpen || !status) return null;

    const filteredAgents = agents.filter(a => a.health_state === status);

    const getStatusColor = (s: string) => {
        switch (s) {
            case 'healthy': return 'text-green-500 bg-green-50 border-green-200';
            case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
            case 'critical': return 'text-red-600 bg-red-50 border-red-200';
            default: return 'text-gray-500 bg-gray-50 border-gray-200';
        }
    };

    const getStatusIcon = (s: string) => {
        switch (s) {
            case 'healthy': return <CheckCircle className="w-5 h-5 text-green-500" />;
            case 'warning': return <Activity className="w-5 h-5 text-yellow-500" />;
            case 'critical': return <AlertTriangle className="w-5 h-5 text-red-500" />;
            default: return <Server className="w-5 h-5 text-gray-400" />;
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col animate-in fade-in zoom-in duration-200">

                {/* Header */}
                <div className={`px-6 py-4 border-b flex justify-between items-center ${status === 'critical' ? 'bg-red-50/50' :
                        status === 'warning' ? 'bg-yellow-50/50' : 'bg-white'
                    }`}>
                    <div className="flex items-center gap-3">
                        {getStatusIcon(status)}
                        <div>
                            <h3 className="text-lg font-bold text-gray-900 capitalize">
                                {status === 'unknown' ? 'Unknown Status' : `${status} Agents`}
                            </h3>
                            <p className="text-sm text-gray-500">
                                Found {filteredAgents.length} agents matching this criteria
                            </p>
                        </div>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* List */}
                <div className="p-0 overflow-y-auto flex-1">
                    {filteredAgents.length === 0 ? (
                        <div className="p-12 text-center text-gray-500">
                            No agents found in this state.
                        </div>
                    ) : (
                        <table className="min-w-full divide-y divide-gray-100">
                            <thead className="bg-gray-50 sticky top-0">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent / Host</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP & Platform</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Seen</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Action</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-100">
                                {filteredAgents.map(agent => (
                                    <tr key={agent.agent_id} className="hover:bg-gray-50 transition-colors group">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="font-medium text-gray-900">{agent.hostname}</div>
                                            <div className="text-xs text-gray-500 font-mono">{agent.agent_id.substring(0, 8)}...</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-600">{agent.ip}</div>
                                            <div className="text-xs text-gray-400 capitalize">{agent.platform} v{agent.version}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {new Date(agent.last_seen).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right">
                                            <button
                                                onClick={() => onNavigateToAgent(agent.agent_id)}
                                                className="inline-flex items-center px-3 py-1.5 border border-indigo-200 text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded text-sm font-medium transition-colors"
                                            >
                                                Ver Agente <ArrowRight className="w-3 h-3 ml-1" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t bg-gray-50 rounded-b-lg flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-white border border-gray-300 rounded text-gray-700 hover:bg-gray-50 text-sm font-medium shadow-sm"
                    >
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    );
};
