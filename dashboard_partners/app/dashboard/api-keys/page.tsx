"use client";

import { useEffect, useState } from "react";
import { getMyApiKeys, createApiKey, revokeApiKey } from "@/lib/partner-api";
import { Plus, Trash2, Copy } from "lucide-react";

export default function ApiKeysPage() {
    const [keys, setKeys] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newKeyName, setNewKeyName] = useState("");

    const fetchKeys = async () => {
        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;
        try {
            const res = await getMyApiKeys(token);
            setKeys(res);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchKeys();
    }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;
        try {
            await createApiKey(token, newKeyName);
            setNewKeyName("");
            fetchKeys();
        } catch (e) {
            alert("Error al crear API Key");
        }
    };

    const handleRevoke = async (id: string) => {
        if (!confirm("¿Estás seguro de revocar esta API Key? Dejará de funcionar inmediatamente.")) return;
        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;
        try {
            await revokeApiKey(token, id);
            fetchKeys();
        } catch (e) {
            alert("Error al revocar API Key");
        }
    };

    if (loading) return <div className="p-6 text-slate-400">Cargando API Keys...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">API Keys de Partner</h1>
            <p className="text-slate-400">Utiliza estas llaves para integrar tus sistemas con Deco-Security programáticamente.</p>

            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                <h3 className="text-lg font-medium text-white mb-4">Crear Nueva Llave</h3>
                <form onSubmit={handleCreate} className="flex gap-4">
                    <input
                        type="text"
                        placeholder="Nombre (ej: Script N8N)"
                        value={newKeyName}
                        onChange={(e) => setNewKeyName(e.target.value)}
                        required
                        className="flex-1 rounded-md border border-slate-700 bg-slate-950 px-4 py-2 text-white focus:border-blue-500 focus:outline-none"
                    />
                    <button
                        type="submit"
                        className="flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                    >
                        <Plus className="mr-2 h-4 w-4" />
                        Generar
                    </button>
                </form>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden">
                <table className="min-w-full divide-y divide-slate-800">
                    <thead className="bg-slate-950">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Nombre</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">API Key</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Creada</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Último Uso</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-900">
                        {keys.map((k: any) => (
                            <tr key={k.id} className="hover:bg-slate-800/50 transition-colors">
                                <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-white">{k.name}</td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm font-mono text-slate-400">
                                    {k.api_key.substring(0, 8)}...{k.api_key.substring(k.api_key.length - 4)}
                                </td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500">{new Date(k.created_at).toLocaleDateString()}</td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500">
                                    {k.last_used_at ? new Date(k.last_used_at).toLocaleString() : "Nunca"}
                                </td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300 flex space-x-3">
                                    <button
                                        onClick={() => { navigator.clipboard.writeText(k.api_key); alert("Copiada!"); }}
                                        className="text-blue-400 hover:text-blue-300"
                                        title="Copiar"
                                    >
                                        <Copy className="h-4 w-4" />
                                    </button>
                                    <button
                                        onClick={() => handleRevoke(k.id)}
                                        className="text-red-400 hover:text-red-300"
                                        title="Revocar"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
