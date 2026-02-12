"use client";

import { useEffect, useState } from "react";
import { getMyAgents, updateMyAgents } from "@/lib/partner-api";
import { useI18n } from "@/lib/i18n";
import { Check, X, RefreshCw, Server, Shield } from "lucide-react";

export default function AgentsPage() {
    const { t } = useI18n();
    const [agents, setAgents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);

    useEffect(() => {
        loadAgents();
    }, []);

    const loadAgents = () => {
        const token = localStorage.getItem("deco_partner_api_key");
        if (token) {
            getMyAgents(token)
                .then(setAgents)
                .catch(console.error)
                .finally(() => setLoading(false));
        }
    };

    const handleUpdate = async () => {
        if (!confirm("¿Estás seguro de lanzar una actualización masiva a TODOS los agentes online que no estén en la última versión?")) return;

        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;

        setUpdating(true);
        try {
            const res = await updateMyAgents(token);
            alert(`Actualización iniciada: ${res.queued} agentes en cola. Versión objetivo: ${res.version}`);
            loadAgents(); // Refresh list potentially
        } catch (e: any) {
            alert("Error al iniciar actualización: " + e.message);
        }
        setUpdating(false);
    };

    if (loading) return (
        <div className="flex h-full items-center justify-center p-10 text-slate-400">
            <RefreshCw className="animate-spin mr-2 h-6 w-6" /> Cargando agentes...
        </div>
    );

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center">
                        <Server className="mr-3 h-6 w-6 text-blue-400" />
                        {t('agents')}
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">Gestión centralizada de agentes y actualizaciones.</p>
                </div>

                <div className="flex space-x-3">
                    <button
                        onClick={loadAgents}
                        className="px-3 py-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
                    >
                        <RefreshCw className="h-4 w-4" />
                    </button>
                    <button
                        onClick={handleUpdate}
                        disabled={updating}
                        className="flex items-center bg-blue-600 px-4 py-2 rounded text-white hover:bg-blue-700 disabled:opacity-50 font-medium transition-colors"
                    >
                        {updating ? (
                            <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                            <Shield className="mr-2 h-4 w-4" />
                        )}
                        {updating ? "Iniciando..." : "Actualizar Agentes"}
                    </button>
                </div>
            </div>

            <div className="rounded-lg border border-slate-700 bg-slate-800/40 overflow-hidden shadow-sm">
                <table className="w-full text-left text-sm text-slate-400">
                    <thead className="bg-slate-900/60 text-slate-200 border-b border-slate-700">
                        <tr>
                            <th className="px-6 py-4 font-medium">Hostname</th>
                            <th className="px-6 py-4 font-medium">Cliente</th>
                            <th className="px-6 py-4 font-medium">Estado</th>
                            <th className="px-6 py-4 font-medium">Versión</th>
                            <th className="px-6 py-4 font-medium">Capacidades (X-Ray)</th>
                            <th className="px-6 py-4 font-medium">Última Conexión</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/50">
                        {agents.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="px-6 py-8 text-center text-slate-500">
                                    No hay agentes registrados.
                                </td>
                            </tr>
                        ) : (
                            agents.map(a => (
                                <tr key={a.id} className="hover:bg-slate-800/30 transition-colors">
                                    <td className="px-6 py-4 font-medium text-white">{a.hostname}</td>
                                    <td className="px-6 py-4 text-blue-300">{a.client_name}</td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${a.status === 'online'
                                                ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                                                : 'bg-slate-700 text-slate-400 border border-slate-600'
                                            }`}>
                                            <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${a.status === 'online' ? 'bg-green-400' : 'bg-slate-400'}`}></span>
                                            {a.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 font-mono text-xs">{a.version || "1.0.0"}</td>
                                    <td className="px-6 py-4">
                                        {a.capabilities?.xray ? (
                                            <div className="flex items-center text-green-400 text-xs bg-green-900/20 px-2 py-1 rounded w-fit border border-green-900/30">
                                                <Check className="h-3 w-3 mr-1" />
                                                X-Ray Ready
                                            </div>
                                        ) : (
                                            <span className="text-slate-600 text-xs">-</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 text-xs text-slate-500">
                                        {a.last_seen_at ? new Date(a.last_seen_at).toLocaleString() : "Nunca"}
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
