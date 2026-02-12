"use client";
import React, { useState } from 'react';
import { ShieldCheck, Globe, ChevronDown, ArrowRight } from 'lucide-react';

export function NavbarImported() {
    const [openLang, setOpenLang] = useState(false);
    const [lang, setLang] = useState("ES");

    return (
        <nav className="fixed top-0 w-full z-40 border-b border-white/5 glass-panel h-16">
            <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between">

                {/* Logo */}
                <div className="flex items-center gap-2 group cursor-pointer">
                    <ShieldCheck className="text-emerald-500 text-xl group-hover:rotate-90 transition-transform duration-700 w-6 h-6" />
                    <span className="font-sans font-semibold text-lg tracking-widest text-white">
                        DECO<span className="font-light text-neutral-500">SECURITY</span>
                    </span>
                </div>

                {/* Links */}
                <div className="hidden md:flex items-center gap-8 text-xs font-medium tracking-wide text-neutral-400">
                    <a href="#concept" className="hover:text-white transition-colors">CONCEPTO</a>
                    <a href="#architecture" className="hover:text-white transition-colors">ESTRUCTURA</a>
                    <a href="#consoles" className="hover:text-white transition-colors">CONSOLAS</a>
                    <a href="#partners" className="hover:text-white transition-colors">PARTNERS</a>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4">
                    {/* Language Selector */}
                    <div className="relative group">
                        <button
                            className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 hover:border-emerald-500/50 transition-all text-xs text-white"
                            onClick={() => setOpenLang(!openLang)}
                        >
                            <Globe className="text-emerald-400 w-3 h-3" />
                            <span className="uppercase tracking-wider font-mono">{lang}</span>
                            <ChevronDown className="opacity-50 w-3 h-3" />
                        </button>
                    </div>

                    <a href="#contact" className="hidden md:flex items-center gap-2 bg-white text-black px-4 py-1.5 rounded-full text-xs font-semibold hover:bg-emerald-400 transition-colors">
                        <span>SOLICITAR DEMO</span>
                        <ArrowRight className="w-3 h-3" />
                    </a>
                </div>
            </div>
        </nav>
    );
}
