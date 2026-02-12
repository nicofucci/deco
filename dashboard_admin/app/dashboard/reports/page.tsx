"use client";

import { useEffect, useState } from "react";
import { getClients, generateReport, getReports } from "@/lib/api";
import { FileText, Download, Loader2, Calendar, Shield } from "lucide-react";
import { useI18n } from "@/lib/i18n";

const API_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "http://127.0.0.1:18001";

export default function ReportsPage() {
    const { t, language } = useI18n();
    const [clients, setClients] = useState<any[]>([]);
    const [reports, setReports] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedClient, setSelectedClient] = useState("");
    const [generating, setGenerating] = useState(false);
    const [lastReport, setLastReport] = useState<{ filename: string, download_url: string } | null>(null);

    useEffect(() => {
        async function loadData() {
            const key = localStorage.getItem("deco_admin_master_key");
            if (!key) return;
            try {
                const [clientsRes, reportsRes] = await Promise.all([
                    getClients(key),
                    getReports(key)
                ]);
                setClients(clientsRes);
                setReports(reportsRes);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    const handleGenerate = async (type: "executive" | "technical") => {
        if (!selectedClient) return;
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;

        setGenerating(true);
        setLastReport(null);
        try {
            const res = await generateReport(key, selectedClient, type, language);
            setLastReport(res);
            // Refresh reports list
            const updatedReports = await getReports(key);
            setReports(updatedReports);
        } catch (e) {
            alert("Error al generar reporte");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="p-8 space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-white mb-2">{t('reports_center')}</h1>
                <p className="text-slate-400">{t('reports_desc')}</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Generator Section */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                            <FileText className="mr-2 h-5 w-5 text-blue-400" />
                            {t('generate_new')}
                        </h2>
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-2">{t('select_client')}</label>
                                <select
                                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    value={selectedClient}
                                    onChange={(e) => setSelectedClient(e.target.value)}
                                    disabled={loading}
                                >
                                    <option value="">-- {t('select_client')} --</option>
                                    {clients.map((c) => (
                                        <option key={c.id} value={c.id}>{c.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="grid grid-cols-1 gap-4">
                                <button
                                    onClick={() => handleGenerate("executive")}
                                    disabled={!selectedClient || generating}
                                    className="flex items-center justify-between p-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all disabled:opacity-50"
                                >
                                    <div className="text-left">
                                        <span className="block font-medium text-white">{t('exec_report')}</span>
                                        <span className="text-xs text-slate-400">{t('exec_desc')}</span>
                                    </div>
                                    <FileText className="h-5 w-5 text-blue-400" />
                                </button>

                                <button
                                    onClick={() => handleGenerate("technical")}
                                    disabled={!selectedClient || generating}
                                    className="flex items-center justify-between p-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-all disabled:opacity-50"
                                >
                                    <div className="text-left">
                                        <span className="block font-medium text-white">{t('tech_report')}</span>
                                        <span className="text-xs text-slate-400">{t('tech_desc')}</span>
                                    </div>
                                    <FileText className="h-5 w-5 text-purple-400" />
                                </button>
                            </div>

                            {generating && (
                                <div className="flex items-center justify-center p-4 text-blue-400 bg-blue-900/10 rounded-lg">
                                    <Loader2 className="h-5 w-5 animate-spin mr-2" />
                                    {t('generating')}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Reports List Section */}
                <div className="lg:col-span-2">
                    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                        <div className="p-6 border-b border-slate-800">
                            <h2 className="text-xl font-semibold text-white flex items-center">
                                <Download className="mr-2 h-5 w-5 text-green-400" />
                                {t('history')}
                            </h2>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm text-slate-400">
                                <thead className="bg-slate-950 text-slate-200 uppercase font-medium">
                                    <tr>
                                        <th className="px-6 py-4">{t('clients')}</th>
                                        <th className="px-6 py-4">Tipo</th>
                                        <th className="px-6 py-4">{t('date')}</th>
                                        <th className="px-6 py-4">{t('severity')}</th>
                                        <th className="px-6 py-4 text-right">{t('action')}</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                    {reports.map((report) => (
                                        <tr key={report.id} className="hover:bg-slate-800/50 transition-colors">
                                            <td className="px-6 py-4 font-medium text-white">{report.client_name}</td>
                                            <td className="px-6 py-4">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${report.type.includes("Ejecutivo") ? "bg-blue-900/30 text-blue-400" : "bg-purple-900/30 text-purple-400"
                                                    }`}>
                                                    {report.type}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 flex items-center gap-2">
                                                <Calendar className="h-3 w-3" />
                                                {new Date(report.generated_at).toLocaleDateString(language === 'es' ? 'es-ES' : language === 'it' ? 'it-IT' : 'en-US')}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`flex items-center gap-1 ${report.severity === "Critical" ? "text-red-400" : "text-orange-400"
                                                    }`}>
                                                    <Shield className="h-3 w-3" />
                                                    {report.severity}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <a
                                                    href={`${process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "http://127.0.0.1:18001"}${report.download_url}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-md text-xs font-medium transition-colors border border-slate-700"
                                                >
                                                    <Download className="h-3 w-3 mr-1.5" />
                                                    PDF
                                                </a>
                                            </td>
                                        </tr>
                                    ))}
                                    {reports.length === 0 && (
                                        <tr>
                                            <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                                                No hay reportes generados recientemente.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
