"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getSystemHealth } from "@/lib/api";
import { CheckCircle, XCircle, Server, Database, Activity, AlertTriangle } from "lucide-react";

export default function SystemPage() {
    const router = useRouter();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [health, setHealth] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchHealth = async () => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) {
            router.push("/login");
            return;
        }
        try {
            const res = await getSystemHealth(key);
            setHealth(res);
            setError(null);
        } catch (e) {
            console.error(e);
            setError("Error al conectar con el sistema. Verifica que el Orchestrator esté activo.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHealth();
    }, [router]);

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <div className="text-slate-400 animate-pulse">Verificando sistema...</div>
            </div>
        );
    }

    if (error || !health) {
        return (
            <div className="rounded-lg border border-red-900/50 bg-red-900/20 p-6 text-center">
                <div className="flex justify-center mb-4">
                    <AlertTriangle className="h-10 w-10 text-red-500" />
                </div>
                <h3 className="text-lg font-medium text-red-400 mb-2">Error de Sistema</h3>
                <p className="text-slate-400">{error || "No se pudo obtener el estado del sistema."}</p>
                <button
                    onClick={() => { setLoading(true); fetchHealth(); }}
                    className="mt-4 px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-300 rounded-md transition-colors"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    const StatusCard = ({ title, status, icon: Icon }: any) => (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 flex items-center justify-between">
            <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-full ${status === 'ok' ? 'bg-green-900/20 text-green-500' : 'bg-red-900/20 text-red-500'}`}>
                    <Icon className="h-6 w-6" />
                </div>
                <div>
                    <h3 className="text-lg font-medium text-white">{title}</h3>
                    <p className="text-sm text-slate-500">Estado del servicio</p>
                </div>
            </div>
            <div className="flex items-center space-x-2">
                {status === 'ok' ? (
                    <CheckCircle className="h-6 w-6 text-green-500" />
                ) : (
                    <XCircle className="h-6 w-6 text-red-500" />
                )}
                <span className={`text-sm font-bold ${status === 'ok' ? 'text-green-500' : 'text-red-500'}`}>
                    {status?.toUpperCase() || "UNKNOWN"}
                </span>
            </div>
        </div>
    );

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Salud del Sistema</h1>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                <StatusCard title="Orchestrator Core" status={health.orchestrator} icon={Server} />
                <StatusCard title="Base de Datos" status={health.database} icon={Database} />
                <StatusCard title="Redis Cache" status={health.redis} icon={Activity} />
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 mt-8">
                <h3 className="text-lg font-medium text-white mb-4">Información de Versión</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="text-slate-400">Orchestrator Version:</div>
                    <div className="text-white font-mono">{health.version || "Unknown"}</div>
                    <div className="text-slate-400">Admin Panel Version:</div>
                    <div className="text-white font-mono">v0.1.0</div>
                    <div className="text-slate-400">Environment:</div>
                    <div className="text-white font-mono">{health.environment || "Production"}</div>
                </div>
            </div>
        </div>
    );
}
