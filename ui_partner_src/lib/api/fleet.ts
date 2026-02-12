import { API_URL } from "../api";

export interface AgentStatus {
    agent_id: string;
    client_id: string;
    hostname: string;
    ip: string;
    platform: string;
    version: string;
    last_seen: string;
    last_update_status: string;
    health_state: 'healthy' | 'warning' | 'critical' | 'unknown';
    jobs_executed_24h: number;
    jobs_failed_24h: number;
    cpu_usage: number;
    ram_usage: number;
}

export const FleetAPI = {
    getClientAgents: async (token: string, clientId: string, signal?: AbortSignal) => {
        const url = `${API_URL}/api/fleet/clients/${clientId}/agents`;
        console.log(`[FleetAPI] Fetching agents for client ${clientId} -> ${url}`);

        const response = await fetch(url, {
            headers: {
                "X-Partner-API-Key": token,
                "Content-Type": "application/json"
            },
            signal
        });
        if (!response.ok) {
            console.error(`[FleetAPI] Error: ${response.status} ${response.statusText}`);
            throw new Error(`No se pudieron obtener agentes (status ${response.status})`);
        }
        const data = await response.json();
        console.log(`[FleetAPI] Agents loaded:`, data);
        return data as AgentStatus[];
    }
};
