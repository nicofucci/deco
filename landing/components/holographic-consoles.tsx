"use client";
import React from 'react';
import { motion } from 'framer-motion';

export function HolographicConsoles() {
    return (
        <div className="py-32 overflow-hidden relative">
            <div className="max-w-7xl mx-auto px-4 text-center">
                <h2 className="text-3xl md:text-5xl font-bold mb-16">
                    Interfaz de <span className="text-ai-cyan">Comando Central</span>
                </h2>

                <div className="relative h-[400px] md:h-[600px] w-full flex justify-center items-center perspective-1000">

                    {/* Left Screen (Partner) */}
                    <motion.div
                        initial={{ opacity: 0, rotateY: 45, x: -100 }}
                        whileInView={{ opacity: 0.5, rotateY: 30, x: -200 }}
                        transition={{ duration: 1 }}
                        className="absolute w-[500px] h-[300px] border border-ai-neon/30 bg-black/80 rounded-xl backdrop-blur-md hidden lg:flex items-center justify-center transform-style-3d shadow-[0_0_50px_rgba(16,185,129,0.1)]"
                    >
                        <div className="text-ai-neon font-mono">PARTNER_VIEW</div>
                    </motion.div>

                    {/* Right Screen (Client) */}
                    <motion.div
                        initial={{ opacity: 0, rotateY: -45, x: 100 }}
                        whileInView={{ opacity: 0.5, rotateY: -30, x: 200 }}
                        transition={{ duration: 1 }}
                        className="absolute w-[500px] h-[300px] border border-ai-violet/30 bg-black/80 rounded-xl backdrop-blur-md hidden lg:flex items-center justify-center transform-style-3d shadow-[0_0_50px_rgba(139,92,246,0.1)]"
                    >
                        <div className="text-ai-violet font-mono">CLIENT_VIEW</div>
                    </motion.div>

                    {/* Center Screen (Master) */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 50 }}
                        whileInView={{ opacity: 1, scale: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="relative z-10 w-full max-w-3xl aspect-video border border-ai-cyan/50 bg-black rounded-lg overflow-hidden shadow-[0_0_100px_rgba(6,182,212,0.15)] flex flex-col"
                    >
                        {/* Mock Header */}
                        <div className="h-8 border-b border-neutral-800 bg-neutral-900/50 flex items-center px-4 gap-2">
                            <div className="w-2 h-2 rounded-full bg-red-500" />
                            <div className="w-2 h-2 rounded-full bg-yellow-500" />
                            <div className="w-2 h-2 rounded-full bg-green-500" />
                        </div>
                        {/* Mock Body */}
                        <div className="flex-1 bg-neutral-950 p-8 grid grid-cols-3 gap-4">
                            <div className="col-span-2 h-32 bg-neutral-900/50 rounded border border-neutral-800" />
                            <div className="col-span-1 h-32 bg-neutral-900/50 rounded border border-neutral-800" />
                            <div className="col-span-3 h-48 bg-neutral-900/50 rounded border border-neutral-800" />
                        </div>
                    </motion.div>

                </div>
            </div>
        </div>
    );
}
