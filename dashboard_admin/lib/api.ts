// Selección dinámica: SSR usa interno; CSR usa env y solo fuerza loopback si hostname local
const INTERNAL_API_URL =
    process.env.ORCHESTRATOR_INTERNAL_URL ||
    process.env.INTERNAL_API_URL ||
    "http://orchestrator_api:8000";

const BROWSER_API_URL =
    (typeof window !== "undefined" && ["localhost", "127.0.0.1"].includes(window.location.hostname))
        ? "http://127.0.0.1:8001"
        : (process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "https://api.deco-security.com");

const PRIMARY_API_URL = (typeof window === "undefined") ? INTERNAL_API_URL : BROWSER_API_URL;
const API_URL = PRIMARY_API_URL; // compat: resto de funciones usan API_URL base

const FALLBACK_URLS: string[] = Array.from(new Set([
    PRIMARY_API_URL,
    process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "",
    "https://api.deco-security.com",
].filter(Boolean)));

async function fetchWithFallback(path: string, init?: RequestInit) {
    let lastErr: any = null;
    for (const base of FALLBACK_URLS) {
        try {
            const res = await fetch(`${base}${path}`, init);
            if (res.ok) return res;
            lastErr = new Error(`HTTP ${res.status} ${res.statusText} @ ${base}${path}`);
        } catch (e) {
            lastErr = e;
        }
    }
    throw lastErr || new Error("No se pudo contactar al Orchestrator");
}

