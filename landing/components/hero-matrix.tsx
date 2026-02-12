"use client";
import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { cn } from '@/lib/utils'; // Assuming you have this utility
import { Terminal, Shield, Activity, Zap, Lock, Globe } from 'lucide-react';

export function HeroMatrix() {
    const { scrollY } = useScroll();
    const y1 = useTransform(scrollY, [0, 500], [0, 200]);
    const y2 = useTransform(scrollY, [0, 500], [0, -150]);
    const opacity = useTransform(scrollY, [0, 300], [1, 0]);

    return (
        <div className="relative h-screen w-full flex flex-col items-center justify-center overflow-hidden">

            {/* Content Container */}
            <div className="relative z-10 w-full max-w-7xl px-4 flex flex-col md:flex-row items-center gap-12 mt-20 md:mt-0">

                {/* Left: Copy */}
                <motion.div
                    style={{ y: y1, opacity }}
                    className="flex-1 text-left"
                >
                    <div className="inline-block px-3 py-1 mb-4 border border-matrix-bright/30 rounded-full bg-matrix-dim/20 backdrop-blur-sm">
                        <span className="text-matrix-bright font-mono text-xs tracking-widest uppercase type-animation">
                            System: Secure // Status: Online
                        </span>
                    </div>

                    <h1 className="text-5xl md:text-7xl font-bold leading-tight tracking-tighter text-white mb-6">
                        El Sistema Inmunológico <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-matrix-bright to-cyan-400">
                            Digital para PYMEs
                        </span>
                    </h1>

                    <p className="text-lg md:text-xl text-neutral-400 max-w-xl mb-8 leading-relaxed">
                        Ciberdefensa autónoma. Distribuida. Predictiva.
                        <br />
                        Protección 24/7 sin necesidad de un SOC humano.
                    </p>

                    <div className="flex gap-4">
                        <button className="group relative px-8 py-3 bg-matrix-bright text-black font-bold text-sm tracking-uppercase skew-x-[-10deg] hover:bg-white transition-colors duration-200">
                            <span className="block skew-x-[10deg]">VER DEMO</span>
                            <div className="absolute inset-0 border-2 border-white opacity-0 group-hover:opacity-100 group-hover:animate-ping" />
                        </button>
                        <button className="px-8 py-3 border border-neutral-700 text-white font-mono text-sm hover:border-matrix-bright hover:text-matrix-bright transition-colors duration-200">
                            QUIERO SER PARTNER
                        </button>
                    </div>
                </motion.div>

                {/* Right: Live Status Panel Mock */}
                <motion.div
                    style={{ y: y2 }}
                    className="flex-1 w-full max-w-lg hidden md:block"
                >
                    <LiveStatusPanel />
                </motion.div>
            </div>

        </div>
    );
}

function LiveStatusPanel() {
    return (
        <div className="w-full bg-black/80 backdrop-blur-md border border-neutral-800 rounded-lg overflow-hidden shadow-[0_0_50px_rgba(0,255,65,0.1)] font-mono text-xs">
            {/* Header */}
            <div className="bg-neutral-900 px-4 py-2 flex items-center justify-between border-b border-neutral-800">
                <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500" />
                </div>
                <div className="text-neutral-500">deco-tower-main</div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-neutral-900/50 p-3 rounded border border-neutral-800">
                        <div className="text-neutral-500 mb-1 flex items-center gap-2">
                            <Activity className="w-3 h-3 text-matrix-bright" /> AGENT_UPTIME
                        </div>
                        <div className="text-2xl text-white font-bold">99.9%</div>
                        <div className="text-[10px] text-matrix-bright mt-1">+0.4% this week</div>
                    </div>
                    <div className="bg-neutral-900/50 p-3 rounded border border-neutral-800">
                        <div className="text-neutral-500 mb-1 flex items-center gap-2">
                            <Shield className="w-3 h-3 text-cyan-400" /> THREATS_BLK
                        </div>
                        <div className="text-2xl text-white font-bold">14,203</div>
                        <div className="text-[10px] text-cyan-400 mt-1">Live updates</div>
                    </div>
                </div>

                {/* Terminal Log */}
                <div className="space-y-2 font-mono text-[10px]">
                    <div className="flex gap-2">
                        <span className="text-neutral-600">10:42:01</span>
                        <span className="text-cyan-500">INFO</span>
                        <span className="text-neutral-300">New agent registered (ID: agt_8x92)</span>
                    </div>
                    <div className="flex gap-2">
                        <span className="text-neutral-600">10:42:05</span>
                        <span className="text-yellow-500">WARN</span>
                        <span className="text-neutral-300">Port scan detected from 192.168.1.55</span>
                    </div>
                    <div className="flex gap-2">
                        <span className="text-neutral-600">10:42:06</span>
                        <span className="text-matrix-bright">SUCCESS</span>
                        <span className="text-neutral-300">Threat isolated automatically.</span>
                    </div>
                    <div className="flex gap-2 animate-pulse">
                        <span className="text-neutral-600">10:42:10</span>
                        <span className="text-purple-500">AI</span>
                        <span className="text-neutral-300">Analyzing pattern signatures...</span>
                    </div>
                </div>

                {/* Progress Bars */}
                <div className="space-y-3">
                    <div className="flex justify-between text-neutral-500">
                        <span>NETWORK_SCAN</span>
                        <span>84%</span>
                    </div>
                    <div className="h-1 w-full bg-neutral-800 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-matrix-bright to-cyan-500 w-[84%] animate-progress" />
                    </div>
                </div>

            </div>
        </div>
    )
}
