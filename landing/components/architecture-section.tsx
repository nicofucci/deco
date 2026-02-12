"use client";
import React from 'react';
import { Satellite, Cpu, LayoutDashboard, ScanEye, Sparkles, Share2, Eye } from 'lucide-react';
import { motion } from 'framer-motion';

export function ArchitectureSection() {
    const features = [
        { icon: ScanEye, color: "text-emerald-500", title: "X-Ray de Red", desc: "Visibilidad completa de dispositivos invisibles y flujo de datos." },
        { icon: Sparkles, color: "text-blue-400", title: "Self-Healing", desc: "El sistema propone correcciones automáticas ante configuraciones de riesgo." },
        { icon: Share2, color: "text-purple-400", title: "Inteligencia Colectiva", desc: "Si un nodo detecta una amenaza, todos los clientes se inmunizan al instante." },
        { icon: Eye, color: "text-orange-400", title: "IA Supervisora", desc: "Una segunda capa de IA que audita las decisiones del núcleo para evitar sesgos." },
    ];

    return (
        <section id="architecture" className="py-24 bg-neutral-950/50 relative">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center mb-16">
                    <span className="text-emerald-500 font-mono text-xs tracking-widest uppercase mb-2 block">
                        Arquitectura del Sistema
                    </span>
                    <h2 className="text-3xl md:text-5xl font-semibold text-white tracking-tight">
                        Tres Pilares de Defensa
                    </h2>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mb-24">
                    {/* Card 1: Agentes */}
                    <motion.div
                        whileHover={{ y: -5 }}
                        className="group glass-panel p-8 rounded-xl border border-white/5 hover:border-emerald-500/30 hover:bg-white/5 transition-all duration-500"
                    >
                        <div className="w-12 h-12 bg-white/5 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <Satellite className="text-2xl text-white w-6 h-6" />
                        </div>
                        <h3 className="text-xl font-semibold text-white mb-3">Agentes Distribuidos</h3>
                        <p className="text-sm text-neutral-400 leading-relaxed">
                            Sensores ultraligeros instalados en los sistemas. Sin IA pesada local. Actúan como nervios periféricos enviando telemetría constante al núcleo central.
                        </p>
                    </motion.div>

                    {/* Card 2: Core */}
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        className="group glass-panel p-8 rounded-xl border border-emerald-500/20 bg-emerald-900/5 hover:border-emerald-500/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.1)] transition-all duration-500 relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 p-4 opacity-20">
                            <Cpu className="text-6xl text-emerald-500 animate-spin-slow w-16 h-16" />
                        </div>
                        <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center mb-6 text-emerald-400">
                            <Cpu className="text-2xl w-6 h-6" />
                        </div>
                        <h3 className="text-xl font-semibold text-white mb-3">Deco Core Central</h3>
                        <p className="text-sm text-neutral-400 leading-relaxed">
                            El cerebro del sistema. IA local que analiza vulnerabilidades, predice vectores de ataque y genera acciones de mitigación en milisegundos.
                        </p>
                    </motion.div>

                    {/* Card 3: Consolas */}
                    <motion.div
                        whileHover={{ y: -5 }}
                        className="group glass-panel p-8 rounded-xl border border-white/5 hover:border-blue-500/30 hover:bg-white/5 transition-all duration-500"
                    >
                        <div className="w-12 h-12 bg-white/5 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <LayoutDashboard className="text-2xl text-white w-6 h-6" />
                        </div>
                        <h3 className="text-xl font-semibold text-white mb-3">Consolas de Control</h3>
                        <p className="text-sm text-neutral-400 leading-relaxed">
                            Interfaces adaptadas para Master, Partners y Clientes. Visibilidad total del ecosistema y gestión simplificada de incidentes complejos.
                        </p>
                    </motion.div>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {features.map((feat, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="glass-panel p-6 rounded-lg border border-white/5 hover:bg-white/5 transition-colors"
                        >
                            <feat.icon className={`${feat.color} text-2xl mb-4 w-6 h-6`} />
                            <h4 className="text-white font-medium mb-2">{feat.title}</h4>
                            <p className="text-xs text-neutral-500">{feat.desc}</p>
                        </motion.div>
                    ))}
                </div>

            </div>
        </section>
    );
}
