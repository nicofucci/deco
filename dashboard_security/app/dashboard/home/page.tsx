"use client";

import { useEffect, useState } from "react";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Doughnut } from "react-chartjs-2";
import { ShieldAlert, Server, Activity, FileText } from "lucide-react";
import { useClient } from "@/providers/ClientProvider";
import { getFindings, getAssets, getJobs, getSpecializedFindings, getNetworkAssetsSummary, getPredictiveReport, getAutofixPlaybooks } from "@/lib/client-api";
import { Card } from "@/components/Card";
import { FindingsTable } from "@/components/FindingsTable";
import { useI18n } from "@/lib/i18n";
import { FleetAPI } from "@/lib/api/fleet";
import { DeviceHealthWidget } from "@/components/DeviceHealthWidget";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function HomePage() {
    const { apiKey, clientInfo, riskLevel } = useClient();
    const { t } = useI18n();

    const [stats, setStats] = useState({
        assets: 0,
        findings: 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
    });
    const [recentFindings, setRecentFindings] = useState<any[]>([]);
    const [specializedAlerts, setSpecializedAlerts] = useState<any[]>([]);
    const [networkSummary, setNetworkSummary] = useState<any>(null);
    const [predictiveScore, setPredictiveScore] = useState<any>(null);
    const [autofixPlaybooks, setAutofixPlaybooks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const [wtiSummary, setWtiSummary] = useState<any>(null);
    const [fleetAgents, setFleetAgents] = useState<any[]>([]);

    useEffect(() => {
        if (!apiKey || !clientInfo) return;

        const fetchData = async () => {
            try {
                // Fetch independently to allow partial loading
                const findingsRes = await getFindings(apiKey).catch(() => []);
                const assetsRes = await getAssets(apiKey).catch(() => []);
                const jobsRes = await getJobs(apiKey).catch(() => []);
                const specializedRes = await getSpecializedFindings(apiKey, clientInfo.id).catch(() => []);
                const summaryRes = await getNetworkAssetsSummary(apiKey, clientInfo.id).catch(() => null);
                const predictiveRes = await getPredictiveReport(apiKey, clientInfo.id).catch(() => null);
                const autofixRes = await getAutofixPlaybooks(apiKey, clientInfo.id).catch(() => []);
                const fleetRes = await FleetAPI.getMyAgents(clientInfo.id).catch(() => []);

                setFleetAgents(fleetRes); // Set Fleet Agents
                setNetworkSummary(summaryRes); // Set Summary
                setPredictiveScore(predictiveRes?.score || 100);
                setAutofixPlaybooks(Array.isArray(autofixRes) ? autofixRes : []);

                const findings = Array.isArray(findingsRes) ? findingsRes : [];
                const assets = Array.isArray(assetsRes) ? assetsRes : [];
                const specialized = Array.isArray(specializedRes) ? specializedRes : [];

                setSpecializedAlerts(specialized);

                const critical = findings.filter((f: any) => f.severity?.toLowerCase() === "critical").length;
                const high = findings.filter((f: any) => f.severity?.toLowerCase() === "high").length;
                const medium = findings.filter((f: any) => f.severity?.toLowerCase() === "medium").length;
                const low = findings.filter((f: any) => f.severity?.toLowerCase() === "low").length;

                setStats({
                    assets: assets.length,
                    findings: findings.length,
                    critical,
                    high,
                    medium,
                    low,
                });

                setRecentFindings(findings.slice(0, 5));
            } catch (e) {
                console.error("Error fetching dashboard data", e);
            } finally {
                setLoading(false);
            }
        };

        // Fetch WTI independently
        import("@/lib/client-api").then(api => {
            api.getClientThreatSummary(apiKey, clientInfo.id)
                .then(res => setWtiSummary(res))
                .catch(err => console.error(err));
        });

        fetchData();
    }, [apiKey, clientInfo]);

    const chartData = {
        labels: ["Critical", "High", "Medium", "Low"],
        datasets: [
            {
                data: [stats.critical, stats.high, stats.medium, stats.low],
                backgroundColor: [
                    "rgba(239, 68, 68, 0.8)", // Red
                    "rgba(249, 115, 22, 0.8)", // Orange
                    "rgba(234, 179, 8, 0.8)", // Yellow
                    "rgba(59, 130, 246, 0.8)", // Blue
                ],
                borderColor: [
                    "rgba(239, 68, 68, 1)",
                    "rgba(249, 115, 22, 1)",
                    "rgba(234, 179, 8, 1)",
                    "rgba(59, 130, 246, 1)",
                ],
                borderWidth: 1,
            },
        ],
    };

    if (loading) return <div className="p-6">{t('loading_dashboard')}</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('security_summary')}</h1>
                <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-slate-500">{t('global_risk')}:</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${riskLevel === 'Crítico' ? 'bg-red-100 text-red-800' :
                        riskLevel === 'Alto' ? 'bg-orange-100 text-orange-800' :
                            riskLevel === 'Medio' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-blue-100 text-blue-800'
                        }`}>
                        {riskLevel.toUpperCase()}
                    </span>
                </div>
            </div>

            {/* WTI Widget (Task 2.2) */}
            {wtiSummary && wtiSummary.total_threats > 0 && (
                <div className="bg-slate-900 border border-blue-900 rounded-lg p-4 shadow-lg flex items-center justify-between relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                    <div className="flex items-start z-10">
                        <div className="p-2 bg-blue-900/30 rounded-full mr-4">
                            <Activity className="h-6 w-6 text-blue-400" />
                        </div>
                        <div>
                            <h3 className="text-blue-100 font-bold text-lg">Amenazas Globales Relevantes</h3>
                            <p className="text-blue-300/80 text-sm mt-1 max-w-xl">
                                Se ha detectado una amenaza global que coincide con uno de tus dispositivos (Total: {wtiSummary.total_threats}). Nuestro equipo está analizando las medidas recomendadas.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {specializedAlerts.length > 0 && (
                <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 rounded shadow-sm">
                    <div className="flex items-start">
                        <ShieldAlert className="w-5 h-5 text-red-500 mt-0.5 mr-3" />
                        <div>
                            <h3 className="text-red-800 dark:text-red-200 font-bold">¡Alertas de Infraestructura Crítica!</h3>
                            <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                                Se han detectado {specializedAlerts.length} problemas en dispositivos IoT/Infraestructura (ej. Firmware, RDP).
                                Contacte a su proveedor de seguridad.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Predictive Risk Widget (Task 2.1) */}
            {predictiveScore !== null && (
                <div className={`p-4 rounded-lg border shadow-sm flex items-center justify-between ${predictiveScore >= 80 ? 'bg-green-50 border-green-200 dark:bg-green-900/10 dark:border-green-800' :
                    predictiveScore >= 50 ? 'bg-orange-50 border-orange-200 dark:bg-orange-900/10 dark:border-orange-800' :
                        'bg-red-50 border-red-200 dark:bg-red-900/10 dark:border-red-800'
                    }`}>
                    <div>
                        <h3 className={`font-bold ${predictiveScore >= 80 ? 'text-green-800 dark:text-green-300' :
                            predictiveScore >= 50 ? 'text-orange-800 dark:text-orange-300' :
                                'text-red-800 dark:text-red-300'
                            }`}>Riesgo Predictivo del Sistema</h3>
                        <p className={`text-sm mt-1 ${predictiveScore >= 80 ? 'text-green-700 dark:text-green-400' :
                            predictiveScore >= 50 ? 'text-orange-700 dark:text-orange-400' :
                                'text-red-700 dark:text-red-400'
                            }`}>
                            {predictiveScore >= 80 ? "Tu red se comporta de forma estable." :
                                predictiveScore >= 50 ? "Se detectaron cambios inusuales en algunos dispositivos." :
                                    "Recomendamos una auditoría. Comportamiento anómalo detectado."}
                        </p>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="text-3xl font-black opacity-80">{predictiveScore}%</div>
                    </div>
                </div>
            )}

            {/* Autofix IA Widget (Task 3.1) */}
            {autofixPlaybooks.filter(p => p.status === 'pending').length > 0 && (
                <div className="bg-indigo-50 dark:bg-indigo-900/20 border-l-4 border-indigo-500 p-4 rounded shadow-sm">
                    <div className="flex items-start">
                        <div className="mr-3 mt-0.5">
                            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-500 text-xs font-bold text-white">AI</span>
                        </div>
                        <div>
                            <h3 className="text-indigo-800 dark:text-indigo-200 font-bold">Mitigaciones IA Disponibles</h3>
                            <p className="text-sm text-indigo-700 dark:text-indigo-300 mt-1">
                                Autofix IA ha generado {autofixPlaybooks.filter(p => p.status === 'pending').length} propuestas de mitigación para sus vulnerabilidades.
                                Contacte a su proveedor de servicios para su aprobación y ejecución.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Fleet Device Health Widget (Task 2.3) */}
            {fleetAgents.length > 0 && <DeviceHealthWidget agents={fleetAgents} />}

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card title={t('detected_assets')} value={stats.assets} icon={Server} />
                <Card title={t('total_findings')} value={stats.findings} icon={ShieldAlert} />
                <Card title={t('critical_findings')} value={stats.critical} icon={Activity} className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-900/10" />
                <Card title={t('high_findings')} value={stats.high} icon={Activity} className="border-orange-200 bg-orange-50 dark:border-orange-900 dark:bg-orange-900/10" />
            </div>

            {/* Network Activity Summary (Task 1.4) */}
            {networkSummary && (
                <div className="bg-white dark:bg-slate-900 p-4 rounded-lg shadow border border-slate-200 dark:border-slate-800">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                            <Activity className="h-5 w-5 text-blue-500" /> Actividad de Red en Tiempo Real
                        </h3>
                        <a href="/dashboard/network" className="text-sm text-blue-500 hover:text-blue-400">Ver detalle &rarr;</a>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded border border-slate-200 dark:border-slate-800 text-center">
                            <div className="text-xl font-bold text-green-500">{networkSummary.active}</div>
                            <div className="text-xs text-slate-500 uppercase">Activos Hoy</div>
                        </div>
                        <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded border border-slate-200 dark:border-slate-800 text-center">
                            <div className="text-xl font-bold text-indigo-500">{networkSummary.new_assets}</div>
                            <div className="text-xs text-slate-500 uppercase">Detectados Nuevos</div>
                        </div>
                        <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded border border-slate-200 dark:border-slate-800 text-center">
                            <div className="text-xl font-bold text-red-500">{networkSummary.at_risk}</div>
                            <div className="text-xs text-slate-500 uppercase">En Riesgo</div>
                        </div>
                        <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded border border-slate-200 dark:border-slate-800 text-center opacity-70">
                            <div className="text-xl font-bold text-slate-500">{networkSummary.gone}</div>
                            <div className="text-xs text-slate-500 uppercase">Desaparecidos</div>
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                <Card title={t('severity_distribution')} className="lg:col-span-1">
                    <div className="flex h-64 items-center justify-center">
                        <Doughnut data={chartData} options={{ maintainAspectRatio: false }} />
                    </div>
                </Card>
                <Card title={t('latest_findings')} className="lg:col-span-2">
                    <FindingsTable findings={recentFindings} />
                </Card>
            </div>
        </div>
    );
}