export async function getAdminOverview(masterKey: string) {
    const res = await fetchWithFallback(`/api/master/summary`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Error al obtener resumen");
    return res.json();
}

export async function getGlobalInsights(masterKey: string) {
    const res = await fetchWithFallback(`/api/master/global_insights`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Error al obtener insights globales");
    return res.json();
}

export async function getClients(masterKey: string) {
    const res = await fetch(`${API_URL}/api/master/clients`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch clients");
    return res.json();
}

export async function deleteClient(masterKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/master/clients/${clientId}`, {
        method: "DELETE",
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Failed to delete client: ${res.status} ${errorText}`);
    }
    return res.json();
}

export async function getAgents(masterKey: string) {
    const res = await fetch(`${API_URL}/api/master/agents`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch agents");
    return res.json();
}

export async function deleteAgent(masterKey: string, agentId: string) {
    const res = await fetch(`${API_URL}/api/master/agents/${agentId}`, {
        method: "DELETE",
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to delete agent");
    return res.json();
}

export async function getJobs(masterKey: string) {
    const res = await fetch(`${API_URL}/api/master/jobs`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch jobs");
    return res.json();
}

export async function getFindings(masterKey: string) {
    const res = await fetch(`${API_URL}/api/master/findings`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch findings");
    return res.json();
}

export async function getMasterAssets(masterKey: string, skip: number = 0, limit: number = 50, search: string = "", clientId: string = "") {
    const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
    });
    if (search) params.append("search", search);
    if (clientId) params.append("client_id", clientId);

    const res = await fetch(`${API_URL}/api/master/assets?${params.toString()}`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch assets");
    return res.json();
}

export async function getMasterFindings(masterKey: string, skip: number = 0, limit: number = 50, severity: string = "", clientId: string = "") {
    const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
    });
    if (severity) params.append("severity", severity);
    if (clientId) params.append("client_id", clientId);

    const res = await fetch(`${API_URL}/api/master/findings?${params.toString()}`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch findings");
    return res.json();
}

export async function getSystemHealth(masterKey: string) {
    const res = await fetch(`${API_URL}/api/master/system`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch system health");
    return res.json();
}

export async function getPartners(masterKey: string) {
    const res = await fetch(`${API_URL}/api/partners/`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch partners");
    return res.json();
}

export async function getPartnerDetails(masterKey: string, partnerId: string) {
    const res = await fetch(`${API_URL}/api/master/partners/${partnerId}`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch partner details");
    return res.json();
}

export async function createPartnerApiKey(masterKey: string, partnerId: string, name: string) {
    const res = await fetch(`${API_URL}/api/master/partners/${partnerId}/api-keys`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Admin-Master-Key": masterKey
        },
        body: JSON.stringify({ name }),
    });
    if (!res.ok) throw new Error("Failed to create partner api key");
    return res.json();
}

export async function createPartner(masterKey: string, data: any) {
    const res = await fetch(`${API_URL}/api/admin/partners`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Admin-Master-Key": masterKey
        },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create partner");
    return res.json();
}

export async function deletePartner(masterKey: string, partnerId: string) {
    const res = await fetch(`${API_URL}/api/admin/partners/${partnerId}`, {
        method: "DELETE",
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to delete partner");
    return true;
}

export async function resetPartnerPassword(masterKey: string, partnerId: string) {
    const res = await fetch(`${API_URL}/api/admin/partners/${partnerId}/reset-password`, {
        method: "PATCH",
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to reset password");
    return res.json();
}

export async function getRiskRadar(masterKey: string) {
    const res = await fetch(`${API_URL}/api/admin/risk-radar`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch risk radar");
    return res.json();
}

export async function getNetworkTopology(masterKey: string) {
    const res = await fetch(`${API_URL}/api/admin/network-topology`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch network topology");
    return res.json();
}

export async function getGlobalStats(masterKey: string) {
    const res = await fetch(`${API_URL}/api/admin/global-stats`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch global stats");
    return res.json();
}

export async function generateReport(masterKey: string, clientId: string, type: "executive" | "technical", lang: string = "es") {
    const res = await fetch(`${API_URL}/api/reports/generate/${clientId}?type=${type}&lang=${lang}`, {
        method: "POST",
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to generate report");
    return res.json();
}

export async function getPlans(masterKey: string) {
    const res = await fetch(`${API_URL}/api/billing/plans`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch plans");
    return res.json();
}

export async function subscribeClient(masterKey: string, clientId: string, planId: string) {
    const res = await fetch(`${API_URL}/api/billing/subscribe`, {
        method: "POST",
        headers: {
            "X-Admin-Master-Key": masterKey,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ client_id: clientId, plan_id: planId }),
    });
    if (!res.ok) throw new Error("Failed to subscribe");
    return res.json();
}

export async function getSubscriptionStatus(masterKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/billing/status/${clientId}`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch subscription status");
    return res.json();
}

export async function getBillingPortal(masterKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/billing/portal/${clientId}`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch portal URL");
    return res.json();
}

export async function getThreatIntel(masterKey: string, ip: string) {
    const res = await fetch(`${API_URL}/api/intel/ip/${ip}`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch threat intel");
    return res.json();
}

export async function configureSIEM(masterKey: string, clientId: string, webhookUrl: string) {
    const res = await fetch(`${API_URL}/api/admin/siem-config`, {
        method: "POST",
        headers: {
            "X-Admin-Master-Key": masterKey,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ client_id: clientId, webhook_url: webhookUrl }),
    });
    if (!res.ok) throw new Error("Failed to configure SIEM");
    return res.json();
}

export async function deleteJob(masterKey: string, jobId: string) {
    const res = await fetch(`${API_URL}/api/admin/jobs/${jobId}`, {
        method: "DELETE",
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to delete job");
    return true;
}

export async function getJobResults(masterKey: string, jobId: string) {
    const res = await fetch(`${API_URL}/api/master/jobs/${jobId}/results`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch job results");
    return res.json();
}

export function getJobDownloadUrl(jobId: string) {
    return `${API_URL}/api/master/jobs/${jobId}/download`;
}

export async function getAIRecommendations(masterKey: string) {
    const res = await fetch(`${API_URL}/api/ai/recommendations`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch AI recommendations");
    return res.json();
}



export async function updatePartnerMode(masterKey: string, partnerId: string, mode: "demo" | "full") {
    const res = await fetch(`${API_URL}/api/admin/partners/${partnerId}/mode`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "X-Admin-Master-Key": masterKey
        },
        body: JSON.stringify({ account_mode: mode }),
    });
    if (!res.ok) throw new Error("Failed to update partner mode");
    return res.json();
}

export async function getReports(masterKey: string) {
    const res = await fetch(`${API_URL}/api/master/reports`, {
        headers: { "X-Admin-Master-Key": masterKey },
    });
    if (!res.ok) throw new Error("Failed to fetch reports");
    return res.json();
}
