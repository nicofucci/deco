
const INTERNAL_API_URL = process.env.ORCHESTRATOR_INTERNAL_URL || 'http://orchestrator_api:8000';
const BROWSER_API_URL =
  (typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname))
    ? 'http://127.0.0.1:18001'
    : (process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'https://api.deco-security.com');

const API_URL = (typeof window === 'undefined') ? INTERNAL_API_URL : BROWSER_API_URL;

export interface AgentStatus {
    agent_id: string;
    client_id: string;
    hostname: string;
    ip: string;
    platform: string;
    version: string;
    health_state: 'healthy' | 'warning' | 'critical' | 'unknown';
    last_seen: string;
}

export const FleetAPI = {
    getMyAgents: async (clientId: string) => {
        // In client console, we usually get clientId from context or local storage.
        // Assuming the ID is passed or available.
        // If the console is generic, maybe we need an endpoint "my-agents" that uses the token?
        // But the requirement says "Use /clients/{id}/agents".
        const response = await fetch(`${API_URL}/api/fleet/clients/${clientId}/agents`);
        if (!response.ok) {
            throw new Error(`No se pudieron obtener agentes del cliente ${clientId} (status ${response.status})`);
        }
        return response.json();
    }
};
