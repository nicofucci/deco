"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getPartners, createPartner, deletePartner } from "@/lib/api";
import { AlertTriangle, Users, Shield } from "lucide-react";

type Partner = {
    id: string;
    name: string;
    email: string;
    status: string;
    account_mode?: string;
    client_limit?: number;
    agent_limit?: number;
    created_at?: string;
};

export default function PartnersPage() {
    const router = useRouter();
    const [partners, setPartners] = useState<Partner[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [showCreateModal, setShowCreateModal] = useState(false);
    const [creating, setCreating] = useState(false);
    const [generatedApiKey, setGeneratedApiKey] = useState<string | null>(null);
    const [newPartner, setNewPartner] = useState({ name: "", email: "", account_mode: "demo" });

    const fetchPartners = async () => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) {
            router.push("/login");
            return;
        }
        try {
            const res = await getPartners(key);
            setPartners(res || []);
            setError(null);
        } catch (e) {
            console.error(e);
            setError("Error al cargar la lista de partners. Verifica la conexión con el Orchestrator.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPartners();
    }, [router]);

    const handleCreatePartner = async (e: React.FormEvent) => {
        e.preventDefault();
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;

        setCreating(true);
        try {
            const res = await createPartner(key, {
                name: newPartner.name,
                email: newPartner.email,
                account_mode: newPartner.account_mode,
            });
            setShowCreateModal(false);
            setNewPartner({ name: "", email: "", account_mode: "demo" });
            if (res.api_key) setGeneratedApiKey(res.api_key);
            await fetchPartners();
        } catch (e) {
            alert("Error al crear partner. Verifique que el email no exista.");
        } finally {
            setCreating(false);
        }
    };

    const handleDeletePartner = async (partnerId: string, partnerName: string) => {
        if (!confirm(`¿Eliminar al partner "${partnerName}"?`)) return;
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;
        try {
            await deletePartner(key, partnerId);
            await fetchPartners();
        } catch (e) {
            alert("Error al eliminar partner. Asegúrate de que no tenga clientes activos.");
        }
    };

    if (loading) {
        return <div className="p-6 text-slate-400">Cargando partners...</div>;
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
                    onClick={() => { setLoading(true); fetchPartners(); }}
                    className="mt-4 px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-300 rounded-md transition-colors"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-white">Gestión de Partners</h1>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
                >
                    + Nuevo Partner
                </button>
            </div>

            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg w-full max-w-md">
                        <h2 className="text-xl font-bold text-white mb-4">Crear Nuevo Partner</h2>
                        <form onSubmit={handleCreatePartner} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-400">Nombre</label>
                                <input
                                    type="text"
                                    required
                                    className="mt-1 w-full rounded bg-slate-800 border border-slate-700 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                                    value={newPartner.name}
                                    onChange={(e) => setNewPartner({ ...newPartner, name: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-400">Email</label>
                                <input
                                    type="email"
                                    required
                                    className="mt-1 w-full rounded bg-slate-800 border border-slate-700 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                                    value={newPartner.email}
                                    onChange={(e) => setNewPartner({ ...newPartner, email: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-400">Modo de Cuenta</label>
                                <select
                                    className="mt-1 w-full rounded bg-slate-800 border border-slate-700 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                                    value={newPartner.account_mode}
                                    onChange={(e) => setNewPartner({ ...newPartner, account_mode: e.target.value })}
                                >
                                    <option value="demo">Demo (1 cliente / 1 agente)</option>
                                    <option value="full">Full (límite por paquetes)</option>
                                </select>
                                <p className="text-xs text-slate-500 mt-1">
                                    Demo: puede gestionar solo 1 cliente con 1 agente activo. Full: sin límite por ahora.
                                </p>
                            </div>
                            <div className="flex justify-end space-x-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setShowCreateModal(false)}
                                    className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    disabled={creating}
                                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md transition-colors disabled:opacity-50"
                                >
                                    {creating ? "Creando..." : "Crear"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {generatedApiKey && (
                <div className="rounded-lg border border-green-800 bg-green-900/20 p-4 text-sm text-green-200">
                    <div className="font-semibold mb-1">Partner API Key generada para el nuevo socio:</div>
                    <div className="flex items-center gap-2 bg-slate-950 p-2 rounded border border-slate-800 font-mono text-xs break-all">
                        <span>{generatedApiKey}</span>
                        <button
                            onClick={() => { navigator.clipboard.writeText(generatedApiKey); alert("Copiada!"); }}
                            className="text-slate-400 hover:text-white ml-auto"
                        >
                            Copiar
                        </button>
                    </div>
                    <div className="mt-2 text-xs text-slate-400">
                        Esta clave es necesaria para el login del partner. Guárdala en un lugar seguro.
                    </div>
                </div>
            )}

            <div className="overflow-x-auto rounded-lg border border-slate-800">
                <table className="min-w-full divide-y divide-slate-800">
                    <thead className="bg-slate-900/60 text-slate-400 text-sm">
                        <tr>
                            <th className="px-4 py-3 text-left">Nombre</th>
                            <th className="px-4 py-3 text-left">Email</th>
                            <th className="px-4 py-3 text-left">Modo</th>
                            <th className="px-4 py-3 text-left">Límites</th>
                            <th className="px-4 py-3 text-left">Estado</th>
                            <th className="px-4 py-3 text-left">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                        {partners.map((p) => (
                            <tr key={p.id} className="hover:bg-slate-900/40 transition-colors">
                                <td
                                    className="px-4 py-3 text-sm text-white font-medium cursor-pointer hover:text-blue-400"
                                    onClick={() => router.push(`/dashboard/partners/${p.id}`)}
                                >
                                    {p.name}
                                </td>
                                <td className="px-4 py-3 text-sm text-slate-300">{p.email}</td>
                                <td className="px-4 py-3 text-sm">
                                    <span className={`px-2 py-1 rounded text-xs ${p.account_mode === "full" ? "bg-green-900/40 text-green-200" : "bg-slate-800 text-slate-200"}`}>
                                        {p.account_mode === "full" ? "Full" : "Demo"}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-sm text-slate-300">
                                    Clientes: {p.client_limit ?? 0} / Agentes: {p.agent_limit ?? 0}
                                </td>
                                <td className="px-4 py-3 text-sm">
                                    <span className={`px-2 py-1 rounded text-xs ${p.status === "active" ? "bg-green-900/30 text-green-200" : "bg-red-900/30 text-red-200"}`}>
                                        {p.status}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-sm">
                                    <div className="flex items-center gap-3">
                                        <button
                                            onClick={() => router.push(`/dashboard/partners/${p.id}`)}
                                            className="text-blue-400 hover:text-blue-300 text-xs font-medium"
                                        >
                                            Ver
                                        </button>
                                        <button
                                            onClick={() => handleDeletePartner(p.id, p.name)}
                                            className="text-red-400 hover:text-red-200 text-xs"
                                        >
                                            Eliminar
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                        {partners.length === 0 && (
                            <tr>
                                <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                                    No hay partners creados.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-4 flex items-center gap-3 text-slate-300">
                <Shield className="h-5 w-5 text-blue-400" />
                <div>
                    <div className="font-semibold">Modo Demo</div>
                    <div className="text-xs text-slate-500">Límite 1 cliente / 1 agente. Cambia a Full para escalar.</div>
                </div>
            </div>
        </div>
    );
}
