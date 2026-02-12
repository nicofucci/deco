"use client";

import { useEffect, useState } from "react";
import { getGlobalStats } from "@/lib/api";
import { ShieldAlert, Activity, Globe } from "lucide-react";

export default function GlobalDashboardPage() {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    const fetchStats = async () => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;
        try {
            const res = await getGlobalStats(key);
            setStats(res);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 5000); // Real-time update
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-6 text-slate-400">Cargando inteligencia global...</div>;
    if (!stats) return <div className="p-6 text-red-400">Error al cargar datos.</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Globe className="h-6 w-6 text-blue-400" />
                Red Global Distribuida
            </h1>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-400">Amenazas Procesadas</p>
                            <p className="text-3xl font-bold text-white">{stats.total_threats_processed}</p>
                        </div>
                        <Activity className="h-8 w-8 text-blue-500" />
                    </div>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-400">Críticas Detectadas</p>
                            <p className="text-3xl font-bold text-red-500">{stats.severity_distribution.critical}</p>
                        </div>
                        <ShieldAlert className="h-8 w-8 text-red-500" />
                    </div>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-400">Alta Severidad</p>
                            <p className="text-3xl font-bold text-orange-500">{stats.severity_distribution.high}</p>
                        </div>
                        <ShieldAlert className="h-8 w-8 text-orange-500" />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Top Threats */}
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <h3 className="text-lg font-medium text-white mb-4">Top Amenazas Globales</h3>
                    <div className="space-y-3">
                        {stats.top_threats.length === 0 ? (
                            <p className="text-slate-500 text-sm">No hay datos suficientes aún.</p>
                        ) : (
                            stats.top_threats.map((t: any, i: number) => (
                                <div key={i} className="flex items-center justify-between p-3 bg-slate-950 rounded border border-slate-800">
                                    <span className="text-sm text-slate-300 font-mono">{t.title}</span>
                                    <span className="text-xs font-bold bg-red-900/30 text-red-400 px-2 py-1 rounded">
                                        {t.count}
                                    </span>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Severity Distribution */}
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
                    <h3 className="text-lg font-medium text-white mb-4">Distribución de Severidad</h3>
                    <div className="space-y-4">
                        {Object.entries(stats.severity_distribution).map(([severity, count]: [string, any]) => (
                            <div key={severity}>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-400 capitalize">{severity}</span>
                                    <span className="text-white">{count}</span>
                                </div>
                                <div className="w-full bg-slate-800 rounded-full h-2">
                                    <div
                                        className={`h-2 rounded-full ${severity === 'critical' ? 'bg-red-600' :
                                                severity === 'high' ? 'bg-orange-500' :
                                                    severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                                            }`}
                                        style={{ width: `${Math.min((count / (stats.total_threats_processed || 1)) * 100, 100)}%` }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
