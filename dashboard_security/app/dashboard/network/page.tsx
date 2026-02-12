"use client";

import { useEffect, useState } from "react";
import { useClient } from "@/providers/ClientProvider";
import { getNetworkAssets, getVulnerabilities } from "@/lib/client-api";
import NetworkTopology from "@/components/NetworkTopology";
import {
    Wifi, Search, Clock, Laptop, Server, Printer, Smartphone, Activity, HelpCircle,
    Bug, ShieldAlert
} from "lucide-react";

const getDeviceIcon = (type?: string) => {
    const key = (type || "").toLowerCase();
    switch (key) {
        case "server":
            return <Server className="w-5 h-5" />;
        case "printer":
            return <Printer className="w-5 h-5" />;
        case "mobile":
        case "phone":
        case "smartphone":
            return <Smartphone className="w-5 h-5" />;
        case "laptop":
        case "workstation":
            return <Laptop className="w-5 h-5" />;
        case "network":
        case "router":
        case "switch":
            return <Activity className="w-5 h-5" />;
        default:
            return <HelpCircle className="w-5 h-5" />;
    }
};

export default function NetworkPage() {
    const { apiKey, clientInfo } = useClient();
    const [networkAssets, setNetworkAssets] = useState<any[]>([]);
    const [vulns, setVulns] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (apiKey && clientInfo?.id) {
            loadNetworkData();
        }
    }, [apiKey, clientInfo]);

    const loadNetworkData = async () => {
        setLoading(true);
        try {
            const [assetsData, vulnsData] = await Promise.all([
                getNetworkAssets(apiKey!, clientInfo.id),
                getVulnerabilities(apiKey!, clientInfo.id)
            ]);
            setNetworkAssets(assetsData);
            setVulns(vulnsData);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const criticalVulns = vulns.filter((v: any) => v.severity === 'critical');
    const highVulns = vulns.filter((v: any) => v.severity === 'high');

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-400">
                    <Wifi className="w-8 h-8 inline mr-3 text-cyan-400" />
                    Mi Red Local (X-RAY™)
                </h1>
                <div className="flex space-x-3">
                    <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-md border border-cyan-900/50 flex items-center shadow-lg transform hover:scale-105 transition-all">
                        <Clock className="w-4 h-4 mr-2" /> Historial
                    </button>
                    <button
                        onClick={loadNetworkData}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-lg flex items-center"
                    >
                        <Search className="w-4 h-4 mr-2" /> Actualizar Vista
                    </button>
                </div>
            </div>

            {/* Vulnerability Alert Section */}
            {(criticalVulns.length > 0 || highVulns.length > 0) && (
                <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-red-500/20 rounded-full animate-pulse">
                            <ShieldAlert className="w-8 h-8 text-red-500" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-white">¡Atención! Vulnerabilidades Detectadas</h3>
                            <p className="text-sm text-red-200">
                                Se han encontrado {criticalVulns.length} críticas y {highVulns.length} de alto riesgo en su red.
                            </p>
                        </div>
                    </div>
                    <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded shadow transition-colors">
                        Ver Detalles
                    </button>
                </div>
            )}

            {/* Topology View */}
            <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 shadow-xl backdrop-blur-sm">
                <h3 className="text-lg font-semibold text-slate-300 mb-6 flex items-center">
                    <Activity className="w-5 h-5 mr-2 text-blue-500" /> Topología Visual
                </h3>
                <div className="rounded-lg overflow-hidden border border-slate-700/50 bg-black/40">
                    <NetworkTopology assets={networkAssets} />
                </div>
                <div className="mt-4 flex space-x-6 text-sm text-slate-400 justify-center">
                    <span className="flex items-center"><span className="w-3 h-3 rounded-full bg-green-500 mr-2 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span> Nuevo</span>
                    <span className="flex items-center"><span className="w-3 h-3 rounded-full bg-slate-400 mr-2"></span> Estable</span>
                    <span className="flex items-center"><span className="w-3 h-3 rounded-full bg-red-500 mr-2 shadow-[0_0_8px_rgba(239,68,68,0.6)]"></span> En Riesgo</span>
                </div>
            </div>

            {/* Vulnerability List Simplified */}
            {vulns.length > 0 && (
                <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden shadow-xl">
                    <div className="px-6 py-4 border-b border-slate-800/50 bg-slate-900/80 flex justify-between items-center">
                        <h3 className="text-lg font-semibold text-slate-200 flex items-center">
                            <Bug className="w-5 h-5 mr-2 text-orange-400" /> Vulnerabilidades Activas
                        </h3>
                    </div>
                    <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {criticalVulns.map((v: any) => (
                            <div key={v.id} className="bg-red-950/30 border border-red-900/50 p-3 rounded flex items-start space-x-3">
                                <ShieldAlert className="w-5 h-5 text-red-500 mt-1 flex-shrink-0" />
                                <div>
                                    <div className="font-bold text-red-400 text-sm">{v.cve}</div>
                                    <div className="text-xs text-slate-400 mt-1">{v.description_short || "Sin descripción"}</div>
                                    <div className="mt-2 text-xs font-mono text-slate-500 bg-black/30 px-2 py-1 rounded inline-block">Score: {v.cvss_score}</div>
                                </div>
                            </div>
                        ))}
                        {highVulns.map((v: any) => (
                            <div key={v.id} className="bg-orange-950/30 border border-orange-900/50 p-3 rounded flex items-start space-x-3">
                                <Bug className="w-5 h-5 text-orange-500 mt-1 flex-shrink-0" />
                                <div>
                                    <div className="font-bold text-orange-400 text-sm">{v.cve}</div>
                                    <div className="text-xs text-slate-400 mt-1">{v.description_short || "Sin descripción"}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Assets Table */}
            <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden shadow-xl">

                <div className="px-6 py-4 border-b border-slate-800/50 bg-slate-900/80">
                    <h3 className="text-lg font-semibold text-slate-200">Inventario de Dispositivos</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-slate-950/80 text-xs text-slate-500 uppercase tracking-wider">
                            <tr>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">IP Address</th>
                                <th className="px-6 py-4">Hostname</th>
                                <th className="px-6 py-4">Device Details</th>
                                <th className="px-6 py-4">Network Info</th>
                                <th className="px-6 py-4">Open Ports</th>
                                <th className="px-6 py-4">Last Seen</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50 text-sm">
                            {loading ? (
                                <tr><td colSpan={7} className="px-6 py-12 text-center text-slate-500 animate-pulse">Cargando mapa de red...</td></tr>
                            ) : networkAssets.map((asset: any) => (
                                <tr key={asset.id} className="hover:bg-slate-800/40 transition-colors group">
                                    <td className="px-6 py-4">
                                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${asset.status === 'new' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                                            asset.status === 'at_risk' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                                asset.status === 'gone' ? 'bg-slate-700/50 text-slate-500 border-slate-600' :
                                                    'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                            }`}>
                                            {asset.status?.toUpperCase() || 'STABLE'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 font-mono text-cyan-400 font-medium group-hover:text-cyan-300">{asset.ip}</td>
                                    <td className="px-6 py-4 text-slate-300 font-medium">{asset.hostname || "Unknown"}</td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center space-x-3">
                                            <div className="p-2 bg-slate-800 rounded-lg text-slate-400 group-hover:bg-slate-700 group-hover:text-slate-200 transition-colors">
                                                {getDeviceIcon(asset.device_type)}
                                            </div>
                                            <div className="flex flex-col">
                                                <span className="capitalize text-slate-300">{asset.device_type}</span>
                                                <span className="text-xs text-slate-500">{asset.os_guess || "OS Unknown"}</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-xs">
                                        <div className="font-mono text-slate-400">{asset.mac || "NO MAC"}</div>
                                        <div className="text-slate-500 truncate max-w-[120px]" title={asset.mac_vendor}>{asset.mac_vendor}</div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-wrap gap-1.5">
                                            {asset.open_ports?.slice(0, 4).map((p: number) => (
                                                <span key={p} className="px-1.5 py-0.5 bg-slate-800/80 text-xs rounded text-slate-400 border border-slate-700">{p}</span>
                                            ))}
                                            {asset.open_ports?.length > 4 && <span className="text-xs text-slate-500 flex items-center">+{asset.open_ports.length - 4}</span>}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-slate-500 text-xs">
                                        {new Date(asset.last_seen).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                            {!loading && networkAssets.length === 0 && (
                                <tr>
                                    <td colSpan={7} className="px-6 py-16 text-center text-slate-500">
                                        <div className="flex flex-col items-center">
                                            <Wifi className="w-12 h-12 mb-4 text-slate-700" />
                                            <p className="text-lg font-medium text-slate-400">No hay dispositivos en tu red local.</p>
                                            <p className="text-sm text-slate-600 mt-1">Asegúrate de que el Agente esté activo y ejecutando X-RAY.</p>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
