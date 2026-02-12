"use client";
import React from 'react';
import { MonitorCheck, UserCheck } from 'lucide-react';
import { motion } from 'framer-motion';

export function ConsolePreview() {
    return (
        <section id="consoles" className="py-24 px-6 relative overflow-hidden">
            {/* Decorative glowing blobs */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-[100px] -z-10"></div>

            <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-12 items-center">

                <div className="md:w-1/2">
                    <span className="px-3 py-1 bg-white/10 rounded-full text-[10px] font-mono uppercase tracking-widest text-white mb-6 inline-block border border-white/10">Interface</span>
                    <h2 className="text-4xl font-semibold text-white tracking-tight mb-6">Control Total, Complejidad Cero</h2>
                    <p className="text-neutral-400 mb-8 font-light">
                        La interfaz de Deco Security traduce millones de logs de datos en una visualización clara y accionable. Diseñada para SOCs remotos y directores de seguridad.
                    </p>

                    <div className="space-y-4">
                        <div className="flex items-start gap-4 p-4 rounded-lg bg-white/5 border border-white/5">
                            <MonitorCheck className="text-emerald-400 mt-1 w-5 h-5" />
                            <div>
                                <h4 className="text-white text-sm font-medium">Consola Partner</h4>
                                <p className="text-xs text-neutral-500 mt-1">Gestión multi-tenant para escalar servicios de seguridad sin fricción.</p>
                            </div>
                        </div>
                        <div className="flex items-start gap-4 p-4 rounded-lg bg-white/5 border border-white/5">
                            <UserCheck className="text-blue-400 mt-1 w-5 h-5" />
                            <div>
                                <h4 className="text-white text-sm font-medium">Consola Cliente</h4>
                                <p className="text-xs text-neutral-500 mt-1">Visibilidad del ROI de seguridad y estado de salud de la red en tiempo real.</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Fake UI Interface */}
                <motion.div
                    initial={{ opacity: 0, x: 50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8 }}
                    className="md:w-1/2 w-full"
                >
                    <div className="relative rounded-xl bg-[#0F0F11] border border-white/10 shadow-2xl overflow-hidden aspect-video group">
                        {/* Top Bar */}
                        <div className="h-8 border-b border-white/10 flex items-center px-4 gap-2 bg-white/5">
                            <div className="w-2 h-2 rounded-full bg-red-500/50"></div>
                            <div className="w-2 h-2 rounded-full bg-yellow-500/50"></div>
                            <div className="w-2 h-2 rounded-full bg-green-500/50"></div>
                            <div className="ml-auto text-[10px] text-neutral-600 font-mono">DECO_OS_V2.4</div>
                        </div>
                        {/* UI Body */}
                        <div className="p-6 grid grid-cols-3 gap-4 h-full relative">
                            {/* Graph Column */}
                            <div className="col-span-2 space-y-4">
                                <div className="h-32 bg-white/5 rounded border border-white/5 p-3 relative overflow-hidden">
                                    <div className="absolute bottom-0 left-0 w-full h-16 bg-gradient-to-t from-emerald-500/20 to-transparent"></div>
                                    {/* Simple SVG Line Chart simulation */}
                                    <svg viewBox="0 0 100 40" className="w-full h-full stroke-emerald-500 fill-none stroke-2" preserveAspectRatio="none">
                                        <path d="M0,35 Q10,35 20,30 T40,20 T60,25 T80,10 T100,5" vectorEffect="non-scaling-stroke">
                                            <animate attributeName="d" dur="5s" repeatCount="indefinite" values="M0,35 Q10,35 20,30 T40,20 T60,25 T80,10 T100,5; M0,35 Q10,32 20,25 T40,15 T60,30 T80,5 T100,10; M0,35 Q10,35 20,30 T40,20 T60,25 T80,10 T100,5"></animate>
                                        </path>
                                    </svg>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="h-20 bg-white/5 rounded border border-white/5 p-3">
                                        <div className="text-[10px] text-neutral-500 uppercase">Threats Neutralized</div>
                                        <div className="text-2xl text-white font-mono mt-1">1,024</div>
                                    </div>
                                    <div className="h-20 bg-white/5 rounded border border-white/5 p-3">
                                        <div className="text-[10px] text-neutral-500 uppercase">System Health</div>
                                        <div className="text-2xl text-emerald-400 font-mono mt-1">99.9%</div>
                                    </div>
                                </div>
                            </div>
                            {/* Side Column */}
                            <div className="col-span-1 space-y-2">
                                <div className="h-full bg-white/5 rounded border border-white/5 p-3">
                                    <div className="space-y-2">
                                        <div className="w-full h-1 bg-white/10 rounded overflow-hidden">
                                            <div className="h-full bg-emerald-500 w-[70%] animate-pulse"></div>
                                        </div>
                                        <div className="w-full h-1 bg-white/10 rounded overflow-hidden">
                                            <div className="h-full bg-blue-500 w-[40%]"></div>
                                        </div>
                                        <div className="w-full h-1 bg-white/10 rounded overflow-hidden">
                                            <div className="h-full bg-purple-500 w-[90%]"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Radar overlay */}
                            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border border-white/5 rounded-full flex items-center justify-center opacity-30 pointer-events-none">
                                <div className="w-full h-1 bg-gradient-to-r from-transparent to-emerald-500 absolute top-1/2 left-0 -translate-y-1/2 animate-spin origin-center"></div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
