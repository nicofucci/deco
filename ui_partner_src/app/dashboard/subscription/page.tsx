"use client";

import { useEffect, useState } from "react";
import { getMe, getBillingSummary, buyPackage } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import { Check, AlertTriangle, ShoppingCart, Package, DollarSign } from "lucide-react";

export default function SubscriptionPage() {
    const [partner, setPartner] = useState<any>(null);
    const [billing, setBilling] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [buying, setBuying] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;

        try {
            const me = await getMe(token);
            setPartner(me);

            if (me.type === "FULL") {
                const bill = await getBillingSummary(token);
                setBilling(bill);
            }
        } catch (e) {
            console.error(e);
            setError("Error al cargar datos de suscripción");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleBuyPackage = async (type: "clients" | "agents") => {
        if (!confirm(`¿Confirmas la compra de un paquete de 10 ${type === "clients" ? "clientes" : "agentes"}? Se añadirá a tu facturación mensual.`)) {
            return;
        }

        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;

        setBuying(true);
        try {
            await buyPackage(token, type, 1);
            await fetchData(); // Refresh data
            alert("Paquete comprado exitosamente.");
        } catch (e: any) {
            alert("Error al comprar paquete: " + (e.response?.data?.detail || e.message));
        } finally {
            setBuying(false);
        }
    };

    if (loading) return <div className="p-6 text-slate-400">Cargando suscripción...</div>;

    if (partner?.type === "DEMO") {
        return (
            <div className="space-y-6">
                <h1 className="text-2xl font-bold text-white">Mi Suscripción</h1>
                <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-8 text-center">
                    <AlertTriangle className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-white mb-2">Modo DEMO Activo</h2>
                    <p className="text-slate-400 max-w-md mx-auto mb-6">
                        Estás utilizando una versión de prueba limitada a 1 cliente y 1 agente.
                        Tu periodo de prueba expira el {new Date(partner.demo_expires_at).toLocaleDateString()}.
                    </p>
                    <div className="bg-slate-900 p-4 rounded-lg inline-block text-left mb-6">
                        <h3 className="text-white font-medium mb-2">Beneficios del Plan FULL:</h3>
                        <ul className="space-y-2 text-slate-400 text-sm">
                            <li className="flex items-center"><Check className="h-4 w-4 text-green-500 mr-2" /> 20 Clientes incluidos</li>
                            <li className="flex items-center"><Check className="h-4 w-4 text-green-500 mr-2" /> 20 Agentes incluidos</li>
                            <li className="flex items-center"><Check className="h-4 w-4 text-green-500 mr-2" /> Posibilidad de ampliar límites</li>
                            <li className="flex items-center"><Check className="h-4 w-4 text-green-500 mr-2" /> Soporte prioritario</li>
                        </ul>
                    </div>
                    <div>
                        <button className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-bold transition-colors">
                            Contactar para Actualizar a FULL
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Gestión de Suscripción y Paquetes</h1>

            {/* Resumen de Facturación */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
                        <h2 className="text-lg font-medium text-white mb-4 flex items-center">
                            <Package className="h-5 w-5 mr-2 text-blue-500" />
                            Paquetes de Ampliación
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Paquete Clientes */}
                            <div className="bg-slate-950 border border-slate-800 rounded-lg p-5 hover:border-blue-500/50 transition-colors">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-white font-bold">Paquete de Clientes</h3>
                                        <p className="text-sm text-slate-400">+10 Clientes adicionales</p>
                                    </div>
                                    <span className="bg-blue-900/30 text-blue-400 text-xs px-2 py-1 rounded">150€ / mes</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <div className="text-sm text-slate-500">
                                        Adquiridos: <span className="text-white">{billing?.paquetes_clientes || 0}</span>
                                    </div>
                                    <button
                                        onClick={() => handleBuyPackage("clients")}
                                        disabled={buying}
                                        className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded text-sm font-medium disabled:opacity-50"
                                    >
                                        Comprar (+10)
                                    </button>
                                </div>
                            </div>

                            {/* Paquete Agentes */}
                            <div className="bg-slate-950 border border-slate-800 rounded-lg p-5 hover:border-green-500/50 transition-colors">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-white font-bold">Paquete de Agentes</h3>
                                        <p className="text-sm text-slate-400">+10 Agentes adicionales</p>
                                    </div>
                                    <span className="bg-green-900/30 text-green-400 text-xs px-2 py-1 rounded">10€ / mes</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <div className="text-sm text-slate-500">
                                        Adquiridos: <span className="text-white">{billing?.paquetes_agentes || 0}</span>
                                    </div>
                                    <button
                                        onClick={() => handleBuyPackage("agents")}
                                        disabled={buying}
                                        className="bg-green-600 hover:bg-green-500 text-white px-3 py-1.5 rounded text-sm font-medium disabled:opacity-50"
                                    >
                                        Comprar (+10)
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Facturación Mensual */}
                <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 h-fit">
                    <h2 className="text-lg font-medium text-white mb-4 flex items-center">
                        <DollarSign className="h-5 w-5 mr-2 text-yellow-500" />
                        Resumen Mensual
                    </h2>
                    <div className="space-y-3 text-sm">
                        <div className="flex justify-between text-slate-400">
                            <span>Plan Base (FULL)</span>
                            <span className="text-white">{formatCurrency(billing?.base_plan || 297)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span>Paquetes Clientes ({billing?.paquetes_clientes})</span>
                            <span className="text-white">{formatCurrency((billing?.paquetes_clientes || 0) * 150)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span>Paquetes Agentes ({billing?.paquetes_agentes})</span>
                            <span className="text-white">{formatCurrency((billing?.paquetes_agentes || 0) * 10)}</span>
                        </div>
                        <div className="border-t border-slate-800 pt-3 flex justify-between font-bold text-lg">
                            <span className="text-white">Total Mensual</span>
                            <span className="text-yellow-500">{formatCurrency(billing?.facturacion_total || 0)}</span>
                        </div>
                    </div>
                    <div className="mt-6 p-3 bg-slate-950 rounded border border-slate-800 text-xs text-slate-500 text-center">
                        La facturación se realiza automáticamente el día 1 de cada mes.
                    </div>
                </div>
            </div>
        </div>
    );
}
