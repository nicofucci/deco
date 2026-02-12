"use client";

import { useEffect, useState } from "react";
import { getGlobalStats } from "@/lib/api";
import { Shield, Activity, Users, AlertTriangle, Menu, Bell } from "lucide-react";

export default function MobilePage() {
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        async function load() {
            const key = localStorage.getItem("deco_admin_master_key");
            if (key) {
                try {
                    const res = await getGlobalStats(key);
                    setStats(res);
                } catch (e) {
                    console.error(e);
                }
            }
        }
        load();
    }, []);

    return (
        <div className="flex justify-center items-center min-h-screen bg-slate-950 p-4">
            <div className="w-[375px] h-[812px] bg-slate-900 rounded-[40px] border-8 border-slate-800 overflow-hidden relative shadow-2xl flex flex-col">
                {/* Notch */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-40 h-7 bg-slate-800 rounded-b-2xl z-20"></div>

                {/* Status Bar */}
                <div className="h-12 flex justify-between items-center px-6 pt-2 text-xs text-slate-400 z-10">
                    <span>9:41</span>
                    <div className="flex space-x-1">
                        <div className="w-4 h-4 bg-slate-700 rounded-full"></div>
                        <div className="w-4 h-4 bg-slate-700 rounded-full"></div>
                    </div>
                </div>

                {/* Header */}
                <div className="px-6 py-4 flex justify-between items-center">
                    <Menu className="text-white h-6 w-6" />
                    <Shield className="text-blue-500 h-8 w-8" />
                    <Bell className="text-white h-6 w-6" />
                </div>

                {/* Content */}
                <div className="flex-1 px-6 py-4 overflow-y-auto no-scrollbar">
                    <h1 className="text-2xl font-bold text-white mb-1">Hola, Admin</h1>
                    <p className="text-slate-400 mb-6">Resumen de seguridad</p>

                    <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl p-6 mb-6 shadow-lg shadow-blue-900/20">
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-blue-100 font-medium">Riesgo Global</span>
                            <Activity className="text-white h-5 w-5" />
                        </div>
                        <div className="text-4xl font-bold text-white mb-1">{stats?.global_risk_score || 42}</div>
                        <div className="text-blue-200 text-sm">Nivel Moderado</div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="bg-slate-800 rounded-2xl p-4">
                            <Users className="text-purple-400 h-6 w-6 mb-2" />
                            <div className="text-2xl font-bold text-white">{stats?.total_clients || 0}</div>
                            <div className="text-slate-400 text-xs">Clientes</div>
                        </div>
                        <div className="bg-slate-800 rounded-2xl p-4">
                            <AlertTriangle className="text-red-400 h-6 w-6 mb-2" />
                            <div className="text-2xl font-bold text-white">{stats?.active_threats || 0}</div>
                            <div className="text-slate-400 text-xs">Amenazas</div>
                        </div>
                    </div>

                    <h2 className="text-lg font-bold text-white mb-4">Actividad Reciente</h2>
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="flex items-center bg-slate-800/50 p-3 rounded-xl">
                                <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center mr-3">
                                    <AlertTriangle className="h-5 w-5 text-red-400" />
                                </div>
                                <div>
                                    <div className="text-white text-sm font-medium">Intento de acceso SSH</div>
                                    <div className="text-slate-500 text-xs">Hace {i * 5} min • 192.168.1.{10 + i}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Bottom Nav */}
                <div className="h-20 bg-slate-800/50 backdrop-blur-md flex justify-around items-center pb-4 px-6">
                    <div className="flex flex-col items-center text-blue-400">
                        <Shield className="h-6 w-6" />
                        <span className="text-[10px] mt-1">Inicio</span>
                    </div>
                    <div className="flex flex-col items-center text-slate-500">
                        <Activity className="h-6 w-6" />
                        <span className="text-[10px] mt-1">Alertas</span>
                    </div>
                    <div className="flex flex-col items-center text-slate-500">
                        <Users className="h-6 w-6" />
                        <span className="text-[10px] mt-1">Perfil</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
