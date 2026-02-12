"use client";
import React from 'react';

export function MissionTimeline() {
    const steps = [
        { year: "Phase 1 / FOUNDATION", title: "Dashboard Core & Agent V1", active: false },
        { year: "Phase 2 / EXPANSION", title: "Partner Portal & RAG Engine", active: false },
        { year: "Phase 3 / ACTIVE", title: "AI Orchestration & Auto-Remediation", active: true },
        { year: "Phase 4 / FUTURE", title: "Predictive Mesh & Zero-Day Hunter", active: false },
    ];

    return (
        <div className="py-24 bg-black border-t border-neutral-900">
            <div className="max-w-4xl mx-auto px-4">
                <h2 className="text-3xl font-bold mb-16 text-center text-neutral-500">MISION LOG</h2>

                <div className="relative border-l border-neutral-800 ml-4 md:ml-0 md:border-l-0 md:border-t md:flex md:justify-between md:pt-8">
                    {steps.map((step, idx) => (
                        <div key={idx} className="relative pl-8 pb-12 md:pl-0 md:pb-0 md:flex-1 md:text-center group">
                            {/* Dot */}
                            <div className={`absolute left-[-5px] top-0 w-2.5 h-2.5 rounded-full border md:left-1/2 md:top-[-37px] md:-translate-x-1/2 transition-all duration-500
                            ${step.active ? 'bg-ai-cyan border-ai-cyan shadow-[0_0_20px_rgba(6,182,212,0.8)]' : 'bg-black border-neutral-700'}`}
                            />

                            <div className={`text-xs font-mono mb-2 ${step.active ? 'text-ai-cyan' : 'text-neutral-600'}`}>
                                {step.year}
                            </div>
                            <div className={`font-bold ${step.active ? 'text-white' : 'text-neutral-500'}`}>
                                {step.title}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
