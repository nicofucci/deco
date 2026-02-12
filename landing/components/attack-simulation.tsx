"use client";
import React from 'react';
import { motion } from 'framer-motion';

export function AttackSimulation() {
    return (
        <div className="relative w-full py-20 bg-slate-950 flex flex-col items-center overflow-hidden">

            <div className="text-center mb-16 z-10 px-4">
                <h2 className="text-3xl md:text-5xl font-bold text-white mb-4">
                    DEFENSA <span className="text-red-500">ACTIVA</span> VS <span className="text-ai-cyan">REACTIVA</span>
                </h2>
                <p className="text-slate-400 max-w-2xl mx-auto">
                    Deco no espera a que el daño ocurra. Visualiza el ataque y lo intercepta en la capa de red.
                </p>
            </div>

            {/* Visual Simulation Area */}
            <div className="relative w-full max-w-5xl h-64 bg-slate-900/50 border border-slate-800 rounded-xl flex items-center justify-between px-8 md:px-20 overflow-hidden">

                {/* Grid Background */}
                <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>

                {/* Attacker (Left) */}
                <div className="relative z-10 flex flex-col items-center">
                    <div className="w-16 h-16 bg-red-500/10 border border-red-500 rounded-lg flex items-center justify-center mb-2">
                        <span className="text-2xl">💀</span>
                    </div>
                    <span className="text-red-500 font-mono text-sm">THREAT_ACTOR</span>
                </div>

                {/* Defender (Center - Dynamic Shield) */}
                <div className="relative z-10 h-full flex flex-col justify-center items-center">
                    <motion.div
                        animate={{ height: [0, 200, 200, 0] }}
                        transition={{ duration: 3, repeat: Infinity, repeatDelay: 1 }}
                        className="w-2 bg-ai-cyan shadow-[0_0_20px_#06b6d4] rounded-full"
                    />
                    <motion.div
                        animate={{ opacity: [0, 1, 1, 0] }}
                        transition={{ duration: 3, repeat: Infinity, repeatDelay: 1 }}
                        className="absolute bg-black/80 px-4 py-2 border border-ai-cyan text-ai-cyan font-mono text-xs rounded"
                    >
                        BLOCKING_PAYLOAD
                    </motion.div>
                </div>

                {/* Your Network (Right) */}
                <div className="relative z-10 flex flex-col items-center">
                    <div className="w-16 h-16 bg-blue-500/10 border border-blue-500 rounded-lg flex items-center justify-center mb-2">
                        <span className="text-2xl">🏢</span>
                    </div>
                    <span className="text-blue-500 font-mono text-sm">CORP_NETWORK</span>
                </div>

                {/* Attack Projectile */}
                <motion.div
                    className="absolute left-28 top-1/2 -translate-y-1/2 w-4 h-4 bg-red-500 rounded-full shadow-[0_0_10px_red]"
                    animate={{ x: [0, 250], opacity: [1, 1, 0, 0] }} // Stops at shield logic visually
                    transition={{ duration: 3, repeat: Infinity, repeatDelay: 1, ease: 'linear' }}
                />

            </div>
        </div>
    );
}
