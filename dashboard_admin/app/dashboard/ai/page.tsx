"use client";

import { useEffect, useState } from "react";
import { getAIRecommendations } from "@/lib/api";
import { Brain, AlertTriangle, ShieldCheck, TrendingUp } from "lucide-react";

export default function AIPage() {
    const [recommendations, setRecommendations] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRecs = async () => {
            const key = localStorage.getItem("deco_admin_master_key");
            if (!key) return;
            try {
                const res = await getAIRecommendations(key);
                setRecommendations(res);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchRecs();
    }, []);

    if (loading) return <div className="p-6 text-slate-400">Cargando motor de IA...</div>;

    return (
        <div className="space-y-8">
            <div className="flex items-center space-x-4">
                <div className="p-3 bg-purple-900/20 rounded-lg border border-purple-500/30">
                    <Brain className="h-8 w-8 text-purple-400" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-white">IA Predictiva</h1>
                    <p className="text-slate-400">Análisis de riesgos y patrones anómalos en tiempo real</p>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-slate-400 font-medium">Nivel de Riesgo Global</h3>
                        <TrendingUp className="h-5 w-5 text-orange-400" />
                    </div>
                    <div className="text-3xl font-bold text-white">Medio-Alto</div>
                    <div className="mt-2 text-sm text-slate-500">Basado en 12 patrones detectados</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-slate-400 font-medium">Amenazas Prevenidas</h3>
                        <ShieldCheck className="h-5 w-5 text-green-400" />
                    </div>
                    <div className="text-3xl font-bold text-white">85%</div>
                    <div className="mt-2 text-sm text-slate-500">Eficacia del modelo predictivo</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-slate-400 font-medium">Anomalías Activas</h3>
                        <AlertTriangle className="h-5 w-5 text-red-400" />
                    </div>
                    <div className="text-3xl font-bold text-white">{recommendations.length}</div>
                    <div className="mt-2 text-sm text-slate-500">Requieren atención inmediata</div>
                </div>
            </div>

            {/* Recommendations List */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <div className="p-6 border-b border-slate-800">
                    <h2 className="text-xl font-bold text-white">Predicciones y Recomendaciones</h2>
                </div>
                <div className="divide-y divide-slate-800">
                    {recommendations.map((rec, idx) => (
                        <div key={idx} className="p-6 hover:bg-slate-800/30 transition-colors">
                            <div className="flex items-start justify-between">
                                <div className="space-y-1">
                                    <div className="flex items-center space-x-2">
                                        <span className="px-2 py-1 bg-purple-900/30 text-purple-400 text-xs font-bold rounded uppercase">
                                            {rec.cliente}
                                        </span>
                                        <span className="text-sm text-slate-500">{rec.fecha}</span>
                                    </div>
                                    <h3 className="text-lg font-semibold text-white">{rec.tipo}</h3>
                                    <p className="text-slate-400 text-sm mt-2">{rec.recomendacion}</p>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm text-slate-400 mb-1">Probabilidad</div>
                                    <div className={`text-2xl font-bold ${rec.probabilidad > 0.9 ? 'text-red-400' :
                                            rec.probabilidad > 0.7 ? 'text-orange-400' : 'text-yellow-400'
                                        }`}>
                                        {(rec.probabilidad * 100).toFixed(0)}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                    {recommendations.length === 0 && (
                        <div className="p-8 text-center text-slate-500">
                            No se han detectado patrones de riesgo por el momento.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
