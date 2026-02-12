"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, Shield, Users, Server, Activity } from "lucide-react";
import { getAdminOverview, getGlobalInsights } from "@/lib/api";

type Summary = {
    total_clients: number;
    suspended_clients: number;
    total_partners: number;
    total_assets: number;
    total_agents: number;
    active_agents: number;
    total_jobs: number;
    active_jobs: number;
    total_findings: number;
    findings_by_severity: { critical: number; high: number; medium: number; low: number };
    last_findings: {
        id: string;
        severity: string;
        title: string;
        client_name: string;
        detected_at: string;
    }[];
    system_status?: string;
};

type Insights = {
    geo_points: any[];
    total_agents: number;
} | null;

export default function OverviewPage() {
    const router = useRouter();
    const [summary, setSummary] = useState<Summary | null>(null);
    const [insights, setInsights] = useState<Insights>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                let key = localStorage.getItem("deco_admin_master_key");
                if (!key) {
                    localStorage.setItem("deco_admin_master_key", "MASTER_DECO");
                    key = "MASTER_DECO";
                }
                const [s, i] = await Promise.all([
                    getAdminOverview(key),
                    getGlobalInsights(key).catch(() => null)
                ]);
                setSummary(s);
                setInsights(i);
                setError(null);
            } catch (e: any) {
                console.error(e);
                setError("No se pudo conectar con el servidor central.");
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [router]);

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center bg-slate-950">
                <div className="text-slate-300 font-mono animate-pulse">Cargando dashboard...</div>
            </div>
        );
    }

    if (error || !summary) {
        return (
            <div className="flex h-screen items-center justify-center bg-slate-950 p-6">
                <div className="max-w-md w-full bg-slate-900 border border-red-900/50 rounded-2xl p-8 text-center shadow-2xl shadow-red-900/20">
                    <div className="flex justify-center mb-6">
                        <div className="p-4 bg-red-900/20 rounded-full">
                            <AlertTriangle className="h-12 w-12 text-red-500" />
                        </div>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">Error de Conexión</h3>
                    <p className="text-slate-400 mb-6">{error || "No se pudo cargar el dashboard."}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all font-medium shadow-lg shadow-red-600/20"
                    >
                        Reintentar
                    </button>
                </div>
            </div>
        );
    }

    const sev = summary.findings_by_severity || { critical: 0, high: 0, medium: 0, low: 0 };

    const stats = [
        { title: "Clientes", value: summary.total_clients, icon: Users, color: "text-blue-400", sub: `${summary.suspended_clients} suspendidos` },
        { title: "Agentes Online", value: summary.active_agents, icon: Server, color: "text-green-400", sub: `de ${summary.total_agents} totales` },
        { title: "Hallazgos", value: summary.total_findings, icon: Shield, color: "text-red-400", sub: "Total acumulado" },
        { title: "Jobs", value: summary.total_jobs, icon: Activity, color: "text-purple-400", sub: `${summary.active_jobs} activos` },
    ];

    return (
        <div className="min-h-screen bg-slate-950 text-white p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Resumen General</h1>
                    <p className="text-slate-400 text-sm">Estado: {summary.system_status || "healthy"}</p>
                </div>
                <div className="text-xs text-slate-500">
                    Agentes activos: {summary.active_agents} / {summary.total_agents} {insights ? `(geo: ${insights.total_agents})` : ""}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
                {stats.map((s) => (
                    <div key={s.title} className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg shadow-slate-950/40">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-slate-400">{s.title}</p>
                                <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
                                <p className="text-xs text-slate-500 mt-1">{s.sub}</p>
                            </div>
                            <s.icon className={`h-8 w-8 ${s.color}`} />
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                    <h3 className="text-lg font-semibold mb-3">Hallazgos recientes</h3>
                    <div className="space-y-2">
                        {(summary.last_findings || []).slice(0, 5).map((f) => (
                            <div key={f.id} className="flex items-center justify-between rounded border border-slate-800 bg-slate-950 p-3">
                                <div>
                                    <p className="text-sm font-medium">{f.title}</p>
                                    <p className="text-xs text-slate-500">{f.client_name}</p>
                                </div>
                                <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-200 capitalize">{f.severity}</span>
                            </div>
                        ))}
                        {(summary.last_findings || []).length === 0 && (
                            <p className="text-slate-500 text-sm">Sin hallazgos recientes.</p>
                        )}
                    </div>
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                    <h3 className="text-lg font-semibold mb-3">Severidad</h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="p-3 rounded border border-slate-800 bg-slate-950">Critical: {sev.critical}</div>
                        <div className="p-3 rounded border border-slate-800 bg-slate-950">High: {sev.high}</div>
                        <div className="p-3 rounded border border-slate-800 bg-slate-950">Medium: {sev.medium}</div>
                        <div className="p-3 rounded border border-slate-800 bg-slate-950">Low: {sev.low}</div>
                    </div>
                </div>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                <h3 className="text-lg font-semibold mb-3">Estado de agentes</h3>
                <p className="text-sm text-slate-400">
                    Total: {summary.total_agents} | Online: {summary.active_agents} | Geo puntos: {insights?.geo_points?.length ?? 0}
                </p>
                <p className="text-xs text-slate-500 mt-2">Mapa deshabilitado temporalmente para estabilidad.</p>
            </div>
        </div>
    );
}
