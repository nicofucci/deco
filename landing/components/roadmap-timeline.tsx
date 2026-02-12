"use client";
import React from 'react';
import { motion } from 'framer-motion';

export function RoadmapTimeline() {
    const steps = [
        { year: "Phase 1", title: "Fundación", items: ["Dashboard Core", "Agente V1 Windows", "Escaneo Básico"] },
        { year: "Phase 2", title: "Expansión", items: ["Consola Partner", "Reportes PDF", "RAG Knowledge Base"] },
        { year: "Now", title: "Inteligencia", items: ["IA Orquestadora", "Auto-Remediación", "Marketplace"], current: true },
        { year: "2026", title: "Futuro", items: ["IA Predictiva Real", "Red Colaborativa Mesh", "Zero-Day Hunter"] },
    ];

    return (
        <div className="w-full py-24 bg-black border-t border-neutral-900">
            <div className="max-w-6xl mx-auto px-4">
                <h2 className="text-4xl font-bold text-white mb-16 text-center text-transparent bg-clip-text bg-gradient-to-r from-neutral-200 to-neutral-600">
                    Roadmap de Evolución
                </h2>

                <div className="relative">
                    {/* Line */}
                    <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-neutral-800 transform -translate-x-1/2 hidden md:block" />

                    <div className="space-y-12">
                        {steps.map((step, idx) => (
                            <TimelineItem key={idx} {...step} index={idx} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function TimelineItem({ year, title, items, current, index }: any) {
    const isEven = index % 2 === 0;

    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className={`flex flex-col md:flex-row items-center justify-between gap-8 ${isEven ? '' : 'md:flex-row-reverse'}`}
        >
            {/* Content Side */}
            <div className="flex-1 w-full md:text-right">
                <div className={`p-6 rounded-2xl border ${current ? 'border-matrix-bright bg-matrix-dim/10' : 'border-neutral-800 bg-neutral-900'} ${isEven ? 'md:mr-8' : 'md:ml-8'}`}>
                    <div className={`text-sm font-mono mb-2 ${current ? 'text-matrix-bright' : 'text-neutral-500'}`}>{year}</div>
                    <h3 className="text-xl font-bold text-white mb-4">{title}</h3>
                    <ul className={`space-y-2 ${isEven ? 'md:text-left' : 'md:text-right'}`}> {/* Force inner text to align logically inside the box if desired, or keep centered. Let's align left for readability always inside box */}
                        {items.map((item: string, i: number) => (
                            <li key={i} className="text-neutral-400 text-sm flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${current ? 'bg-matrix-bright' : 'bg-neutral-600'}`} />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Center Dot */}
            <div className="relative z-10 flex-shrink-0">
                <div className={`w-4 h-4 rounded-full border-2 ${current ? 'border-matrix-bright bg-matrix-bright shadow-[0_0_20px_#00ff41]' : 'border-neutral-700 bg-black'}`} />
            </div>

            {/* Empty Side for balance */}
            <div className="flex-1 w-full hidden md:block" />
        </motion.div>
    )
}
