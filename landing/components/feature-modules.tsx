"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, Eye, Zap, FileText, Database } from 'lucide-react';

export function FeatureModules() {
    const features = [
        {
            title: "Radiografía Express",
            desc: "Escaneo profundo de red en <60s. Detecta activos ocultos.",
            icon: <Eye className="w-6 h-6 text-cyan-400" />,
            color: "border-cyan-500/20"
        },
        {
            title: "Hardening Playbook",
            desc: "Recetas automáticas para cerrar brechas en Windows/Linux.",
            icon: <Lock className="w-6 h-6 text-matrix-bright" />,
            color: "border-matrix-bright/20"
        },
        {
            title: "Auditoría PDF",
            desc: "Generación instantánea de reportes ejecutivos y técnicos.",
            icon: <FileText className="w-6 h-6 text-purple-400" />,
            color: "border-purple-500/20"
        },
        {
            title: "Vulnerability Hub",
            desc: "Correlación de CVEs en tiempo real con tu inventario.",
            icon: <Database className="w-6 h-6 text-red-400" />,
            color: "border-red-500/20"
        },
        {
            title: "Jobs & Workers",
            desc: "Asigna tareas masivas a tu flota de agentes distribuida.",
            icon: <Zap className="w-6 h-6 text-yellow-400" />,
            color: "border-yellow-500/20"
        },
        {
            title: "Túneles Seguros & Mesh",
            desc: "Acceso remoto sin exposiciones públicas. Zero Trust.",
            icon: <Shield className="w-6 h-6 text-blue-400" />,
            color: "border-blue-500/20"
        },
    ];

    return (
        <div className="w-full py-20 bg-black relative z-10">
            <div className="max-w-7xl mx-auto px-4">
                <h2 className="text-3xl md:text-5xl font-bold text-center mb-16 text-white">
                    Módulos <span className="text-matrix-bright">Operativos</span>
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((feature, idx) => (
                        <FeatureCard key={idx} {...feature} index={idx} />
                    ))}
                </div>
            </div>
        </div>
    );
}

function FeatureCard({ title, desc, icon, color, index }: any) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5, boxShadow: "0 10px 30px -10px rgba(0,255,65,0.1)" }}
            className={`p-6 rounded-xl bg-neutral-900/40 backdrop-blur-sm border ${color} group cursor-default relative overflow-hidden`}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <div className="mb-4 p-3 bg-neutral-900/80 w-fit rounded-lg border border-neutral-800 group-hover:border-white/20 transition-colors">
                {icon}
            </div>

            <h3 className="text-xl font-bold text-white mb-2 group-hover:text-matrix-bright transition-colors font-mono">
                {title}
            </h3>

            <p className="text-neutral-400 text-sm leading-relaxed">
                {desc}
            </p>

            {/* Glitch Effect Element (Hidden by default, visible on hover) */}
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-matrix-bright font-mono">
                0x{Math.floor(Math.random() * 999)}F
            </div>
        </motion.div>
    )
}
