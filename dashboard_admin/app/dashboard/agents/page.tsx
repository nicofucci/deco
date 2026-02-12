"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAgents, deleteAgent } from "@/lib/api";
import { Trash, AlertTriangle, Server } from "lucide-react";

export default function AgentsPage() {
    const router = useRouter();
    const [agents, setAgents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchAgents = async () => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) {
            router.push("/login");
            return;
        }
        try {
            const res = await getAgents(key);
            setAgents(res || []);
            setError(null);
        } catch (e) {
            console.error(e);
            setError("No se pudo cargar la lista de agentes. Verifica la conexión con el Orchestrator.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAgents();
    }, [router]);

    const handleDeleteAgent = async (agentId: string) => {
        if (!confirm("¿Estás seguro de que deseas eliminar este agente?")) return;

        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;

        try {
            await deleteAgent(key, agentId);
            fetchAgents();
        } catch (e: any) {
            alert(`Error al eliminar agente: ${e.message || "Error desconocido"}`);
        }
    };

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <div className="text-slate-400 animate-pulse">Cargando agentes...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="rounded-lg border border-red-900/50 bg-red-900/20 p-6 text-center">
                <div className="flex justify-center mb-4">
                    <AlertTriangle className="h-10 w-10 text-red-500" />
                </div>
                <h3 className="text-lg font-medium text-red-400 mb-2">Error de Carga</h3>
                <p className="text-slate-400">{error}</p>
                <button
                    onClick={() => { setLoading(true); fetchAgents(); }}
                    className="mt-4 px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-300 rounded-md transition-colors"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Agentes Globales</h1>

            {agents.length > 0 ? (
                <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden">
                    <table className="min-w-full divide-y divide-slate-800">
                        <thead className="bg-slate-950">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Hostname</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Cliente</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Estado</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Última Actividad</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 bg-slate-900">
                            {agents.map((agent: any) => (
                                <tr key={agent.id} className="hover:bg-slate-800/50 transition-colors">
                                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-white">{agent.hostname}</td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-400">{agent.client_name}</td>
                                    <td className="whitespace-nowrap px-6 py-4">
                                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${agent.status === 'online' ? 'bg-green-900/30 text-green-400' : 'bg-gray-800 text-gray-400'
                                            }`}>
                                            {agent.status.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500">
                                        {agent.last_seen_at ? new Date(agent.last_seen_at).toLocaleString() : "Nunca"}
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">
                                        <button onClick={() => handleDeleteAgent(agent.id)} className="text-red-400 hover:text-red-300" title="Eliminar Agente">
                                            <Trash className="h-4 w-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-12 text-center">
                    <div className="flex justify-center mb-4">
                        <Server className="h-12 w-12 text-slate-600" />
                    </div>
                    <h3 className="text-lg font-medium text-white mb-2">No hay agentes registrados</h3>
                    <p className="text-slate-400">Aún no se han conectado agentes al sistema.</p>
                </div>
            )}
        </div>
    );
}
