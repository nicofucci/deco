"use client";

import { useEffect, useState } from "react";
import { getMe } from "@/lib/partner-api";

export default function ProfilePage() {
    const [partner, setPartner] = useState<any>(null);

    useEffect(() => {
        const fetchMe = async () => {
            const token = localStorage.getItem("deco_partner_api_key");
            if (!token) return;
            try {
                const res = await getMe(token);
                setPartner(res);
            } catch (e) {
                console.error(e);
            }
        };
        fetchMe();
    }, []);

    if (!partner) return <div className="p-6 text-slate-400">Cargando perfil...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Mi Perfil</h1>

            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 max-w-2xl">
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-400">Nombre</label>
                        <div className="mt-1 text-lg text-white">{partner.name}</div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400">Email</label>
                        <div className="mt-1 text-lg text-white">{partner.email}</div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400">Modo de Cuenta</label>
                        <div className="mt-1">
                            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${partner.account_mode === "full" ? "bg-green-900/30 text-green-300" : "bg-amber-900/30 text-amber-200"}`}>
                                {partner.account_mode === "full" ? "Full" : "Demo"}
                            </span>
                        </div>
                        {partner.account_mode === "demo" && (
                            <p className="text-xs text-amber-300 mt-1">Demo: límite 1 cliente / 1 agente.</p>
                        )}
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400">Miembro Desde</label>
                        <div className="mt-1 text-lg text-slate-300">{new Date(partner.created_at).toLocaleDateString()}</div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400">Estado de Cuenta</label>
                        <div className="mt-1">
                            <span className="inline-flex items-center rounded-full bg-green-900/30 px-2.5 py-0.5 text-xs font-medium text-green-400">
                                {partner.status.toUpperCase()}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
