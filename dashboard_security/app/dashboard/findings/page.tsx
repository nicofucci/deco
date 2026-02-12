"use client";

import { useEffect, useState } from "react";
import { useClient } from "@/providers/ClientProvider";
import { getFindings, getAssets } from "@/lib/client-api";
import { FindingsTable } from "@/components/FindingsTable";

export default function FindingsPage() {
    const { apiKey } = useClient();
    const [findings, setFindings] = useState([]);
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!apiKey) return;

        const fetchData = async () => {
            try {
                setError(null);
                const [findingsData, assetsData] = await Promise.all([
                    getFindings(apiKey),
                    getAssets(apiKey),
                ]);
                setFindings(findingsData);
                setAssets(assetsData);
            } catch (e) {
                console.error("Error fetching findings", e);
                setError("No pudimos cargar los hallazgos. Intenta de nuevo.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [apiKey]);

    if (loading) return <div className="p-6">Cargando hallazgos...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Hallazgos de Seguridad</h1>
            {error && <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">{error}</div>}
            {findings.length === 0 ? (
                <div className="rounded-md border border-dashed border-slate-300 p-6 text-sm text-slate-600 dark:border-slate-700 dark:text-slate-300">
                    Aún no hay resultados. Lanza un escaneo desde la sección Jobs.
                </div>
            ) : (
                <FindingsTable findings={findings} assets={assets} />
            )}
        </div>
    );
}
