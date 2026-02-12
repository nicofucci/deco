"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMe, getMyClients, getEarnings } from "@/lib/api";
import { Users, ShieldAlert } from "lucide-react";

type Partner = {
    name: string;
    client_limit?: number;
    agent_limit?: number;
    client_packages?: number;
    agent_packages?: number;
    account_mode?: string;
    type?: string;
    demo_expires_at?: string;
};

type PartnerStats = {
    agents_limit: number;
    agents_assigned: number;
    agents_available: number;
};

export default function OverviewPage() {
    const [partner, setPartner] = useState<Partner | null>(null);
    const [stats, setStats] = useState<PartnerStats | null>(null);
    const [clients, setClients] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    useEffect(() => {
        // Fix: Debug logging to identify data shape
        if (clients && clients.length > 0) {
            console.log("Partner Clients Data:", clients);
            // Verify if total_agents exists
            console.log("First Client Keys:", Object.keys(clients[0]));
        }
        if (stats) {
            console.log("Partner Stats (Source of Truth):", stats);
        }
    }, [clients, stats]);

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem("deco_partner_api_key");
            if (!token) {
                router.push("/login");
                return;
            }
            try {
                const meRes = await getMe(token);
                // Fix: Ensure meRes is an object before setting
                if (meRes && typeof meRes === 'object') {
                    setPartner(meRes);
                } else {
                    throw new Error("Respuesta inválida de perfil");
                }

                const statsRes = await getEarnings(token).catch(() => null); // Fail safely
                setStats(statsRes);

                const clientsRes = await getMyClients(token).catch(() => []);
                setClients(Array.isArray(clientsRes) ? clientsRes : []);
                setError(null);
            } catch (e: any) {
                console.error("Error fetching data:", e);
                setError(e.message || "Error al cargar datos. Verifica tu conexión.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [router]);

    if (loading) {
        return (
            <div className="flex h-full items-center justify-center p-6">
                <div className="text-slate-400 animate-pulse">Cargando datos del partner...</div>
            </div>
        );
    }

    if (error || !partner) {
        return (
            <div className="flex h-full items-center justify-center p-6">
                <div className="rounded-lg border border-red-900 bg-red-900/20 p-6 text-center">
                    <ShieldAlert className="mx-auto h-12 w-12 text-red-500 mb-4" />
                    <h3 className="text-lg font-medium text-red-400 mb-2">Error de Carga</h3>
                    <p className="text-sm text-red-300 mb-4">{error || "No se pudieron obtener los datos."}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-red-900/50 hover:bg-red-900/70 text-red-200 rounded transition-colors"
                    >
                        Reintentar
                    </button>
                </div>
            </div>
        );
    }

    // Fix: Safe access to account_mode
    const rawMode = partner?.account_mode || partner?.type || "demo";
    const mode = String(rawMode || "demo").toLowerCase();
    const isDemo = mode === "demo";

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Hola, {partner.name}</h1>
                <span className={`px-3 py-1 rounded text-xs ${isDemo ? "bg-amber-900/40 text-amber-200" : "bg-green-900/30 text-green-200"}`}>
                    Modo {isDemo ? "Demo" : "Full"}
                </span>
            </div>

            {isDemo && (
                <div className="rounded-lg border border-amber-800 bg-amber-900/20 p-4 text-amber-100 flex gap-3 items-start">
                    <ShieldAlert className="h-5 w-5 mt-0.5" />
                    <div>
                        <div className="font-semibold">Estás en modo Demo</div>
                        <div className="text-sm">Límite 1 cliente / 1 agente. Contacta con Deco-Security para pasar a Full.</div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <div className="flex items-center justify-between">
                        <h3 className="text-sm font-medium text-slate-400">Clientes Activos</h3>
                        <Users className="h-4 w-4 text-blue-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold text-white">
                        {clients.length} <span className="text-sm text-slate-500 font-normal">/ {partner.client_limit ?? (isDemo ? 1 : 0)}</span>
                    </div>
                    <div className="mt-1 text-xs text-slate-500">
                        Paquetes: {partner.client_packages || 0}
                    </div>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <div className="flex items-center justify-between">
                        <h3 className="text-sm font-medium text-slate-400">Agentes Disponibles</h3>
                        <ShieldAlert className="h-4 w-4 text-purple-500" />
                    </div>
                    <div className="mt-2 text-2xl font-bold text-white">
                        {/* Fix: Calculation of available agents (Backend Source of Truth) */}
                        {(() => {
                            if (stats) {
                                return (
                                    <span>
                                        {stats.agents_available} <span className="text-sm text-slate-500 font-normal">/ {stats.agents_limit}</span>
                                    </span>
                                );
                            }
                            // Fallback to client-side calc if stats fail
                            const limit = Number(partner?.agent_limit) ?? (isDemo ? 1 : 0);
                            const used = Array.isArray(clients)
                                ? clients.reduce((acc, c) => acc + (Number(c?.total_agents) || 0), 0)
                                : 0;
                            const available = Math.max(0, limit - used);
                            return (
                                <span>
                                    {available} <span className="text-sm text-slate-500 font-normal">/ {limit}</span>
                                </span>
                            );
                        })()}
                    </div>
                    <div className="mt-1 text-xs text-slate-500">
                        Paquetes: {partner.agent_packages || 0}
                    </div>
                </div>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                <h3 className="mb-4 text-lg font-medium text-white">Últimos Clientes Registrados</h3>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-800">
                        <thead>
                            <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Nombre</th>
                                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Email</th>
                                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Estado</th>
                                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Fecha</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                            {clients.slice(0, 5).map((c: any) => (
                                <tr key={c.id}>
                                    <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-white">{c.name}</td>
                                    <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-400">{c.contact_email}</td>
                                    <td className="whitespace-nowrap px-4 py-3">
                                        <span className="inline-flex items-center rounded-full bg-green-900/30 px-2.5 py-0.5 text-xs font-medium text-green-400">
                                            {c.status}
                                        </span>
                                    </td>
                                    <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-500">{new Date(c.created_at).toLocaleDateString()}</td>
                                </tr>
                            ))}
                            {clients.length === 0 && (
                                <tr>
                                    <td colSpan={4} className="px-4 py-6 text-center text-slate-500">
                                        Aún no tienes clientes registrados.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
