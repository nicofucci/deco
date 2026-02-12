"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Eye, Brain, ShieldAlert } from 'lucide-react';

export function ProcessFlow() {
    return (
        <div className="py-32 relative z-10">
            <div className="max-w-7xl mx-auto px-4">
                <h2 className="text-3xl md:text-4xl font-bold text-center mb-20 text-white">
                    Ciclo de Vida de <span className="text-ai-cyan">Defensa Autónoma</span>
                </h2>

                <div className="flex flex-col md:flex-row justify-center items-center gap-8 md:gap-0 relative">

                    {/* Connecting Line (Background) */}
                    <div className="hidden md:block absolute top-1/2 left-20 right-20 h-[2px] bg-neutral-800 -z-10" />

                    <ProcessNode
                        title="Sense"
                        subtitle="Agentes Distribuidos"
                        desc="Sensores ligeros recolectan telemetría en endpoint y red."
                        icon={<Eye className="w-8 h-8 text-ai-cyan" />}
                        delay={0}
                    />

                    <ProcessNode
                        title="Think"
                        subtitle="IA Orquestadora"
                        desc="Jarvis correlaciona eventos y detecta patrones anómalos."
                        icon={<Brain className="w-8 h-8 text-ai-violet" />}
                        delay={0.2}
                        highlight
                    />

                    <ProcessNode
                        title="Act"
                        subtitle="Respuesta Automática"
                        desc="Aislamiento de host, bloqueo de puertos y hardening."
                        icon={<ShieldAlert className="w-8 h-8 text-ai-neon" />}
                        delay={0.4}
                    />

                </div>
            </div>
        </div>
    );
}

function ProcessNode({ title, subtitle, desc, icon, delay, highlight }: any) {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay, duration: 0.5 }}
            className={`flex-1 max-w-sm p-8 rounded-2xl border bg-black/50 backdrop-blur-md relative group hover:-translate-y-2 transition-transform duration-300
                ${highlight ? 'border-ai-violet/50 shadow-[0_0_30px_rgba(139,92,246,0.1)]' : 'border-neutral-800'}
            `}
        >
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-6 bg-neutral-900 border border-neutral-800 group-hover:bg-white/5 transition-colors`}>
                {icon}
            </div>

            <div className="absolute top-8 right-8 text-xs font-mono text-neutral-600">0{delay * 10 + 1}</div>

            <h3 className="text-2xl font-bold text-white mb-1">{title}</h3>
            <div className="text-sm font-mono text-ai-cyan mb-4">{subtitle}</div>
            <p className="text-neutral-400 text-sm leading-relaxed">{desc}</p>
        </motion.div>
    )
}
