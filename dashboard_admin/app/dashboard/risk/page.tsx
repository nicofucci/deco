"use client";

import { useEffect, useState } from "react";
import { getRiskRadar, getNetworkTopology, getThreatIntel } from "@/lib/api";
import RiskRadar from "@/components/RiskRadar";
import NetworkMap from "@/components/NetworkMap";
import { Shield, AlertTriangle, Search, Globe } from "lucide-react";

export default function RiskPage() {
    const [radarData, setRadarData] = useState<any[]>([]);
    const [networkData, setNetworkData] = useState<{ nodes: any[], edges: any[] } | null>(null);
    const [loading, setLoading] = useState(true);

    // Threat Intel State
    const [ipQuery, setIpQuery] = useState("");
    const [intelResult, setIntelResult] = useState<any>(null);
    const [intelLoading, setIntelLoading] = useState(false);

    useEffect(() => {
        async function loadData() {
            const key = localStorage.getItem("deco_admin_master_key");
            if (!key) {
                setLoading(false);
                return;
            }

            try {
                const [radar, topology] = await Promise.all([
                    getRiskRadar(key),
                    getNetworkTopology(key)
                ]);
                setRadarData(radar);
                setNetworkData(topology);
            } catch (error) {
                console.error("Error loading risk data:", error);
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, []);

    const handleIntelSearch = async () => {
        if (!ipQuery) return;
        setIntelLoading(true);
        setIntelResult(null);
        const key = localStorage.getItem("deco_admin_master_key");
        if (key) {
            try {
                const res = await getThreatIntel(key, ipQuery);
                setIntelResult(res);
            } catch (e) {
                console.error(e);
                alert("Error al consultar Threat Intel");
            } finally {
                setIntelLoading(false);
            }
        }
    };

    if (loading) {
        return (
            <div className="p-8 text-white">
                <div className="animate-pulse flex space-x-4">
                    <div className="flex-1 space-y-6 py-1">
                        <div className="h-2 bg-slate-700 rounded"></div>
                        <div className="space-y-3">
                            <div className="grid grid-cols-3 gap-4">
                                <div className="h-2 bg-slate-700 rounded col-span-2"></div>
                                <div className="h-2 bg-slate-700 rounded col-span-1"></div>
                            </div>
                            <div className="h-2 bg-slate-700 rounded"></div>
                        </div>
                    </div>
                </div>
                <p className="mt-4 text-slate-400">Cargando análisis de riesgo...</p>
            </div>
        );
    }

    return (
        <div className="p-8 space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-white mb-2">Panel de Riesgo Avanzado</h1>
                <p className="text-slate-400">Visualización estratégica de amenazas y topología de red.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Radar Chart - Takes 1 column */}
                <div className="lg:col-span-1">
                    <RiskRadar data={radarData} />

                    <div className="mt-6 bg-slate-900/50 rounded-xl border border-slate-800 p-4">
                        <h3 className="text-lg font-semibold text-white mb-3">Recomendaciones Automáticas</h3>
                        <ul className="space-y-3">
                            <li className="flex items-start gap-3 text-sm text-slate-300">
                                <span className="text-yellow-500 mt-1">⚠️</span>
                                <span>Aumentar cobertura de agentes en clientes nuevos (actual: 33%).</span>
                            </li>
                            <li className="flex items-start gap-3 text-sm text-slate-300">
                                <span className="text-red-500 mt-1">🔥</span>
                                <span>Parchear vulnerabilidades críticas en <b>10.0.0.50</b>.</span>
                            </li>
                            <li className="flex items-start gap-3 text-sm text-slate-300">
                                <span className="text-blue-500 mt-1">ℹ️</span>
                                <span>Revisar configuración de puertos en <b>localhost</b>.</span>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Network Map - Takes 2 columns */}
                <div className="lg:col-span-2">
                    {networkData && (
                        <NetworkMap
                            initialNodes={networkData.nodes}
                            initialEdges={networkData.edges}
                        />
                    )}
                </div>
            </div >

            {/* Threat Intel Section */}
            < div className="mt-8 bg-slate-900 p-6 rounded-xl border border-slate-800" >
                <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                    <Globe className="mr-2 text-green-400" />
                    Threat Intelligence Lookup
                </h2>
                <div className="flex space-x-4 mb-6">
                    <input
                        type="text"
                        placeholder="Ingresa una IP (ej: 192.168.1.10)"
                        className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                        value={ipQuery}
                        onChange={(e) => setIpQuery(e.target.value)}
                    />
                    <button
                        onClick={handleIntelSearch}
                        disabled={intelLoading}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center"
                    >
                        {intelLoading ? "Buscando..." : <><Search className="w-4 h-4 mr-2" /> Consultar</>}
                    </button>
                </div>

                {
                    intelResult && (
                        <div className="bg-slate-950 rounded-lg p-6 border border-slate-800">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h3 className="text-lg font-bold text-white mb-1">{intelResult.ip}</h3>
                                    <p className="text-slate-400 text-sm">Proveedor: {intelResult.provider}</p>
                                </div>
                                <div className={`px-4 py-1 rounded-full text-sm font-bold uppercase ${intelResult.verdict === 'malicious' ? 'bg-red-500/20 text-red-400' :
                                    intelResult.verdict === 'suspicious' ? 'bg-yellow-500/20 text-yellow-400' :
                                        'bg-green-500/20 text-green-400'
                                    }`}>
                                    {intelResult.verdict}
                                </div>
                            </div>

                            <div className="mt-6 grid grid-cols-3 gap-4">
                                <div className="bg-slate-900 p-4 rounded-lg">
                                    <div className="text-slate-500 text-xs uppercase mb-1">Risk Score</div>
                                    <div className="text-2xl font-bold text-white">{intelResult.risk_score}/100</div>
                                </div>
                                <div className="bg-slate-900 p-4 rounded-lg col-span-2">
                                    <div className="text-slate-500 text-xs uppercase mb-1">Tags</div>
                                    <div className="flex flex-wrap gap-2">
                                        {intelResult.tags.length > 0 ? intelResult.tags.map((tag: string) => (
                                            <span key={tag} className="bg-slate-800 text-slate-300 px-2 py-1 rounded text-xs">{tag}</span>
                                        )) : <span className="text-slate-600 italic">Sin etiquetas</span>}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )
                }
            </div >
        </div >
    );
}
