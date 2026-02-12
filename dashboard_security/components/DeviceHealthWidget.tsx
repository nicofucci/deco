
import React from 'react';
import { AgentStatus } from '../lib/api/fleet'; // Path might need adjustment depending on where component is
import { Server, CheckCircle, AlertTriangle, AlertOctagon } from 'lucide-react';

interface DeviceHealthWidgetProps {
    agents: AgentStatus[];
}

export const DeviceHealthWidget: React.FC<DeviceHealthWidgetProps> = ({ agents }) => {
    const total = agents.length;
    const critical = agents.filter(a => a.health_state === 'critical' || a.health_state === 'unknown').length;
    const warning = agents.filter(a => a.health_state === 'warning').length;
    const healthy = agents.filter(a => a.health_state === 'healthy').length;

    let statusColor = "green";
    let statusText = "Todos los sistemas operativos";
    let StatusIcon = CheckCircle;

    if (critical > 0) {
        statusColor = "red";
        statusText = "Atención requerida en dispositivos";
        StatusIcon = AlertOctagon;
    } else if (warning > 0) {
        statusColor = "yellow";
        statusText = "Advertencias de rendimiento detectadas";
        StatusIcon = AlertTriangle;
    }

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between h-full">
            <div>
                <h3 className="text-slate-500 text-sm font-medium uppercase tracking-wider mb-2 flex items-center gap-2">
                    <Server size={18} className="text-slate-400" /> Salud de Equipos
                </h3>
                <div className="mt-4 flex items-center gap-4">
                    <div className={`p-3 rounded-full ${statusColor === 'green' ? 'bg-green-100 text-green-600' :
                            statusColor === 'yellow' ? 'bg-yellow-100 text-yellow-600' :
                                'bg-red-100 text-red-600'
                        }`}>
                        <StatusIcon size={32} />
                    </div>
                    <div>
                        <div className={`text-xl font-bold ${statusColor === 'green' ? 'text-green-700' :
                                statusColor === 'yellow' ? 'text-yellow-700' :
                                    'text-red-700'
                            }`}>
                            {statusColor === 'green' ? 'Saludable' : statusColor === 'yellow' ? 'Advertencia' : 'Crítico'}
                        </div>
                        <p className="text-sm text-slate-500">{statusText}</p>
                    </div>
                </div>
            </div>

            <div className="mt-6 grid grid-cols-3 gap-2 border-t border-slate-100 pt-4">
                <div className="text-center">
                    <div className="text-lg font-bold text-slate-800">{healthy}</div>
                    <div className="text-xs text-slate-400">Ok</div>
                </div>
                <div className="text-center">
                    <div className="text-lg font-bold text-slate-800">{warning}</div>
                    <div className="text-xs text-slate-400">Warn</div>
                </div>
                <div className="text-center">
                    <div className="text-lg font-bold text-slate-800">{critical}</div>
                    <div className="text-xs text-slate-400">Crit</div>
                </div>
            </div>
        </div>
    );
};
