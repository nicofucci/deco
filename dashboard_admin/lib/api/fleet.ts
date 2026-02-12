
// Ensure this matches start_tower.sh backend URL
const INTERNAL_API_URL =
  process.env.ORCHESTRATOR_INTERNAL_URL ||
  process.env.INTERNAL_API_URL ||
  'http://orchestrator_api:8000';

const BROWSER_API_URL =
  (typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname))
    ? 'http://127.0.0.1:18001'
    : (process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'https://api.deco-security.com');

const API_URL = (typeof window === 'undefined') ? INTERNAL_API_URL : BROWSER_API_URL;

// Types
export interface AgentStatus {
    agent_id: string;
    client_id: string;
    hostname: string;
    ip: string;
    platform: string;
    version: string;
    last_seen: string;
    last_update_check: string;
    last_update_status: string;
    health_state: 'healthy' | 'warning' | 'critical' | 'unknown';
    error_reason?: string;
    jobs_executed_24h: number;
    jobs_failed_24h: number;
    cpu_usage: number;
    ram_usage: number;
}

export interface FleetAlert {
    id: string;
    agent_id: string;
    alert_type: string;
    severity: string;
    message: string;
    timestamp: string;
    resolved: boolean;
}

export interface FleetStats {
    total: number;
    items: AgentStatus[];
}

// API Service
export const FleetAPI = {
    getAgents: async (status?: string): Promise<FleetStats> => {
        const url = new URL(`${API_URL}/api/fleet/agents`);
        if (status) url.searchParams.set('status', status);
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`No se pudieron obtener agentes (status ${response.status})`);
        }
        return response.json();
    },

    getAgentDetail: async (agentId: string) => {
        const response = await fetch(`${API_URL}/api/fleet/agents/${agentId}`);
        if (!response.ok) {
            throw new Error(`No se pudo obtener el agente ${agentId} (status ${response.status})`);
        }
        return response.json(); // { status: AgentStatus, alerts: FleetAlert[] }
    },

    getAlerts: async (resolved = false) => {
        const url = new URL(`${API_URL}/api/fleet/alerts`);
        url.searchParams.set('resolved', String(resolved));
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`No se pudieron obtener alertas (status ${response.status})`);
        }
        return response.json();
    },

    // Client specific
    getClientAgents: async (clientId: string) => {
        const response = await fetch(`${API_URL}/api/fleet/clients/${clientId}/agents`);
        if (!response.ok) {
            throw new Error(`No se pudieron obtener agentes del cliente ${clientId} (status ${response.status})`);
        }
        return response.json();
    }
};
