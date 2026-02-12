"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getClients, getPlans, subscribeClient, getSubscriptionStatus, getBillingPortal } from "@/lib/api";
import { CreditCard, Check, Shield, Zap, Star, ExternalLink, AlertTriangle } from "lucide-react";

export default function BillingPage() {
    const router = useRouter();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [clients, setClients] = useState<any[]>([]);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [plans, setPlans] = useState<any[]>([]);
    const [selectedClient, setSelectedClient] = useState("");
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [subscription, setSubscription] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [processing, setProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function loadData() {
            const key = localStorage.getItem("deco_admin_master_key");
            if (!key) {
                router.push("/login");
                return;
            }
            try {
                const [clientsRes, plansRes] = await Promise.all([
                    getClients(key),
                    getPlans(key)
                ]);
                setClients(clientsRes || []);
                setPlans(plansRes || []);
                setError(null);
            } catch (e) {
                console.error(e);
                setError("No se pudieron cargar los datos de facturación. Verifica la conexión.");
            } finally {
                setLoading(false);
            }
        }
        loadData();
    }, [router]);

    useEffect(() => {
        if (!selectedClient) {
            setSubscription(null);
            return;
        }
        async function fetchSub() {
            const key = localStorage.getItem("deco_admin_master_key");
            if (!key) return;
            try {
                const res = await getSubscriptionStatus(key, selectedClient);
                setSubscription(res);
            } catch (e) {
                console.error(e);
                // Non-critical error, maybe just no sub
            }
        }
        fetchSub();
    }, [selectedClient]);

    const handleSubscribe = async (planId: string) => {
        if (!selectedClient) return;
        if (!confirm(`¿Confirmar cambio al plan ${planId.toUpperCase()}?`)) return;

        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;

        setProcessing(true);
        try {
            await subscribeClient(key, selectedClient, planId);
            const res = await getSubscriptionStatus(key, selectedClient);
            setSubscription(res);
            alert("Suscripción actualizada correctamente.");
        } catch (e) {
            alert("Error al actualizar suscripción.");
        } finally {
            setProcessing(false);
        }
    };

    const handlePortal = async () => {
        if (!selectedClient) return;
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;

        try {
            const res = await getBillingPortal(key, selectedClient);
            if (res && res.url) {
                window.open(res.url, "_blank");
            } else {
                alert("No se pudo obtener la URL del portal.");
            }
        } catch (e) {
            alert("Error al abrir portal de facturación.");
        }
    };

    if (loading) {
        return (
            <div className="flex h-64 items-center justify-center">
                <div className="text-slate-400 animate-pulse">Cargando información de facturación...</div>
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
                    onClick={() => window.location.reload()}
                    className="mt-4 px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-300 rounded-md transition-colors"
                >
                    Reintentar
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-white mb-2">Facturación y Planes</h1>
                <p className="text-slate-400">Gestiona las suscripciones y métodos de pago de los clientes.</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <label className="block text-sm font-medium text-slate-400 mb-2">Seleccionar Cliente para Gestionar</label>
                <select
                    className="w-full max-w-md bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                    value={selectedClient}
                    onChange={(e) => setSelectedClient(e.target.value)}
                >
                    <option value="">-- Seleccione un cliente --</option>
                    {clients.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                </select>

                {subscription && (
                    <div className="mt-6 p-4 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                        <div>
                            <p className="text-sm text-slate-400">Plan Actual</p>
                            <p className="text-xl font-bold text-white capitalize">{subscription.plan}</p>
                            <p className="text-xs text-slate-500">Estado: <span className={subscription.status === 'active' ? 'text-green-400' : 'text-red-400'}>{subscription.status}</span></p>
                        </div>
                        {subscription.plan !== 'none' && (
                            <button
                                onClick={handlePortal}
                                className="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm transition-colors"
                            >
                                <CreditCard className="h-4 w-4 mr-2" />
                                Gestionar Pagos
                                <ExternalLink className="h-3 w-3 ml-2 opacity-50" />
                            </button>
                        )}
                    </div>
                )}
            </div>

            {selectedClient && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {plans.map((plan) => {
                        const isCurrent = subscription?.plan === plan.id;
                        const Icon = plan.id === 'starter' ? Shield : plan.id === 'pro' ? Zap : Star;

                        return (
                            <div key={plan.id} className={`relative rounded-2xl border p-6 flex flex-col ${isCurrent ? 'bg-blue-900/10 border-blue-500 shadow-lg shadow-blue-900/20' : 'bg-slate-900 border-slate-800'}`}>
                                {isCurrent && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                                        PLAN ACTUAL
                                    </div>
                                )}

                                <div className="mb-4">
                                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${isCurrent ? 'bg-blue-500/20 text-blue-400' : 'bg-slate-800 text-slate-400'}`}>
                                        <Icon className="h-6 w-6" />
                                    </div>
                                    <h3 className="text-xl font-bold text-white">{plan.name}</h3>
                                    <div className="mt-2 flex items-baseline text-white">
                                        <span className="text-3xl font-bold tracking-tight">
                                            {plan.price === 0 ? 'Custom' : `$${plan.price / 100}`}
                                        </span>
                                        {plan.price > 0 && <span className="text-sm text-slate-400 ml-1">/mes</span>}
                                    </div>
                                </div>

                                <ul className="space-y-3 mb-8 flex-1">
                                    {plan.features.map((feature: string) => (
                                        <li key={feature} className="flex items-start">
                                            <Check className="h-5 w-5 text-green-500 mr-2 shrink-0" />
                                            <span className="text-sm text-slate-300 capitalize">{feature.replace('_', ' ')}</span>
                                        </li>
                                    ))}
                                </ul>

                                <button
                                    onClick={() => handleSubscribe(plan.id)}
                                    disabled={isCurrent || processing}
                                    className={`w-full py-2.5 rounded-lg font-medium transition-colors ${isCurrent
                                        ? 'bg-slate-800 text-slate-400 cursor-default'
                                        : 'bg-blue-600 hover:bg-blue-500 text-white'
                                        }`}
                                >
                                    {isCurrent ? 'Activo' : 'Seleccionar Plan'}
                                </button>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
