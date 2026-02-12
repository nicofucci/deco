"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAIRecommendations } from "@/lib/api";
import { BrainCircuit, AlertTriangle, ShieldAlert } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export default function AIPage() {
    const router = useRouter();
    const { t } = useI18n();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [recommendations, setRecommendations] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchRecommendations = async () => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) {
            router.push("/login");
            return;
        }
        try {
            const res = await getAIRecommendations(key);
            setRecommendations(res || []);
            setError(null);
        } catch (e) {
            console.error(e);
            setError("No se pudieron cargar las recomendaciones de IA. Verifica la conexión con el Orchestrator.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRecommendations();
    }, [router]);

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <div className="text-slate-400 animate-pulse">Cargando análisis predictivo...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="rounded-lg border border-red-900/50 bg-red-900/20 p-6 text-center">
                <div className="flex justify-center mb-4">
                    <AlertTriangle className="h-10 w-10 text-red-500" />
                </div>
                <h3 className="text-lg font-medium text-red-400 mb-2">Error de Carga</h3>
                <p className="text-slate-400">{error}</p>
                <button
                    onClick={() => { setLoading(true); fetchRecommendations(); }}
                    className="mt-4 px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-300 rounded-md transition-colors"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <BrainCircuit className="h-8 w-8 text-purple-500" />
                        {t('ai_predictive')}
                    </h1>
                    <p className="text-slate-400 mt-1">{t('ai_desc')}</p>
                </div>
                <span className="px-3 py-1 rounded-full bg-purple-900/30 text-purple-400 text-xs border border-purple-800">
                    {t('ai_model')}
                </span>
            </div>

            {recommendations.length > 0 ? (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {recommendations.map((rec, index) => (
                        <div key={index} className="bg-slate-900 border border-slate-800 rounded-lg p-6 hover:border-purple-500/50 transition-colors">
                            <div className="flex justify-between items-start mb-4">
                                <div className="bg-slate-800 rounded px-2 py-1 text-xs text-slate-300">
                                    {rec.cliente}
                                </div>
                                <div className={`flex items-center gap-1 text-sm font-bold ${rec.probabilidad > 0.9 ? "text-red-400" :
                                    rec.probabilidad > 0.7 ? "text-orange-400" : "text-yellow-400"
                                    }`}>
                                    <ShieldAlert className="h-4 w-4" />
                                    {(rec.probabilidad * 100).toFixed(0)}% {t('risk')}
                                </div>
                            </div>

                            <h3 className="text-lg font-semibold text-white mb-2">{rec.tipo}</h3>
                            <p className="text-slate-400 text-sm mb-4">{rec.recomendacion}</p>

                            <div className="flex items-center justify-between text-xs text-slate-500 pt-4 border-t border-slate-800">
                                <span>{t('detected')}: {rec.fecha}</span>
                                <span className="flex items-center gap-1 text-purple-400">
                                    <BrainCircuit className="h-3 w-3" />
                                    AI Confidence
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-12 text-center">
                    <BrainCircuit className="h-16 w-16 mx-auto mb-4 text-slate-700" />
                    <h3 className="text-lg font-medium text-white mb-2">{t('no_predictions')}</h3>
                    <p className="text-slate-400">El sistema de IA no ha detectado anomalías o patrones de riesgo recientes.</p>
                </div>
            )}
        </div>
    );
}
