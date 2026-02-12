
import React from 'react';
import Link from 'next/link';
import { AgentStatus } from '../../lib/api/fleet';
import { Eye } from 'lucide-react';

interface AgentsTableProps {
    agents: AgentStatus[];
}

export const AgentsTable: React.FC<AgentsTableProps> = ({ agents }) => {
    return (
        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hostname / IP</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Version</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Health</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Telemetry</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Seen</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {agents.map((agent) => (
                        <tr key={agent.agent_id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm font-medium text-gray-900">{agent.hostname || 'Unknown'}</div>
                                <div className="text-sm text-gray-500">{agent.ip}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                                {agent.platform || 'windows'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {agent.version || 'N/A'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <HealthBadge status={agent.health_state} />
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                <div className="flex flex-col space-y-1">
                                    <span className={agent.cpu_usage > 90 ? "text-red-500 font-bold" : ""}>CPU: {agent.cpu_usage?.toFixed(0)}%</span>
                                    <span>RAM: {agent.ram_usage?.toFixed(0)}%</span>
                                </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {new Date(agent.last_seen).toLocaleString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <Link href={`/dashboard/fleet/${agent.agent_id}`} className="text-indigo-600 hover:text-indigo-900 flex items-center justify-end gap-1">
                                    <Eye size={16} /> Details
                                </Link>
                            </td>
                        </tr>
                    ))}
                    {agents.length === 0 && (
                        <tr>
                            <td colSpan={7} className="px-6 py-4 text-center text-sm text-gray-500">
                                No agents found in fleet.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

const HealthBadge = ({ status }: { status: string }) => {
    switch (status) {
        case 'healthy':
            return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Healthy</span>;
        case 'warning':
            return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Warning</span>;
        case 'critical':
            return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Critical</span>;
        default:
            return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">Unknown</span>;
    }
};
