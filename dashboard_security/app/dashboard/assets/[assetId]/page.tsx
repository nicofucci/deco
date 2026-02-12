"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useClient } from "@/providers/ClientProvider";
import { getAssets, getFindings } from "@/lib/client-api";
import { Card } from "@/components/Card";
import { FindingsTable } from "@/components/FindingsTable";
import { Server } from "lucide-react";

export default function AssetDetailPage() {
    const { assetId } = useParams();
    const { apiKey } = useClient();
    const [asset, setAsset] = useState<any>(null);
    const [findings, setFindings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!apiKey || !assetId) return;

        const fetchData = async () => {
            try {
                setError(null);
                const [assetsData, findingsData] = await Promise.all([
                    getAssets(apiKey),
                    getFindings(apiKey, assetId as string),
                ]);

                const foundAsset = assetsData.find((a: any) => a.id === assetId);
                setAsset(foundAsset);
                setFindings(findingsData);
            } catch (e) {
                console.error("Error fetching asset details", e);
                setError("No pudimos cargar el activo. Revisa tu conexión o intenta más tarde.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [apiKey, assetId]);

    if (loading) return <div className="p-6">Cargando detalles del activo...</div>;
    if (!asset) return <div className="p-6">Activo no encontrado.</div>;

    return (
        <div className="space-y-6">
            {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}
            <div className="flex items-center space-x-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-slate-200 dark:bg-slate-800">
                    <Server className="h-6 w-6 text-slate-600 dark:text-slate-300" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{asset.hostname || "Unknown Host"}</h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{asset.ip}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                <Card title="Puertos abiertos" value={asset.open_ports && asset.open_ports.length > 0 ? asset.open_ports.join(", ") : "N/A"} />
                <Card title="Último escaneo" value={asset.last_scan_at ? new Date(asset.last_scan_at).toLocaleString() : "N/A"} />
                <Card title="Total Hallazgos" value={findings.length} />
            </div>

            <div className="space-y-4">
                <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Hallazgos Asociados</h2>
                {findings.length === 0 ? (
                    <div className="rounded-md border border-dashed border-slate-300 p-4 text-sm text-slate-600 dark:border-slate-700 dark:text-slate-300">
                        Aún no hay hallazgos para este activo.
                    </div>
                ) : (
                    <FindingsTable findings={findings} />
                )}
            </div>
        </div>
    );
}
