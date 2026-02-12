"use client";

import { useEffect, useState } from "react";
import { useClient } from "@/providers/ClientProvider";
import { getAssets, getFindings, getAgents } from "@/lib/client-api";
import { AssetCard } from "@/components/AssetCard";

export default function AssetsPage() {
    const { apiKey } = useClient();
    const [assets, setAssets] = useState([]);
    const [findings, setFindings] = useState([]);
    const [agents, setAgents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!apiKey) return;

        const fetchData = async () => {
            try {
                setError(null);
                const [assetsData, findingsData, agentsData] = await Promise.all([
                    getAssets(apiKey),
                    getFindings(apiKey),
                    getAgents(apiKey),
                ]);
                setAssets(assetsData);
                setFindings(findingsData);
                setAgents(agentsData);
            } catch (e) {
                console.error("Error fetching assets", e);
                setError("No pudimos cargar los activos. Inténtalo de nuevo en unos segundos.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [apiKey]);

    const getFindingCount = (assetId: string) => {
        return findings.filter((f: any) => f.asset_id === assetId).length;
    };

    if (loading) return <div className="p-6">Cargando activos...</div>;

    return (
        <div className="space-y-8">
            {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}
            {/* Agents Section */}
            <section>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Agentes Conectados</h2>
                <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
                    <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
                        <thead className="bg-slate-50 dark:bg-slate-950">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Hostname</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">IP Local</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Red (CIDR)</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Interfaces</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Estado</th>
                                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Última Vez</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 dark:divide-slate-800 bg-white dark:bg-slate-900">
                            {agents.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-4 text-center text-sm text-slate-500">
                                        No hay agentes conectados.
                                    </td>
                                </tr>
                            ) : (
                                agents.map((agent: any) => (
                                    <tr key={agent.id}>
                                        <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-900 dark:text-white">
                                            {agent.hostname}
                                        </td>
                                        <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                            {agent.local_ip || "N/A"}
                                        </td>
                                        <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                            {agent.primary_cidr || "N/A"}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                            <div className="flex flex-col space-y-1">
                                                {agent.interfaces && agent.interfaces.length > 0 ? (
                                                    agent.interfaces.slice(0, 2).map((iface: any, idx: number) => (
                                                        <span key={idx} className="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                                                            {iface.name}: {iface.ip}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span className="text-xs text-slate-400">Sin detalles</span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="whitespace-nowrap px-6 py-4 text-sm">
                                            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${agent.status === 'online' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-400'
                                                }`}>
                                                {agent.status}
                                            </span>
                                        </td>
                                        <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                            {new Date(agent.last_seen_at).toLocaleString()}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </section>

            <section>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Inventario de Activos Descubiertos</h2>
                {assets.length === 0 ? (
                    <div className="rounded-md border border-dashed border-slate-300 p-6 text-sm text-slate-600 dark:border-slate-700 dark:text-slate-300">
                        Aún no hay resultados. Lanza un escaneo desde la sección Jobs.
                    </div>
                ) : (
                    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {assets.map((asset: any) => (
                            <AssetCard key={asset.id} asset={asset} findingCount={getFindingCount(asset.id)} />
                        ))}
                    </div>
                )}
            </section>
        </div>
    );
}
