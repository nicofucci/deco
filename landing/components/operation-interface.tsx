"use client";
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export function OperationInterface() {
    const [activeTab, setActiveTab] = useState('scan');

    return (
        <div className="py-24 bg-gradient-to-b from-neutral-950 to-black">
            <div className="max-w-6xl mx-auto px-4">
                <div className="rounded-xl border border-neutral-800 bg-black overflow-hidden shadow-2xl">
                    {/* Top Bar */}
                    <div className="flex items-center px-4 py-3 bg-neutral-900/50 border-b border-neutral-800 gap-4">
                        <div className="flex gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500" />
                            <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500" />
                        </div>
                        <div className="flex-1 text-center text-xs font-mono text-neutral-500">DECO_SEC_OPS_TERMINAL // V.2.4.1</div>
                    </div>

                    {/* Tabs */}
                    <div className="flex border-b border-neutral-800 bg-neutral-950">
                        {['SCANNING', 'THREATS', 'REPORTS'].map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab.toLowerCase())}
                                className={`px-8 py-3 text-xs font-mono border-r border-neutral-900 transition-colors
                                ${activeTab === tab.toLowerCase() ? 'bg-neutral-900 text-white' : 'text-neutral-600 hover:text-neutral-400'}
                            `}
                            >
                                {tab}
                            </button>
                        ))}
                    </div>

                    {/* Content */}
                    <div className="h-[400px] p-8 font-mono text-sm relative">
                        <AnimatePresence mode="wait">
                            {activeTab === 'scanning' && (
                                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} key="scan">
                                    <div className="text-ai-cyan mb-4">&gt; INITIATING DEEP SCAN SEQUENCE...</div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-4 bg-neutral-900/30 border border-neutral-800 rounded">
                                            <div className="text-neutral-500 text-xs mb-2">TARGET_SUBNET</div>
                                            <div className="text-white">192.168.1.0/24 (Local Mesh)</div>
                                        </div>
                                        <div className="p-4 bg-neutral-900/30 border border-neutral-800 rounded">
                                            <div className="text-neutral-500 text-xs mb-2">ACTIVE_NODES</div>
                                            <div className="text-ai-neon">42 Devices Identified</div>
                                        </div>
                                    </div>
                                    <div className="mt-8">
                                        <div className="h-1 w-full bg-neutral-800 rounded overflow-hidden">
                                            <div className="h-full bg-ai-cyan w-[65%] animate-pulse" />
                                        </div>
                                        <div className="text-xs text-ai-cyan mt-2 text-right">65% COMPLETED</div>
                                    </div>
                                </motion.div>
                            )}
                            {/* Other tabs would go here */}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </div>
    );
}
