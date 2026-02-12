
"use client";

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { FleetAPI, AgentStatus, FleetAlert } from '../../../../lib/api/fleet';
import { ArrowLeft, Cpu, HardDrive, Shield, Activity, Clock } from 'lucide-react';
import Link from 'next/link';

export default function AgentDetailPage() {
    const params = useParams();
    const agentId = params.agentId as string;

    const [status, setStatus] = useState<AgentStatus | null>(null);
    const [alerts, setAlerts] = useState<FleetAlert[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (agentId) {
            loadAgent();
        }
    }, [agentId]);

    const loadAgent = async () => {
        setLoading(true);
        try {
            const data = await FleetAPI.getAgentDetail(agentId);
            setStatus(data.status);
            setAlerts(data.alerts);
        } catch (error) {
            console.error("Error loading agent:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8">Loading Agent Details...</div>;
    if (!status) return <div className="p-8">Agent not found.</div>;

    return (
        <div className="p-8 max-w-5xl mx-auto">
            <Link href="/dashboard/fleet" className="text-gray-500 hover:text-gray-900 flex items-center mb-6">
                <ArrowLeft size={16} className="mr-2" /> Back to Fleet
            </Link>

            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">{status.hostname}</h1>
                    <div className="flex items-center gap-2 text-gray-500 mt-1">
                        <span>{status.ip}</span> • <span>{status.platform}</span> • <span>v{status.version}</span>
                    </div>
                </div>
                <div className={`px-4 py-2 rounded-full font-bold text-sm ${status.health_state === 'healthy' ? 'bg-green-100 text-green-800' : status.health_state === 'warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                    {status.health_state.toUpperCase()}
                </div>
            </div>

            {/* Status Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                        <Cpu size={20} className="text-blue-500" />
                        <span className="font-semibold text-gray-700">CPU Usage</span>
                    </div>
                    <div className="text-2xl font-bold">{status.cpu_usage?.toFixed(1)}%</div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                        <HardDrive size={20} className="text-purple-500" />
                        <span className="font-semibold text-gray-700">RAM Usage</span>
                    </div>
                    <div className="text-2xl font-bold">{status.ram_usage?.toFixed(1)}%</div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                        <Shield size={20} className="text-green-500" />
                        <span className="font-semibold text-gray-700">Agent Version</span>
                    </div>
                    <div className="text-2xl font-bold">{status.version}</div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                        <Activity size={20} className="text-orange-500" />
                        <span className="font-semibold text-gray-700">Last Jobs</span>
                    </div>
                    <div className="text-sm">
                        Executed: <b>{status.jobs_executed_24h}</b><br />
                        Failed: <b>{status.jobs_failed_24h}</b>
                    </div>
                </div>
            </div>

            {/* Alerts Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <AlertTriangleIcon /> Active Alerts
                </h3>
                {alerts.length === 0 ? (
                    <p className="text-gray-500">No active alerts for this agent.</p>
                ) : (
                    <div className="space-y-3">
                        {alerts.map(alert => (
                            <div key={alert.id} className="p-3 bg-red-50 border border-red-100 rounded text-red-900 flex justify-between items-start">
                                <div>
                                    <div className="font-bold">{alert.alert_type}</div>
                                    <div className="text-sm">{alert.message}</div>
                                </div>
                                <div className="text-xs text-red-700">
                                    {new Date(alert.timestamp).toLocaleString()}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

const AlertTriangleIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-500"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>;
