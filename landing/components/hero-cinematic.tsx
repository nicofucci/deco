"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { AiOrb } from "@/components/ai-orb";
import { LiveIntelligence } from "@/components/live-intelligence";

export function HeroCinematic() {
    return (
        <div className="relative w-full h-screen overflow-hidden flex flex-col">

            {/* 1. Cinematic Background Layer */}
            <div className="absolute inset-0 z-[-2]">
                <img src="/background-nebula.png" alt="Control Room" className="w-full h-full object-cover opacity-60 mix-blend-color-dodge" />
                <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/20 to-black" />
            </div>

            {/* 2. 3D Orb Layer */}
            <div className="absolute inset-0 z-0 opacity-80 pointer-events-none">
                <AiOrb />
            </div>

            {/* 3. Main Content Layer */}
            <div className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-4 mt-16">

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="mb-8"
                >
                    <div className="inline-block px-3 py-1 mb-4 rounded-full border border-ai-cyan/30 bg-ai-cyan/10 text-ai-cyan text-xs font-mono tracking-widest">
                        SYSTEM_ONLINE // V.3.0
                    </div>
                    <h1 className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-white to-neutral-500 mb-6 drop-shadow-[0_0_30px_rgba(255,255,255,0.2)]">
                        EL SISTEMA <br />
                        INMUNOLÓGICO <span className="text-ai-cyan">DIGITAL</span>
                    </h1>
                    <p className="text-lg md:text-xl text-neutral-300 max-w-2xl mx-auto leading-relaxed text-shadow-sm">
                        Ciberdefensa <span className="text-white font-bold">autónoma, distribuida y predictiva</span> para PYMEs.
                        <br />
                        Tu red piensa. Tu red actúa.
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 0.8 }}
                    className="flex flex-col md:flex-row gap-4 mb-20"
                >
                    <button className="px-8 py-4 bg-ai-cyan text-black font-bold text-lg rounded-sm hover:bg-white transition-all shadow-[0_0_30px_rgba(6,182,212,0.4)] clip-path-polygon">
                        VER DEMO EN VIVO
                    </button>
                    <button className="px-8 py-4 border border-ai-cyan/50 text-ai-cyan font-bold text-lg rounded-sm hover:bg-ai-cyan/10 transition-all">
                        QUIERO SER PARTNER
                    </button>
                </motion.div>

                {/* 4. Live Intelligence Panel (Bottom) */}
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8, duration: 0.8 }}
                    className="w-full"
                >
                    <LiveIntelligence />
                </motion.div>

            </div>

            {/* HUD Overlay Lines */}
            <div className="absolute top-0 left-0 w-full h-full pointer-events-none opacity-20">
                <div className="absolute top-8 left-8 w-64 h-[1px] bg-white" />
                <div className="absolute top-8 left-8 w-[1px] h-64 bg-white" />
                <div className="absolute top-8 right-8 w-64 h-[1px] bg-white" />
                <div className="absolute top-8 right-8 w-[1px] h-64 bg-white" />
                <div className="absolute bottom-8 left-8 w-64 h-[1px] bg-white" />
                <div className="absolute bottom-8 left-8 w-[1px] h-64 bg-white" />
                <div className="absolute bottom-8 right-8 w-64 h-[1px] bg-white" />
                <div className="absolute bottom-8 right-8 w-[1px] h-64 bg-white" />
            </div>

        </div>
    );
}
