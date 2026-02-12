import { Client, Finding, Asset, ScanJob, ScanResult } from "@/types"; // We will define types later or use any for now

const INTERNAL_API_URL = process.env.ORCHESTRATOR_INTERNAL_URL || 'http://orchestrator_api:8000';
const BROWSER_API_URL =
    (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'))
        ? 'http://127.0.0.1:18001'
        : (process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'https://api.deco-security.com');

const API_URL = (typeof window === 'undefined') ? INTERNAL_API_URL : BROWSER_API_URL;

export async function getClientInfo(apiKey: string) {
    console.log(`[getClientInfo] Calling ${API_URL}/api/clients/me with key ${apiKey.substring(0, 4)}...`);
    const res = await fetch(`${API_URL}/api/clients/me`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Failed to fetch client info");
    return res.json();
}

export async function getFindings(apiKey: string, assetId?: string) {
    const params = assetId ? `?asset_id=${assetId}` : "";
    const res = await fetch(`${API_URL}/api/client/findings${params}`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Error al obtener hallazgos");
    return res.json();
}

export async function getAssets(apiKey: string) {
    const res = await fetch(`${API_URL}/api/client/assets`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Error al obtener activos");
    return res.json();
}

export async function getJobs(apiKey: string) {
    const res = await fetch(`${API_URL}/api/client/jobs`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Error al obtener jobs");
    return res.json();
}

export async function getAgents(apiKey: string) {
    const res = await fetch(`${API_URL}/api/clients/me/agents`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Failed to fetch agents");
    return res.json();
}

export async function createJob(apiKey: string, payload: { type: string; target: string; agent_id: string }) {
    const res = await fetch(`${API_URL}/api/jobs`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Client-API-Key": apiKey,
        },
        body: JSON.stringify({
            ...payload,
            client_id: "ignored", // Backend handles this
        }),
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) {
        const detail = data?.detail || "Error al crear el job";
        throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    return data;
}

export async function getExecutiveReport(apiKey: string, format: "html" | "markdown" = "markdown") {
    const res = await fetch(`${API_URL}/api/client/reports/summary`, {
        method: "POST",
        headers: {
            "X-Client-API-Key": apiKey,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ format }),
    });
    if (!res.ok) throw new Error("Error al generar el informe");
    return res.json();
}

export async function deleteJob(apiKey: string, jobId: string) {
    const res = await fetch(`${API_URL}/api/jobs/${jobId}`, {
        method: "DELETE",
        headers: {
            "X-Client-API-Key": apiKey,
        },
    });
    if (!res.ok) throw new Error("Error al eliminar el job");
    if (!res.ok) throw new Error("Error al eliminar el job");
    return true;
}

export async function getNetworkAssets(apiKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/network/clients/${clientId}/network-assets`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Error obteniendo activos de red");
    return res.json();
}

export async function getVulnerabilities(apiKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/network/clients/${clientId}/vulnerabilities`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Failed to fetch vulnerabilities");
    return res.json();
}

export async function getSpecializedFindings(apiKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/network/clients/${clientId}/specialized-findings`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Failed to fetch specialized findings");
    return res.json();
}

export async function getNetworkAssetsSummary(apiKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/network/clients/${clientId}/network-assets/summary`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Error obteniendo resumen de activos");
    return res.json();
}

export async function getPredictiveReport(apiKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/predictive/clients/${clientId}/predictive`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    // Silent fail optional or return default
    if (!res.ok) return { score: 100, signals: [] };
    return res.json();
}


export async function getClientThreatSummary(apiKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/threat-intel/clients/${clientId}/summary`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) {
        // Silent fail acceptable for dashboard widget
        console.warn("Failed to fetch threat summary");
        return null;
    }
    return res.json();
}

// ... existing exports ...

export async function getReportHistory(apiKey: string, clientId: string) {
    const res = await fetch(`${API_URL}/api/reports/clients/${clientId}/reports`, {
        headers: { "X-Client-API-Key": apiKey },
    });
    if (!res.ok) throw new Error("Error fetching report history");
    return res.json();
}

export async function generatePDFReport(apiKey: string, clientId: string, type: "executive" | "technical" = "executive", force: boolean = false) {
    const res = await fetch(`${API_URL}/api/reports/generate/${clientId}?type=${type}&force=${force}`, {
        method: "POST",
        headers: {
            "X-Client-API-Key": apiKey,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
    });
    // Check for 200 or 201
    const data = await res.json().catch(() => null);
    if (!res.ok) {
        let errorMsg = "Error generating report";
        if (data) {
            if (typeof data.detail === "string") errorMsg = data.detail;
            else if (typeof data.message === "string") errorMsg = data.message;
            else if (data.error && typeof data.error === "string") errorMsg = data.error;
            else errorMsg = JSON.stringify(data);
        }
        throw new Error(errorMsg);
    }
    return data;
}


export async function getAutofixPlaybooks(apiKey: string, clientId: string) { return []; }

