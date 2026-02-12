
import React from 'react';
import { AgentStatus } from '../../lib/api/fleet';
import { Users, AlertTriangle, Monitor, AlertOctagon, CheckCircle } from 'lucide-react';

interface FleetStatsProps {
    agents: AgentStatus[];
    alertsCount: number;
}

export const FleetStats: React.FC<FleetStatsProps> = ({ agents, alertsCount }) => {
    const total = agents.length;
    const healthy = agents.filter(a => a.health_state === 'healthy').length;
    const warning = agents.filter(a => a.health_state === 'warning').length;
    const critical = agents.filter(a => a.health_state === 'critical' || a.health_state === 'unknown').length;
    // Assuming 'outdated' if version < stable (logic might need refinement, for now simple check if status has it)
    const outdated = agents.filter(a => a.last_update_status === 'outdated').length;
    // Active offline alerts also count towards 'Critical' implicitly but let's show alerts specifically.

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
            <StatsCard title="Total Agents" value={total} icon={<Users size={20} />} color="blue" />
            <StatsCard title="Active (Healthy)" value={healthy} icon={<CheckCircle size={20} />} color="green" />
            <StatsCard title="Warning" value={warning} icon={<AlertTriangle size={20} />} color="yellow" />
            <StatsCard title="Critical/Offline" value={critical} icon={<AlertOctagon size={20} />} color="red" />
            <StatsCard title="Active Alerts" value={alertsCount} icon={<Monitor size={20} />} color="purple" />
        </div>
    );
};

const StatsCard = ({ title, value, icon, color }: { title: string, value: number, icon: any, color: string }) => {
    const colors: any = {
        blue: "bg-blue-100 text-blue-800",
        green: "bg-green-100 text-green-800",
        yellow: "bg-yellow-100 text-yellow-800",
        red: "bg-red-100 text-red-800",
        purple: "bg-purple-100 text-purple-800"
    };

    return (
        <div className={`p-4 rounded-lg shadow-sm border border-gray-100 bg-white flex items-center justify-between`}>
            <div>
                <p className="text-sm text-gray-500 font-medium">{title}</p>
                <h3 className="text-2xl font-bold mt-1 text-gray-900">{value}</h3>
            </div>
            <div className={`p-3 rounded-full ${colors[color]}`}>
                {icon}
            </div>
        </div>
    );
};
