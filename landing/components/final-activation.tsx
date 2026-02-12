"use client";
import React from 'react';
import { motion } from 'framer-motion';

export function AiVsAi() {
    return (
        <div className="h-screen w-full flex bg-black relative overflow-hidden">
            {/* Split Screen Effect visually */}

            {/* Left: Chaos (Red) */}
            <div className="w-1/2 h-full bg-neutral-900 border-r border-neutral-800 flex items-center justify-center relative overflow-hidden group">
                <div className="absolute inset-0 bg-[url('https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5eXl5/l41lI4bYmcsPJX9nk/giphy.gif')] opacity-10 mix-blend-overlay pointer-events-none" />
                <div className="relative z-10 text-center">
                    <div className="w-32 h-32 bg-red-600 blur-xl rounded-full absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-20 animate-pulse" />
                    <h2 className="text-4xl md:text-6xl font-black text-red-600 mb-4 font-mono glitch-text">C H A O S</h2>
                    <p className="text-red-400 font-mono text-sm max-w-xs mx-auto">IA Ofensiva.<br />Polimórfica.<br />Destructiva.</p>
                </div>
            </div>

            {/* Right: Order (Cyan) */}
            <div className="w-1/2 h-full bg-black flex items-center justify-center relative">
                <div className="w-32 h-32 bg-cyan-500 blur-3xl rounded-full absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-20" />
                <div className="relative z-10 text-center">
                    <h2 className="text-4xl md:text-6xl font-black text-cyan-400 mb-4 tracking-tighter">ORDER</h2>
                    <p className="text-cyan-200 font-sans text-sm max-w-xs mx-auto">IA Defensiva.<br />Predictiva.<br />Absoluta.</p>
                </div>
            </div>

            {/* Overlap Text */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 bg-black px-6 py-4 border border-neutral-700">
                <span className="text-white font-bold tracking-widest text-xl">VS</span>
            </div>
        </div>
    )
}

export function FinalActivation() {
    return (
        <div className="h-screen bg-black flex flex-col items-center justify-center relative">
            <div className="absolute inset-0 z-0 flex items-center justify-center opacity-30">
                <div className="w-[600px] h-[600px] border border-neutral-800 rounded-full animate-[spin_60s_linear_infinite]" />
                <div className="absolute w-[400px] h-[400px] border border-neutral-800 rounded-full animate-[spin_40s_linear_infinite_reverse]" />
            </div>

            <div className="relative z-10 text-center">
                <h2 className="text-white text-5xl md:text-7xl font-black mb-8 tracking-tighter">
                    El futuro no se protege solo.
                </h2>

                <button className="group relative px-12 py-6 bg-white text-black font-bold text-lg tracking-[0.2em] overflow-hidden hover:scale-105 transition-transform duration-300">
                    <span className="relative z-10 group-hover:text-white transition-colors">ACTIVAR SISTEMA</span>
                    <div className="absolute inset-0 bg-black translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-in-out" />
                </button>
            </div>

            <p className="absolute bottom-10 text-neutral-600 font-mono text-xs">Deco Security © 2025. All systems nominal.</p>
        </div>
    )
}
