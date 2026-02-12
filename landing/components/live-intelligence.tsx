"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Activity, Users, Clock, AlertTriangle, Terminal, Globe } from 'lucide-react';

export function LiveIntelligence() {
    const [events, setEvents] = useState([
        { id: 1, type: "info", text: "Agent agt_8x92 registered (Windows 11)" },
        { id: 2, type: "warn", text: "Port scan DETECTED: 192.168.1.55" },
        { id: 3, type: "success", text: "Hardening applied: SMB Signing Enabled" },
    ]);

    useEffect(() => {
        const interval = setInterval(() => {
            const newEvents = [
                "Vulnerability CVE-2023-4451 correlated",
                "New host discovered: Printer_Main",
                "Brute force blocked: 10.0.0.5",
                "Report generated: Executive PDF",
                "Agent auto-update completed"
            ];
            const randomEvent = newEvents[Math.floor(Math.random() * newEvents.length)];
            const type = randomEvent.includes("blocked") || randomEvent.includes("Vulnerability") ? "warn" : (randomEvent.includes("applied") ? "success" : "info");

            setEvents(prev => [{ id: Date.now(), type, text: randomEvent }, ...prev.slice(0, 3)]);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="w-full max-w-7xl mx-auto px-4 mt-8 grid grid-cols-1 lg:grid-cols-4 gap-4 pointer-events-none">

            {/* Main Stats (Left) */}
            <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricBox label="AGENTS ONLINE" value="842" icon={<Activity className="text-ai-neon" />} color="text-ai-neon" />
                <MetricBox label="CLIENTS PROTECTED" value="126" icon={<Users className="text-ai-cyan" />} color="text-ai-cyan" />
                <MetricBox label="THREAT SIGNALS" value="38" icon={<AlertTriangle className="text-red-500 animate-pulse" />} color="text-red-500" />

                {/* Risk Score Gauge Mock */}
                <div className="bg-black/40 backdrop-blur-md border border-neutral-800 rounded-lg p-4 flex items-center justify-between pointer-events-auto hover:border-ai-cyan transition-colors">
                    <div>
                        <div className="text-[10px] text-neutral-500 font-mono tracking-widest mb-1">RISK SCORE</div>
                        <div className="text-2xl font-bold text-white font-mono">72<span className="text-xs text-neutral-600">/100</span></div>
                    </div>
                    <div className="relative w-12 h-12 flex items-center justify-center">
                        <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                            <path className="text-neutral-900" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="4" />
                            <path className="text-yellow-500" strokeDasharray="72, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="4" />
                        </svg>
                    </div>
                </div>
            </div>

            {/* Live Feed (Right) */}
            <div className="lg:col-span-1 bg-black/40 backdrop-blur-md border border-neutral-800 rounded-lg p-4 h-full flex flex-col pointer-events-auto hover:border-ai-cyan transition-colors overflow-hidden">
                <div className="flex items-center gap-2 mb-3 border-b border-neutral-800 pb-2">
                    <Terminal className="w-3 h-3 text-ai-cyan" />
                    <span className="text-[10px] font-mono text-ai-cyan">EVENT_STREAM // LIVE</span>
                </div>
                <div className="flex-1 flex flex-col gap-2 overflow-hidden">
                    <AnimatePresence mode="popLayout">
                        {events.map((e) => (
                            <motion.div
                                key={e.id}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="text-[10px] font-mono flex items-start gap-2"
                            >
                                <span className={`mt-0.5 w-1.5 h-1.5 rounded-full ${e.type === 'warn' ? 'bg-red-500' : (e.type === 'success' ? 'bg-ai-neon' : 'bg-ai-cyan')}`} />
                                <span className="text-neutral-300 leading-tight">{e.text}</span>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            </div>

            {/* Secondary Low-Level Metrics Row */}
            <div className="lg:col-span-4 grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                <MiniMetric label="VULNS (24H)" value="71" />
                <MiniMetric label="CRITICAL" value="6" color="text-red-500" />
                <MiniMetric label="MTTD" value="32s" />
                <MiniMetric label="MTTR" value="2m 14s" />
            </div>
        </div>
    );
}

function MetricBox({ label, value, icon, color }: any) {
    return (
        <div className="bg-black/40 backdrop-blur-md border border-neutral-800 rounded-lg p-4 flex flex-col justify-center pointer-events-auto hover:border-ai-cyan transition-colors group">
            <div className="flex justify-between items-start mb-2">
                <span className="text-[10px] text-neutral-500 font-mono tracking-widest group-hover:text-ai-cyan transition-colors">{label}</span>
                {React.cloneElement(icon, { className: `w-4 h-4 ${color}` })}
            </div>
            <div className={`text-3xl font-bold font-mono ${color}`}>{value}</div>
        </div>
    )
}

function MiniMetric({ label, value, color = "text-white" }: any) {
    return (
        <div className="flex items-center justify-between px-4 py-2 bg-neutral-900/30 rounded border border-neutral-800/50">
            <span className="text-[10px] text-neutral-500 font-mono">{label}</span>
            <span className={`font-mono font-bold text-sm ${color}`}>{value}</span>
        </div>
    )
}
