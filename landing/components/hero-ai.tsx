"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Shield, Zap } from 'lucide-react';

export function HeroAI() {
    return (
        <div className="relative h-screen w-full flex flex-col items-center justify-center overflow-hidden px-4">

            {/* Central Content (Glass effect to pop against globe) */}
            <div className="relative z-10 text-center max-w-5xl mx-auto mt-[-50px] p-8 rounded-3xl bg-black/20 backdrop-blur-sm border border-white/5">
                {/* AI Core Visual - Kept but simplified or integrated */}
                <div className="mb-8 relative flex justify-center items-center">
                    {/* Core Orb */}
                    <div className="relative w-48 h-48 md:w-64 md:h-64">
                        <div className="absolute inset-0 rounded-full border border-ai-cyan/30 animate-[spin_10s_linear_infinite]" />
                        <div className="absolute inset-4 rounded-full border border-ai-violet/30 animate-[spin_15s_linear_infinite_reverse]" />
                        <div className="absolute inset-12 rounded-full bg-ai-cyan/10 blur-xl animate-pulse" />

                        {/* Center Core */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-24 h-24 bg-gradient-to-br from-ai-cyan to-ai-violet rounded-full blur-md opacity-50 animate-float" />
                        </div>
                    </div>
                </div>

                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="text-5xl md:text-8xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-neutral-500 mb-6"
                >
                    El Sistema Inmunológico <br /><span className="text-ai-cyan">Digital</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3, duration: 0.8 }}
                    className="text-xl text-neutral-400 max-w-2xl mx-auto mb-10 leading-relaxed"
                >
                    Ciberdefensa autónoma, distribuida y predictiva.
                    <br />
                    Tu red aprende, se adapta y reacciona en milisegundos.
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="flex flex-col md:flex-row gap-6 justify-center"
                >
                    <button className="px-8 py-4 bg-ai-cyan/10 border border-ai-cyan text-ai-cyan font-bold rounded-full hover:bg-ai-cyan hover:text-black transition-all shadow-[0_0_30px_rgba(6,182,212,0.2)]">
                        VER DEMO EN VIVO
                    </button>
                    <button className="px-8 py-4 border border-neutral-800 text-neutral-400 font-bold rounded-full hover:border-white hover:text-white transition-all">
                        QUIERO SER PARTNER
                    </button>
                </motion.div>
            </div>

            {/* Live Metrics Footer (HUD style) */}
            <div className="absolute bottom-12 w-full max-w-4xl flex justify-between gap-4 md:px-12 pointer-events-none">
                <Metric label="AGENTS ONLINE" value="842" icon={<Activity className="w-4 h-4 text-ai-neon" />} color="text-ai-neon" />
                <Metric label="JOBS RUNNING" value="12" icon={<Zap className="w-4 h-4 text-ai-violet" />} color="text-ai-violet" />
                <Metric label="THREAT SIGNALS" value="0" icon={<Shield className="w-4 h-4 text-ai-cyan" />} color="text-ai-cyan" />
            </div>
        </div>
    );
}

function Metric({ label, value, icon, color }: any) {
    return (
        <div className="flex items-center gap-3 bg-neutral-900/50 backdrop-blur-sm px-6 py-3 rounded-lg border border-neutral-800">
            {icon}
            <div className="flex flex-col">
                <span className={`text-xl font-mono font-bold ${color}`}>{value}</span>
                <span className="text-[10px] text-neutral-500 tracking-wider">{label}</span>
            </div>
        </div>
    )
}
