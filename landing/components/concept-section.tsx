"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Activity, BrainCircuit, ShieldAlert, Lock } from 'lucide-react';

export function ConceptSection() {
    return (
        <section id="concept" className="py-24 px-6 relative border-t border-white/5">
            <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center">

                {/* Text Side */}
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8 }}
                >
                    <h2 className="text-3xl md:text-4xl font-semibold text-white tracking-tight mb-6">
                        No es un producto.<br />Es un organismo vivo.
                    </h2>
                    <div className="space-y-6 text-neutral-400 font-light">
                        <p>
                            Deco Security rompe con la defensa estática tradicional. Funciona como el sistema inmunitario humano: observa continuamente, detecta anomalías en el tejido digital y neutraliza amenazas antes de que causen daño.
                        </p>
                        <p>
                            Mientras la seguridad convencional espera firmas de virus conocidos, <strong className="text-emerald-400 font-normal">Deco Core</strong> predice comportamientos maliciosos basándose en patrones de IA, aprendiendo y evolucionando con cada intento de ataque.
                        </p>
                        <ul className="space-y-3 mt-4">
                            <li className="flex items-center gap-3">
                                <Activity className="text-emerald-500 w-5 h-5" />
                                <span>Observación Continua</span>
                            </li>
                            <li className="flex items-center gap-3">
                                <BrainCircuit className="text-emerald-500 w-5 h-5" />
                                <span>Aprendizaje Automático</span>
                            </li>
                            <li className="flex items-center gap-3">
                                <ShieldAlert className="text-emerald-500 w-5 h-5" />
                                <span>Mitigación Contextual</span>
                            </li>
                        </ul>
                    </div>
                </motion.div>

                {/* Visual Side */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="relative h-[400px]"
                >
                    {/* Abstract Visualization of "Attack Blocked" */}
                    <div className="absolute inset-0 glass-panel rounded-2xl border border-white/10 overflow-hidden flex items-center justify-center">
                        {/* Background Image placeholder - keeping generic gradient for now to avoid external requests if image fails */}
                        <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/20 to-black opacity-50 mix-blend-screen"></div>

                        <div className="relative z-10 text-center space-y-4">
                            <div className="w-24 h-24 mx-auto border border-emerald-500/50 rounded-full flex items-center justify-center relative">
                                <div className="absolute inset-0 rounded-full animate-ping bg-emerald-500/20"></div>
                                <Lock className="text-4xl text-emerald-400 w-10 h-10" />
                            </div>
                            <div className="bg-black/80 px-4 py-2 rounded font-mono text-xs text-emerald-400 border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                                THREAT_DETECTED: BLOCKED
                            </div>
                        </div>
                        {/* Scanning Line */}
                        <div className="absolute w-full h-[2px] bg-emerald-500/50 shadow-[0_0_10px_#10b981] animate-scan top-0 left-0"></div>
                    </div>
                </motion.div>

            </div>
        </section>
    );
}
