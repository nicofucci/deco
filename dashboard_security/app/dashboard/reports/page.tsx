"use client";

import { useState, useEffect } from "react";
import { useClient } from "@/providers/ClientProvider";
import { getReportHistory, generatePDFReport } from "@/lib/client-api";
import { FileText, Download, RefreshCw, AlertCircle, Calendar, Shield, List } from "lucide-react";

export default function ReportsPage() {
    const { apiKey, clientInfo } = useClient();
    const [activeTab, setActiveTab] = useState<"history" | "generate">("history");
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Generation State
    const [genType, setGenType] = useState<"executive" | "technical">("executive");
    const [forceGen, setForceGen] = useState(false);

    const clientId = clientInfo?.id || clientInfo?.client?.id;
    const API_BASE = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "http://localhost:18001";

    const fetchHistory = async () => {
        if (!apiKey || !clientId) return;
        setLoading(true);
        try {
            const data = await getReportHistory(apiKey, clientId);
            setHistory(data);
        } catch (e) {
            console.error("Failed to load history", e);
            setError("No se pudo cargar el historial.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (activeTab === "history") {
            fetchHistory();
        }
    }, [apiKey, clientId, activeTab]);

    const handleGenerate = async () => {
        if (!apiKey || !clientId) return;
        setGenerating(true);
        setError(null);
        try {
            await generatePDFReport(apiKey, clientId, genType, forceGen);
            setActiveTab("history"); // Switch to history to see the new report
            await fetchHistory(); // Refresh list
        } catch (e: any) {
            console.error("Generation failed", e);
            setError(e.message || "Error al generar el reporte.");
        } finally {
            setGenerating(false);
        }
    };

    const downloadReport = (url: string) => {
        // Construct absolute URL if relative
        const fullUrl = url.startsWith("http") ? url : `${API_BASE}${url}`;
        window.open(fullUrl, "_blank");
    };

    if (!clientInfo) return <div className="p-8 text-center">Cargando información del cliente...</div>;

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Reportes y Cumplimiento</h1>
                    <p className="mt-1 text-sm text-slate-500">Gestione y descargue sus reportes de seguridad en PDF (Snapshot).</p>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-slate-200 dark:border-slate-700">
                <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                    <button
                        onClick={() => setActiveTab("history")}
                        className={`${activeTab === "history"
                                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                                : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
                            } whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium`}
                    >
                        <span className="flex items-center">
                            <List className="mr-2 h-4 w-4" />
                            Historial de Reportes
                        </span>
                    </button>
                    <button
                        onClick={() => setActiveTab("generate")}
                        className={`${activeTab === "generate"
                                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                                : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
                            } whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium`}
                    >
                        <span className="flex items-center">
                            <FileText className="mr-2 h-4 w-4" />
                            Generar Nuevo
                        </span>
                    </button>
                </nav>
            </div>

            {error && (
                <div className="rounded-md bg-red-50 p-4 dark:bg-red-900/20">
                    <div className="flex">
                        <AlertCircle className="h-5 w-5 text-red-400" />
                        <div className="ml-3">
                            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
                            <div className="mt-2 text-sm text-red-700 dark:text-red-300">{error}</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Content */}
            {activeTab === "history" && (
                <div className="space-y-4">
                    {loading ? (
                        <div className="py-12 text-center text-slate-500">Cargando historial...</div>
                    ) : history.length === 0 ? (
                        <div className="rounded-lg border-2 border-dashed border-slate-300 p-12 text-center dark:border-slate-700">
                            <FileText className="mx-auto h-12 w-12 text-slate-400" />
                            <h3 className="mt-2 text-sm font-medium text-slate-900 dark:text-white">No hay reportes</h3>
                            <p className="mt-1 text-sm text-slate-500">Genere su primer reporte snapshot para verlo aquí.</p>
                            <div className="mt-6">
                                <button
                                    onClick={() => setActiveTab("generate")}
                                    className="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
                                >
                                    Generar Reporte
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="overflow-hidden rounded-lg border border-slate-200 shadow dark:border-slate-700">
                            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
                                <thead className="bg-slate-50 dark:bg-slate-900">
                                    <tr>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">Fecha</th>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">Tipo</th>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">Scan Job</th>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">Activos / Hallazgos</th>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">Risk Score</th>
                                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">Estado</th>
                                        <th scope="col" className="relative px-6 py-3"><span className="sr-only">Descargar</span></th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-200 bg-white dark:divide-slate-700 dark:bg-slate-950">
                                    {history.map((report) => (
                                        <tr key={report.id}>
                                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-900 dark:text-slate-200">
                                                {new Date(report.created_at).toLocaleString()}
                                            </td>
                                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400 uppercase font-bold">
                                                {report.kind}
                                            </td>
                                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400 font-mono">
                                                {report.job_id ? report.job_id.substring(0, 8) : "N/A"}
                                            </td>
                                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                                {report.assets_count} / {report.findings_count}
                                            </td>
                                            <td className="whitespace-nowrap px-6 py-4 text-sm font-semibold text-slate-900 dark:text-white">
                                                {report.risk_score}/100
                                            </td>
                                            <td className="whitespace-nowrap px-6 py-4 text-sm">
                                                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${report.status === "ready" ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" :
                                                        report.status === "error" ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400" :
                                                            "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400"
                                                    }`}>
                                                    {report.status === "ready" ? "Listo" : report.status === "generating" ? "Generando" : "Error"}
                                                </span>
                                            </td>
                                            <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                                                {report.status === "ready" && report.pdf_url && (
                                                    <button
                                                        onClick={() => downloadReport(report.pdf_url)}
                                                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 flex items-center justify-end"
                                                    >
                                                        <Download className="mr-1 h-4 w-4" /> PDF
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {activeTab === "generate" && (
                <div className="max-w-2xl rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
                    <h2 className="mb-4 text-lg font-medium text-slate-900 dark:text-white">Generar Nuevo Snapshot</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Tipo de Reporte</label>
                            <select
                                value={genType}
                                onChange={(e) => setGenType(e.target.value as any)}
                                className="mt-1 block w-full rounded-md border-slate-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900 sm:text-sm"
                            >
                                <option value="executive">Ejecutivo (Resumen)</option>
                                <option value="technical">Técnico (Detallado)</option>
                            </select>
                        </div>

                        <div className="flex items-center">
                            <input
                                id="force-gen"
                                type="checkbox"
                                checked={forceGen}
                                onChange={(e) => setForceGen(e.target.checked)}
                                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900"
                            />
                            <label htmlFor="force-gen" className="ml-2 block text-sm text-slate-900 dark:text-slate-300">
                                Forzar regeneración (si ya existe para el último scan)
                            </label>
                        </div>

                        <div className="pt-4">
                            <button
                                onClick={handleGenerate}
                                disabled={generating}
                                className="inline-flex w-full justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                            >
                                {generating ? "Generando..." : "Generar PDF"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
