"use client";
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export function XRayFeature() {
    return (
        <div className="w-full py-20 bg-black/50 relative overflow-hidden backdrop-blur-sm">

            <div className="max-w-7xl mx-auto px-4 md:px-8 relative z-10 flex flex-col md:flex-row items-center gap-12">
                <div className="flex-1">
                    <h2 className="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-neutral-500 mb-6">
                        Scanner de Red X-RAY™
                    </h2>
                    <p className="text-neutral-400 text-lg mb-8">
                        Ve lo que otros ignoran. Nuestro motor de escaneo activo mapea tu topología completa en segundos, identificando dispositivos no gestionados, puertos abiertos y vulnerabilidades latentes.
                    </p>
                    <ul className="space-y-4">
                        {["Descubrimiento Capa 2/3", "Identificación de OS (Fingerprinting)", "Escaneo de Puertos", "Correlación de Vulnerabilidades"].map((item, i) => (
                            <motion.li
                                initial={{ opacity: 0, x: -20 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.1 }}
                                key={i} className="flex items-center gap-3 text-neutral-300"
                            >
                                <div className="h-2 w-2 rounded-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.8)]" />
                                {item}
                            </motion.li>
                        ))}
                    </ul>
                </div>

                <div className="flex-1 w-full relative h-[400px] bg-neutral-900/50 rounded-2xl border border-neutral-800 overflow-hidden flex items-center justify-center group">
                    <ScannerEffect />
                </div>
            </div>
        </div>
    )
}

const ScannerEffect = () => {
    return (
        <div className="relative w-full h-full flex items-center justify-center">
            {/* Radar Line */}
            <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                className="absolute w-[600px] h-[600px] bg-gradient-to-r from-transparent via-cyan-500/10 to-transparent blur-3xl opacity-50"
            />

            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#000_100%)] z-10" />

            {/* Nodes */}
            <div className="relative w-60 h-60 border border-cyan-500/20 rounded-full flex items-center justify-center">
                <div className="w-40 h-40 border border-cyan-500/40 rounded-full flex items-center justify-center relative">
                    <motion.div
                        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="w-4 h-4 bg-cyan-400 rounded-full shadow-[0_0_20px_rgba(34,211,238,1)]"
                    />

                    {/* Floating Nodes */}
                    <Node x={-50} y={-50} delay={0.5} />
                    <Node x={60} y={-20} delay={1.2} />
                    <Node x={-20} y={60} delay={2.0} />
                    <Node x={40} y={40} delay={2.5} />
                </div>
            </div>

            {/* Tech Decoration */}
            <div className="absolute bottom-4 left-4 text-[10px] font-mono text-cyan-500/50">
                STATUS: SCANNING<br />
                TARGET: 192.168.1.0/24<br />
                NODES: 42 DETECTED
            </div>
        </div>
    )
}

const Node = ({ x, y, delay }: { x: number, y: number, delay: number }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 3, delay, repeat: Infinity }}
            style={{ x, y }}
            className="absolute w-2 h-2 bg-purple-500 rounded-full shadow-[0_0_10px_rgba(168,85,247,0.8)]"
        />
    )
}
