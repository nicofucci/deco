"use client";

import { useEffect, useState } from "react";
import { getPartnerDetails, createPartnerApiKey, resetPartnerPassword, updatePartnerMode } from "@/lib/api";
import { useParams } from "next/navigation";
import { Copy, Plus, Key, RefreshCw } from "lucide-react";

export default function PartnerDetailPage() {
    const params = useParams();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [newKeyName, setNewKeyName] = useState("");
    const [resetting, setResetting] = useState(false);
    const [newPassword, setNewPassword] = useState<string | null>(null);

    const fetchDetails = async () => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;
        try {
            const res = await getPartnerDetails(key, params.partnerId as string);
            setData(res);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDetails();
    }, [params.partnerId]);

    const handleCreateKey = async (e: React.FormEvent) => {
        e.preventDefault();
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;
        try {
            await createPartnerApiKey(key, params.partnerId as string, newKeyName);
            setNewKeyName("");
            fetchDetails();
        } catch (e) {
            alert("Error al crear API Key");
        }
    };

    const handleResetPassword = async () => {
        if (!confirm("¿Estás seguro de que quieres resetear la contraseña de este partner? La contraseña anterior dejará de funcionar.")) {
            return;
        }
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;

        setResetting(true);
        try {
            const res = await resetPartnerPassword(key, params.partnerId as string);
            setNewPassword(res.password);
        } catch (e) {
            alert("Error al resetear contraseña");
        } finally {
            setResetting(false);
        }
    };

    const handleUpdateMode = async (newMode: "demo" | "full") => {
        if (!confirm(`¿Cambiar modo a ${newMode.toUpperCase()}?`)) return;
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;

        try {
            await updatePartnerMode(key, params.partnerId as string, newMode);
            fetchDetails();
        } catch (e) {
            alert("Error al actualizar modo");
        }
    };

    if (loading) return <div className="p-6 text-slate-400">Cargando detalles...</div>;
    if (!data) return <div className="p-6 text-red-400">Error al cargar datos.</div>;

    const currentMode = (data.partner.account_mode || "demo").toLowerCase();

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-2xl font-bold text-white">{data.partner.name}</h1>
                    <p className="text-slate-400">{data.partner.email}</p>
                    <div className="mt-2 flex items-center gap-2">
                        <span className="text-sm text-slate-500">Modo de Cuenta:</span>
                        <select
                            value={currentMode}
                            onChange={(e) => handleUpdateMode(e.target.value as "demo" | "full")}
                            className={`text-xs font-medium rounded px-2 py-1 border-none focus:ring-0 cursor-pointer ${currentMode === "full"
                                    ? "bg-green-900/30 text-green-400 hover:bg-green-900/50"
                                    : "bg-amber-900/30 text-amber-400 hover:bg-amber-900/50"
                                }`}
                        >
                            <option value="demo">DEMO</option>
                            <option value="full">FULL</option>
                        </select>
                    </div>
                </div>
                <div className="flex items-center space-x-4">
                    <button
                        onClick={handleResetPassword}
                        disabled={resetting}
                        className="flex items-center space-x-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-sm transition-colors"
                    >
                        <RefreshCw className={`h-4 w-4 ${resetting ? 'animate-spin' : ''}`} />
                        <span>Resetear Contraseña</span>
                    </button>
                    <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${data.partner.status === 'active' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
                        }`}>
                        {data.partner.status.toUpperCase()}
                    </span>
                </div>
            </div>

            {newPassword && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg w-full max-w-md text-center">
                        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-900/30 mb-4">
                            <Key className="h-6 w-6 text-blue-400" />
                        </div>
                        <h3 className="text-lg font-medium leading-6 text-white mb-2">Contraseña Reseteada</h3>
                        <p className="text-sm text-slate-400 mb-4">
                            Copia la nueva contraseña y envíala al partner.
                        </p>
                        <div className="bg-slate-950 p-3 rounded border border-slate-800 mb-4 font-mono text-lg text-blue-400 select-all break-all">
                            {newPassword}
                        </div>
                        <button
                            onClick={() => setNewPassword(null)}
                            className="w-full inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none sm:text-sm"
                        >
                            Entendido
                        </button>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Clients Section */}
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <h3 className="text-lg font-medium text-white mb-4">Clientes Gestionados ({data.clients.length})</h3>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-slate-800">
                            <thead>
                                <tr>
                                    <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">Nombre</th>
                                    <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">Email</th>
                                    <th className="px-4 py-2 text-left text-xs font-medium uppercase text-slate-500">Estado</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {data.clients.map((c: any) => (
                                    <tr key={c.id}>
                                        <td className="px-4 py-2 text-sm text-white">{c.name}</td>
                                        <td className="px-4 py-2 text-sm text-slate-400">{c.contact_email}</td>
                                        <td className="px-4 py-2 text-sm text-slate-300">{c.status}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* API Keys Section */}
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <h3 className="text-lg font-medium text-white mb-4">API Keys del Partner</h3>

                    <form onSubmit={handleCreateKey} className="flex gap-2 mb-4">
                        <input
                            type="text"
                            placeholder="Etiqueta para nueva llave"
                            value={newKeyName}
                            onChange={(e) => setNewKeyName(e.target.value)}
                            required
                            className="flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                        />
                        <button
                            type="submit"
                            className="flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
                        >
                            <Plus className="mr-1 h-4 w-4" />
                            Generar
                        </button>
                    </form>

                    <div className="space-y-2">
                        {data.api_keys.map((k: any) => (
                            <div key={k.id} className="flex items-center justify-between rounded bg-slate-950 p-3 border border-slate-800">
                                <div className="flex-1 mr-4 overflow-hidden">
                                    <div className="text-sm font-medium text-white">{k.name}</div>
                                    <div className="text-xs text-slate-500 font-mono break-all mt-1 bg-slate-900/50 p-1 rounded border border-slate-800/50 select-all">
                                        {k.api_key}
                                    </div>
                                </div>
                                <button
                                    onClick={() => { navigator.clipboard.writeText(k.api_key); alert("Copiada!"); }}
                                    className="text-slate-400 hover:text-white p-2 hover:bg-slate-800 rounded transition-colors"
                                    title="Copiar API Key"
                                >
                                    <Copy className="h-4 w-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
