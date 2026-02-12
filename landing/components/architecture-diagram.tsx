"use client";
import React from 'react';
import { motion } from 'framer-motion';

export function ArchitectureDiagram() {
    return (
        <div className="w-full py-20 bg-black relative overflow-hidden">
            <div className="max-w-7xl mx-auto px-4">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-matrix-bright to-cyan-500 mb-4">
                        Arquitectura Descentralizada
                    </h2>
                    <p className="text-neutral-400 max-w-2xl mx-auto">
                        Una red neuronal de defensa donde cada nodo es un sensor y un ejecutor.
                        Coordinación centralizada, ejecución local.
                    </p>
                </div>

                <div className="relative flex flex-col md:flex-row items-center justify-center gap-8 md:gap-20">

                    {/* Tower Node */}
                    <Node
                        title="TOWER"
                        subtitle="Orchestrator API"
                        icon="🏢"
                        color="border-cyan-500"
                        glow="shadow-[0_0_30px_rgba(14,165,233,0.3)]"
                    />

                    {/* Connection Lines (Animated) */}
                    <ConnectionLine />

                    {/* Agent Node */}
                    <Node
                        title="AGENT"
                        subtitle="Sensor & Executor"
                        icon="🛡️"
                        color="border-matrix-bright"
                        glow="shadow-[0_0_30px_rgba(0,255,65,0.3)]"
                    />

                    {/* Connection Lines (Animated) */}
                    <ConnectionLine />

                    {/* AI Node */}
                    <Node
                        title="S.I.N.A."
                        subtitle="Neural Intelligence"
                        icon="🧠"
                        color="border-purple-500"
                        glow="shadow-[0_0_30px_rgba(168,85,247,0.3)]"
                    />

                </div>
            </div>
        </div>
    );
}

function Node({ title, subtitle, icon, color, glow }: any) {
    return (
        <motion.div
            whileHover={{ scale: 1.05 }}
            className={`w-64 h-64 rounded-2xl bg-neutral-900/50 backdrop-blur-md border ${color} ${glow} flex flex-col items-center justify-center p-6 relative z-10`}
        >
            <div className="text-4xl mb-4">{icon}</div>
            <div className="text-2xl font-bold text-white mb-2">{title}</div>
            <div className="text-sm text-neutral-400 font-mono text-center">{subtitle}</div>

            {/* Corner Accents */}
            <div className={`absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 ${color}`} />
            <div className={`absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 ${color}`} />
            <div className={`absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 ${color}`} />
            <div className={`absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 ${color}`} />
        </motion.div>
    )
}

function ConnectionLine() {
    return (
        <div className="hidden md:flex flex-1 h-[2px] bg-neutral-800 relative w-24">
            <motion.div
                animate={{ x: [-100, 100], opacity: [0, 1, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="absolute top-0 left-0 h-full w-1/2 bg-gradient-to-r from-transparent via-white to-transparent"
            />
        </div>
    )
}
