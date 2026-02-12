"use client";
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export function InteractiveDemo() {
    const [activeTab, setActiveTab] = useState('scan');

    const tabs = [
        { id: 'scan', label: 'Escaneo Activo' },
        { id: 'findings', label: 'Hallazgos' },
        { id: 'report', label: 'Reporte PDF' },
    ];

    return (
        <div className="w-full py-24 bg-neutral-950">
            <div className="max-w-5xl mx-auto px-4">
                <h2 className="text-3xl md:text-5xl font-bold text-center mb-6 text-white">
                    Prueba de Concepto <span className="text-matrix-bright">Live</span>
                </h2>
                <p className="text-neutral-400 text-center mb-12">
                    Experimenta la velocidad de Deco-Security. Sin registro.
                </p>

                <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-2xl">
                    {/* Tabs */}
                    <div className="flex border-b border-neutral-800">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex-1 py-4 text-sm font-medium transition-colors relative ${activeTab === tab.id ? 'text-white' : 'text-neutral-500 hover:text-neutral-300'}`}
                            >
                                {tab.label}
                                {activeTab === tab.id && (
                                    <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-matrix-bright" />
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Content Area */}
                    <div className="h-[400px] bg-black p-8 relative overflow-hidden font-mono text-sm">
                        <AnimatePresence mode='wait'>
                            {activeTab === 'scan' && (
                                <motion.div
                                    key="scan"
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                    className="space-y-2"
                                >
                                    <div className="text-matrix-bright">&gt; init_sequence --target=local_mesh</div>
                                    <div className="text-neutral-400">Scanning subnet 192.168.1.0/24...</div>
                                    <div className="text-neutral-400">Found host: 192.168.1.1 (Gateway) [Uptime: 45d]</div>
                                    <div className="text-neutral-400">Found host: 192.168.1.15 (Windows Server 2019) <span className="text-red-500">[VULN: CVE-2023-23415]</span></div>
                                    <div className="text-neutral-400">Found host: 192.168.1.42 (Printer) <span className="text-yellow-500">[WARN: Default Creds]</span></div>
                                    <div className="mt-4 text-matrix-bright animate-pulse">_ Scanning ports [||||||||||.....] 65%</div>
                                </motion.div>
                            )}
                            {activeTab === 'findings' && (
                                <motion.div
                                    key="findings"
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                >
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-4 border border-red-500/30 bg-red-500/10 rounded">
                                            <div className="text-red-500 font-bold mb-1">CRITICAL: RDP Exposed</div>
                                            <div className="text-neutral-400 text-xs">Host: 192.168.1.15 (Finance-DB)</div>
                                            <div className="mt-2 text-white bg-red-600 px-2 py-1 text-xs w-fit rounded">Fix Available</div>
                                        </div>
                                        <div className="p-4 border border-yellow-500/30 bg-yellow-500/10 rounded">
                                            <div className="text-yellow-500 font-bold mb-1">WARN: Weak Wifi Encryption</div>
                                            <div className="text-neutral-400 text-xs">SSID: "Office_Guest"</div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                            {activeTab === 'report' && (
                                <motion.div
                                    key="report"
                                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                                    className="flex flex-col items-center justify-center h-full text-center"
                                >
                                    <div className="w-16 h-20 border-2 border-white mb-4 rounded flex items-center justify-center bg-white/10">
                                        PDF
                                    </div>
                                    <h3 className="text-white text-lg font-bold mb-2">Reporte Ejecutivo Generado</h3>
                                    <p className="text-neutral-400 mb-6">El informe completo ha sido encriptado y enviado al vault.</p>
                                    <button className="px-6 py-2 bg-matrix-bright text-black font-bold rounded hover:bg-white transition">Descargar Sample</button>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Scanline overlay inside demo */}
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/20 pointer-events-none" style={{ backgroundSize: "100% 4px" }} />
                    </div>
                </div>
            </div>
        </div>
    );
}
