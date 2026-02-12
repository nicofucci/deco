
import React from 'react';
import { AgentStatus } from '../../lib/api/fleet';
import Badge from '../ui/Badge';
import { CheckCircle, AlertTriangle, XCircle, Clock } from 'lucide-react';

interface FleetAgentsTabProps {
    agents: AgentStatus[];
}

export const FleetAgentsTab: React.FC<FleetAgentsTabProps> = ({ agents }) => {
    return (
        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden mt-4">
            <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Fleet & Agents</h3>
            </div>
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hostname / IP</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform / Version</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Update Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Telemetry</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Seen</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {agents.map((agent) => (
                        <tr key={agent.agent_id}>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm font-medium text-gray-900">{agent.hostname}</div>
                                <div className="text-sm text-gray-500">{agent.ip}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-900 capitalize">{agent.platform || 'System'}</div>
                                <div className="text-sm text-gray-500">v{agent.version || '?.?.?'}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                {agent.health_state === 'healthy' && <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Healthy</Badge>}
                                {agent.health_state === 'warning' && <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Warning</Badge>}
                                {(agent.health_state === 'critical' || agent.health_state === 'unknown') && <Badge className="bg-red-100 text-red-800 hover:bg-red-100">Critical</Badge>}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {agent.last_update_status || 'Unknown'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                                CPU: {agent.cpu_usage?.toFixed(0)}% | RAM: {agent.ram_usage?.toFixed(0)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {new Date(agent.last_seen).toLocaleString()}
                            </td>
                        </tr>
                    ))}
                    {agents.length === 0 && (
                        <tr>
                            <td colSpan={6} className="px-6 py-4 text-center text-sm text-gray-500">
                                No agents connected for this client.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};
