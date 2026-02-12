
"use client";

import React, { useEffect, useState } from 'react';
import { FleetAPI, AgentStatus, FleetAlert } from '../../../lib/api/fleet';
import { FleetStats } from '../../../components/fleet/FleetStats';
import { AgentsTable } from '../../../components/fleet/AgentsTable';
import { Loader2 } from 'lucide-react';

export default function FleetPage() {
    const [agents, setAgents] = useState<AgentStatus[]>([]);
    const [alerts, setAlerts] = useState<FleetAlert[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const agentData = await FleetAPI.getAgents(); // items
            const alertData = await FleetAPI.getAlerts();
            setAgents(agentData.items || []);
            setAlerts(alertData || []);
        } catch (error) {
            console.error("Error loading fleet data:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <Loader2 className="animate-spin text-blue-600" size={48} />
                <span className="ml-3 text-gray-500">Loading Fleet Guardian...</span>
            </div>
        );
    }

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Fleet Guardian™ Overview</h1>
            <p className="text-gray-500 mb-8">Global telemetry and health monitoring for all deployed agents.</p>

            <FleetStats agents={agents} alertsCount={alerts.length} />

            <h2 className="text-xl font-semibold text-gray-800 mb-4 mt-8">Agent Inventory</h2>
            <AgentsTable agents={agents} />
        </div>
    );
}
