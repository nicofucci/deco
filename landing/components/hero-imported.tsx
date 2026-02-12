"use client";
import React from 'react';
import { Zap, PlayCircle, Quote, ChevronDown } from 'lucide-react';
import { motion } from 'framer-motion';

export function HeroImported() {
    return (
        <section className="min-h-[90vh] flex flex-col items-center justify-center relative overflow-hidden px-6 pt-20">

            {/* 3D Element Container */}
            <div className="absolute inset-0 flex items-center justify-center opacity-60 -z-10 pointer-events-none">
                <div className="scene">
                    <div className="reactor">
                        <div className="ring"></div>
                        <div className="ring"></div>
                        <div className="ring"></div>
                        <div className="ring"></div>
                        <div className="core-sphere"></div>
                    </div>
                </div>
            </div>

            <div className="text-center max-w-4xl mx-auto space-y-8 mt-10 z-10">
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-900/10 text-emerald-400 text-xs tracking-widest font-mono mb-4 animate-pulse"
                >
                    <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                    <span>SYSTEM ACTIVE: MONITORING</span>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="text-5xl md:text-7xl font-semibold tracking-tight text-white leading-[1.1]"
                >
                    El Sistema Inmunitario<br />
                    <span className="text-gradient-cyber">Digital Autónomo</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="text-lg md:text-xl text-neutral-400 max-w-2xl mx-auto font-light leading-relaxed"
                >
                    <Quote className="inline align-text-bottom mr-1 w-4 h-4" />
                    <span className="italic">Si los atacantes usan inteligencia artificial, la defensa también debe usarla.</span>
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="flex flex-col md:flex-row items-center justify-center gap-4 pt-8"
                >
                    <button className="group relative px-8 py-3 bg-white text-black rounded-full font-medium text-sm overflow-hidden transition-all hover:bg-emerald-400 hover:shadow-[0_0_20px_rgba(16,185,129,0.4)]">
                        <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full group-hover:animate-shimmer"></div>
                        <span className="relative flex items-center gap-2">
                            Iniciar Defensa
                            <Zap className="w-4 h-4" />
                        </span>
                    </button>
                    <button className="px-8 py-3 rounded-full border border-white/10 text-white font-medium text-sm hover:bg-white/5 transition-all flex items-center gap-2">
                        <PlayCircle className="w-4 h-4" />
                        Ver Funcionamiento
                    </button>
                </motion.div>
            </div>

            {/* Scroll Indicator */}
            <motion.div
                animate={{ y: [0, 10, 0], opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
            >
                <span className="text-[10px] uppercase tracking-[0.2em] text-neutral-500">Scroll</span>
                <ChevronDown className="text-white w-4 h-4" />
            </motion.div>
        </section>
    );
}
