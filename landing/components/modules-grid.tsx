"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Radio, Lock, FileText, Zap, Globe } from 'lucide-react';

export function ModulesGrid() {
    const modules = [
        { title: "Radiografía Express", status: "ACTIVE", icon: <Radio />, color: "text-ai-cyan" },
        { title: "Hardening Playbook", status: "READY", icon: <Lock />, color: "text-ai-neon" },
        { title: "Auditoría Completa", status: "IDLE", icon: <FileText />, color: "text-ai-violet" },
        { title: "Vulnerability Hub", status: "SCANNING", icon: <Activity />, color: "text-red-400" },
        { title: "Jobs & Workers", status: "Running", icon: <Zap />, color: "text-yellow-400" },
        { title: "Túneles Seguros", status: "CONNECTED", icon: <Globe />, color: "text-blue-400" },
    ];

    return (
        <div className="py-24 bg-neutral-950/50">
            <div className="max-w-7xl mx-auto px-4">
                <h2 className="text-3xl font-bold mb-12 text-center">Módulos Operativos</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {modules.map((mod, idx) => (
                        <ModuleCard key={idx} {...mod} index={idx} />
                    ))}
                </div>
            </div>
        </div>
    );
}

function ModuleCard({ title, status, icon, color, index }: any) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="group relative p-6 bg-black border border-neutral-800 rounded-xl overflow-hidden hover:border-neutral-700 transition-colors"
        >
            {/* Hover Pulse Background */}
            <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            {/* Top HUD Line */}
            <div className="flex justify-between items-start mb-6">
                <div className={`p-3 rounded-lg bg-neutral-900 ${color}`}>
                    {React.cloneElement(icon, { size: 20 })}
                </div>
                <div className="text-[10px] font-mono border border-neutral-800 px-2 py-1 rounded text-neutral-500 group-hover:text-white group-hover:border-neutral-600 transition-colors">
                    {status}
                </div>
            </div>

            <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
            <p className="text-sm text-neutral-500">Módulo de defensa activa integrado.</p>

            {/* Bottom Decoration */}
            <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-neutral-800 to-transparent group-hover:via-ai-cyan/50 transition-all" />
        </motion.div>
    )
}
