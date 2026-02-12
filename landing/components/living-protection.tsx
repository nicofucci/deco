"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlobeNetwork } from './globe-network'; // Reuse our 3D globe but darker

export function LivingProtection() {
    const [attacks, setAttacks] = useState<any[]>([]);

    useEffect(() => {
        // Simulate incoming attacks
        const interval = setInterval(() => {
            const id = Date.now();
            const x = Math.random() * 80 + 10; // %
            const y = Math.random() * 60 + 20; // %
            const type = Math.random() > 0.5 ? 'BLOCK' : 'SCAN';

            const newAttack = { id, x, y, type };
            setAttacks(prev => [...prev.slice(-4), newAttack]);
        }, 800);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="relative h-screen w-full bg-black overflow-hidden flex flex-col items-center justify-center">

            {/* Background Map (Abstract) */}
            <div className="absolute inset-0 opacity-20">
                <div className="w-full h-full bg-[url('https://upload.wikimedia.org/wikipedia/commons/e/ec/World_map_blank_without_borders.svg')] bg-no-repeat bg-center bg-contain filter invert brightness-50 contrast-200" style={{ backgroundSize: '80%' }} />
            </div>

            {/* Attack Overlay */}
            <div className="absolute inset-0 z-10 w-full h-full max-w-6xl mx-auto relative pointer-events-none">
                <AnimatePresence>
                    {attacks.map(attack => (
                        <motion.div
                            key={attack.id}
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 2 }}
                            className="absolute flex flex-col items-center justify-center"
                            style={{ left: `${attack.x}%`, top: `${attack.y}%` }}
                        >
                            {/* Ping Circle */}
                            <div className={`w-4 h-4 rounded-full animate-ping absolute ${attack.type === 'BLOCK' ? 'bg-red-500' : 'bg-ai-cyan'}`} />
                            <div className={`w-2 h-2 rounded-full relative z-10 ${attack.type === 'BLOCK' ? 'bg-red-500' : 'bg-ai-cyan'}`} />

                            {/* Connecting Line (Defense) */}
                            {attack.type === 'BLOCK' && (
                                <svg className="absolute w-[200px] h-[200px] overflow-visible pointer-events-none" style={{ left: '50%', top: '50%' }}>
                                    <motion.path
                                        d="M 0 0 L 100 -100"
                                        stroke="#06b6d4"
                                        strokeWidth="1"
                                        initial={{ pathLength: 0, opacity: 0 }}
                                        animate={{ pathLength: 1, opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        transition={{ duration: 0.5 }}
                                    />
                                </svg>
                            )}

                            {/* Label */}
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className="bg-black/80 backdrop-blur text-[10px] font-mono text-white px-2 py-1 mt-4 rounded border border-neutral-800 whitespace-nowrap"
                            >
                                {attack.type === 'BLOCK' ? 'THREAT_NEUTRALIZED' : 'NODE_SCANNED'}
                            </motion.div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* Copy Overlay */}
            <div className="relative z-20 text-center pointer-events-none">
                <motion.h2
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    className="text-4xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-b from-white to-neutral-700 mb-6"
                >
                    PROTECCIÓN VIVA
                </motion.h2>
                <p className="text-neutral-400 font-mono text-sm tracking-widest">
                    MIENTRAS OTROS DUERMEN, <span className="text-ai-cyan">DECO ACTÚA.</span>
                </p>
            </div>

        </div>
    );
}
