"use client";
import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, Activity, Zap } from 'lucide-react';

export function PrecisionUI() {
    return (
        <div className="relative min-h-screen bg-neutral-900 flex items-center justify-center p-8 overflow-hidden">

            {/* Ambient glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-purple-900/20 rounded-full blur-[100px]" />

            <div className="relative z-10 w-full max-w-6xl grid md:grid-cols-2 gap-16 items-center">

                {/* Text Side */}
                <div className="order-2 md:order-1">
                    <div className="flex items-center gap-2 mb-4 text-purple-400 font-mono text-sm tracking-wider">
                        <Activity className="w-4 h-4" />
                        <span>PRECISIÓN QUIRÚRGICA</span>
                    </div>
                    <h2 className="text-5xl font-bold text-white mb-6 leading-tight">
                        Control Total.<br />
                        <span className="text-neutral-500">Cero Fricción.</span>
                    </h2>
                    <p className="text-neutral-400 text-lg mb-8 leading-relaxed">
                        Una interfaz diseñada no solo para verse bien, sino para operar a la velocidad del pensamiento. Cada micro-interacción confirma que el sistema está vivo y bajo tu mando.
                    </p>

                    <div className="grid grid-cols-2 gap-4">
                        <MetricBox label="TIEMPO DE RESPUESTA" value="0.4ms" />
                        <MetricBox label="FALSOS POSITIVOS" value="0%" />
                    </div>
                </div>

                {/* UI Visual Side (Floating Glass Panels) */}
                <div className="order-1 md:order-2 relative h-[500px]">
                    {/* Base Panel */}
                    <motion.div
                        initial={{ y: 20, opacity: 0 }}
                        whileInView={{ y: 0, opacity: 1 }}
                        transition={{ duration: 0.8 }}
                        className="absolute inset-0 bg-neutral-800/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6 shadow-2xl"
                    >
                        <div className="flex justify-between items-center mb-8 border-b border-white/5 pb-4">
                            <span className="text-white font-mono">SYSTEM_STATUS</span>
                            <div className="flex gap-2">
                                <div className="w-3 h-3 rounded-full bg-red-500/20" />
                                <div className="w-3 h-3 rounded-full bg-yellow-500/20" />
                                <div className="w-3 h-3 rounded-full bg-green-500" />
                            </div>
                        </div>

                        {/* Dummy Chart */}
                        <div className="flex items-end gap-2 h-32 mb-8">
                            {[40, 60, 30, 80, 50, 90, 70, 40, 60].map((h, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ height: 0 }}
                                    whileInView={{ height: `${h}%` }}
                                    transition={{ delay: i * 0.1, duration: 0.5 }}
                                    className="flex-1 bg-purple-500/50 rounded-t-sm hover:bg-purple-400 transition-colors cursor-crosshair"
                                />
                            ))}
                        </div>

                        <div className="flex gap-4">
                            <ActionButton icon={Shield} label="MITIGAR" active />
                            <ActionButton icon={Zap} label="AISLAR" />
                            <ActionButton icon={Lock} label="BLOQUEAR" />
                        </div>
                    </motion.div>

                    {/* Floating Overlay Card */}
                    <motion.div
                        initial={{ x: 50, y: -50, opacity: 0 }}
                        whileInView={{ x: 20, y: -20, opacity: 1 }}
                        transition={{ delay: 0.4, duration: 0.8 }}
                        className="absolute -right-4 -top-8 bg-black/80 backdrop-blur border border-purple-500/30 p-6 rounded-xl shadow-xl w-64"
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
                                <Zap className="w-5 h-5" />
                            </div>
                            <div>
                                <div className="text-white text-sm font-bold">Amenaza Detenida</div>
                                <div className="text-neutral-500 text-xs">Hace 2 segundos</div>
                            </div>
                        </div>
                        <div className="h-1 w-full bg-neutral-800 rounded-full mt-2 overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                whileInView={{ width: '100%' }}
                                transition={{ delay: 1, duration: 1 }}
                                className="h-full bg-purple-500"
                            />
                        </div>
                    </motion.div>
                </div>

            </div>
        </div>
    );
}

function MetricBox({ label, value }: any) {
    return (
        <div className="p-4 bg-white/5 rounded-lg border border-white/5 hover:border-purple-500/50 transition-colors group">
            <div className="text-xs text-neutral-500 mb-1 font-mono">{label}</div>
            <div className="text-2xl text-white font-bold group-hover:text-purple-400 transition-colors">{value}</div>
        </div>
    )
}

function ActionButton({ icon: Icon, label, active = false }: any) {
    return (
        <button className={`flex-1 flex flex-col items-center justify-center p-4 rounded-lg border transition-all
            ${active ? 'bg-purple-600 border-purple-500 text-white shadow-[0_0_15px_rgba(147,51,234,0.3)]' : 'bg-neutral-800 border-neutral-700 text-neutral-400 hover:bg-neutral-700'}
        `}>
            <Icon className="w-5 h-5 mb-2" />
            <span className="text-[10px] font-bold tracking-widest">{label}</span>
        </button>
    )
}
