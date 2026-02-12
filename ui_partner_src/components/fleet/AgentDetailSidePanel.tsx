
import React from 'react';
import { AgentStatus } from '../../lib/api/fleet';
import { X, Server, Cpu, Activity, Clock, Shield, Terminal, HardDrive } from 'lucide-react';

interface AgentDetailSidePanelProps {
    agent: AgentStatus | null;
    onClose: () => void;
}

export const AgentDetailSidePanel: React.FC<AgentDetailSidePanelProps> = ({ agent, onClose }) => {
    if (!agent) return null;

    const getStatusHeaderColor = (s: string) => {
        switch (s) {
            case 'healthy': return 'bg-green-600';
            case 'warning': return 'bg-yellow-500';
            case 'critical': return 'bg-red-600';
            default: return 'bg-gray-600';
        }
    };

    return (
        <div className="fixed inset-0 z-40 overflow-hidden">
            <div className="absolute inset-0 bg-black/30 backdrop-blur-[1px]" onClick={onClose}></div>

            <div className="absolute inset-y-0 right-0 flex max-w-full pl-10 pointer-events-none">
                <div className="w-screen max-w-md pointer-events-auto transform transition ease-in-out duration-500 sm:duration-700 translate-x-0">
                    <div className="h-full flex flex-col bg-white shadow-2xl">

                        {/* Header */}
                        <div className={`${getStatusHeaderColor(agent.health_state)} px-6 py-6 text-white`}>
                            <div className="flex items-start justify-between">
                                <div>
                                    <h2 className="text-xl font-bold flex items-center gap-2">
                                        <Server className="w-5 h-5" />
                                        {agent.hostname}
                                    </h2>
                                    <p className="opacity-90 font-mono text-sm mt-1">{agent.ip}</p>
                                </div>
                                <button onClick={onClose} className="text-white/80 hover:text-white transition-colors">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="mt-6 flex gap-4 text-sm font-medium">
                                <span className="bg-black/20 px-2 py-1 rounded capitalize flex items-center gap-1">
                                    <Activity className="w-3 h-3" /> {agent.health_state}
                                </span>
                                <span className="bg-black/20 px-2 py-1 rounded capitalize flex items-center gap-1">
                                    <Terminal className="w-3 h-3" /> {agent.platform}
                                </span>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-6">

                            {/* Vital Stats */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                                    <div className="text-xs text-gray-500 uppercase tracking-wide flex items-center gap-1 mb-1">
                                        <Cpu className="w-3 h-3" /> CPU Usage
                                    </div>
                                    <div className="text-2xl font-semibold text-gray-800">
                                        {agent.cpu_usage?.toFixed(1) || 0}%
                                    </div>
                                    <div className="w-full bg-gray-200 h-1.5 rounded-full mt-2 overflow-hidden">
                                        <div
                                            className="bg-indigo-500 h-full rounded-full"
                                            style={{ width: `${Math.min(agent.cpu_usage || 0, 100)}%` }}
                                        ></div>
                                    </div>
                                </div>
                                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                                    <div className="text-xs text-gray-500 uppercase tracking-wide flex items-center gap-1 mb-1">
                                        <HardDrive className="w-3 h-3" /> RAM Usage
                                    </div>
                                    <div className="text-2xl font-semibold text-gray-800">
                                        {agent.ram_usage?.toFixed(1) || 0}%
                                    </div>
                                    <div className="w-full bg-gray-200 h-1.5 rounded-full mt-2 overflow-hidden">
                                        <div
                                            className="bg-purple-500 h-full rounded-full"
                                            style={{ width: `${Math.min(agent.ram_usage || 0, 100)}%` }}
                                        ></div>
                                    </div>
                                </div>
                            </div>

                            {/* Info Block */}
                            <div className="space-y-4">
                                <h3 className="font-semibold text-gray-900 border-b pb-2">Information</h3>

                                <div className="grid grid-cols-2 gap-y-4 text-sm">
                                    <div>
                                        <div className="text-gray-500">Agent ID</div>
                                        <div className="font-mono text-gray-700 text-xs mt-0.5">{agent.agent_id}</div>
                                    </div>
                                    <div>
                                        <div className="text-gray-500">Version</div>
                                        <div className="text-gray-700 font-medium">v{agent.version}</div>
                                    </div>
                                    <div>
                                        <div className="text-gray-500">Last Seen</div>
                                        <div className="text-gray-700">{new Date(agent.last_seen).toLocaleString()}</div>
                                    </div>
                                    <div>
                                        <div className="text-gray-500">Update Status</div>
                                        <div className="text-gray-700">{agent.last_update_status || 'Up to date'}</div>
                                    </div>
                                </div>
                            </div>

                            {/* Job Stats */}
                            <div className="space-y-4">
                                <h3 className="font-semibold text-gray-900 border-b pb-2">Activity (24h)</h3>
                                <div className="flex gap-4">
                                    <div className="flex-1 bg-blue-50 p-3 rounded border border-blue-100">
                                        <div className="text-2xl font-bold text-blue-700">{agent.jobs_executed_24h}</div>
                                        <div className="text-xs text-blue-600">Jobs Executed</div>
                                    </div>
                                    <div className="flex-1 bg-red-50 p-3 rounded border border-red-100">
                                        <div className="text-2xl font-bold text-red-700">{agent.jobs_failed_24h}</div>
                                        <div className="text-xs text-red-600">Jobs Failed</div>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
