"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, ShieldCheck, Search } from 'lucide-react';

export function DataStream() {
    const [logs, setLogs] = useState<any[]>([]);

    useEffect(() => {
        const templates = [
            { text: "Scanning endpoint 192.168.1.105...", icon: Search, color: "text-slate-400" },
            { text: "Heuristic pattern matched: RANSOM_V2", icon: SEARCH, color: "text-yellow-400" },
            { text: "Traffic anomaly detected on port 445", icon: Terminal, color: "text-orange-400" },
            { text: "Deco Shield engaged. Threat blocked.", icon: ShieldCheck, color: "text-ai-cyan" },
            { text: "Report sent to Master Console", icon: Terminal, color: "text-slate-400" },
        ];
        let i = 0;

        const interval = setInterval(() => {
            const item = templates[i % templates.length];
            setLogs(prev => [{ id: Date.now(), ...item }, ...prev.slice(0, 5)]);
            i++;
        }, 1500);

        return () => clearInterval(interval);
    }, []);

    // Fix icon ref
    const SEARCH = Search;

    return (
        <div className="w-full max-w-lg mx-auto bg-slate-900 border border-slate-800 rounded-lg overflow-hidden font-mono text-xs shadow-2xl">
            <div className="bg-slate-800 px-4 py-2 flex items-center gap-2 border-b border-slate-700">
                <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-500" />
                    <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
                </div>
                <div className="text-slate-400 ml-2">deco_agent_logs.sh</div>
            </div>
            <div className="p-4 h-64 overflow-hidden flex flex-col">
                <AnimatePresence mode="popLayout">
                    {logs.map(log => (
                        <motion.div
                            key={log.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0 }}
                            className={`flex items-start gap-3 mb-3 ${log.color}`}
                        >
                            <log.icon className="w-4 h-4 mt-0.5 shrink-0" />
                            <span>{'> ' + log.text}</span>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
}
