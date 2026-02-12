"use client";
import React from 'react';
import { HeroImported } from "@/components/hero-imported";
import { ParticleBackgroundImported } from "@/components/particle-background-imported";
import { ConceptSection } from "@/components/concept-section";
import { ArchitectureSection } from "@/components/architecture-section";
import { ConsolePreview } from "@/components/console-preview";
import { NavbarImported } from "@/components/navbar-imported";
import { Shield, Hexagon, Box, Triangle, CircleDashed } from 'lucide-react';

export default function Home() {
  return (
    <main className="antialiased selection:bg-emerald-500/30 selection:text-emerald-200">

      <ParticleBackgroundImported />

      {/* Scanlines Overlay - Manual CSS class used in HTML, reusing tailwind equivalent here or style */}
      <div className="fixed inset-0 pointer-events-none z-50 opacity-[0.15]"
        style={{ background: 'linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.2))', backgroundSize: '100% 4px' }}
      />

      <div className="fixed inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.8)_100%)] z-0" />

      <NavbarImported />

      <HeroImported />
      <ConceptSection />
      <ArchitectureSection />
      <ConsolePreview />

      {/* Partners Section (Inline as it's simple) */}
      <section id="partners" className="py-24 bg-neutral-900/30 border-y border-white/5 relative z-10">
        <div className="max-w-4xl mx-auto text-center px-6">
          <h2 className="text-2xl md:text-3xl font-semibold text-white mb-8">Ecosistema de Partners</h2>
          <p className="text-neutral-400 mb-12 max-w-2xl mx-auto">
            Deco Security está construido para potenciar a los proveedores de servicios (MSP/MSSP). Conviértete en un SOC de próxima generación sin construir la infraestructura.
          </p>
          <div className="flex flex-wrap justify-center gap-8 opacity-50 grayscale hover:grayscale-0 transition-all duration-700">
            <div className="flex items-center gap-2 text-xl font-bold font-sans tracking-tight text-white"><Hexagon /> CYBERCORP</div>
            <div className="flex items-center gap-2 text-xl font-bold font-sans tracking-tight text-white"><Triangle /> NEXUS DEFENSE</div>
            <div className="flex items-center gap-2 text-xl font-bold font-sans tracking-tight text-white"><CircleDashed /> OMNISEC</div>
            <div className="flex items-center gap-2 text-xl font-bold font-sans tracking-tight text-white"><Box /> STRATOS</div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/10 bg-[#050505] relative z-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Shield className="text-emerald-600 w-5 h-5" />
            <span className="font-sans font-bold text-sm tracking-widest text-white">DECO</span>
          </div>

          <div className="text-neutral-500 text-xs flex gap-6">
            <a href="#" className="hover:text-emerald-400 transition-colors">Privacy Protocol</a>
            <a href="#" className="hover:text-emerald-400 transition-colors">System Status</a>
            <a href="#" className="hover:text-emerald-400 transition-colors">Contact Core</a>
          </div>

          <div className="text-[10px] text-neutral-600 font-mono">
            © 2024 DECO SECURITY SYSTEMS. ALL RIGHTS RESERVED.
          </div>
        </div>
      </footer>

    </main>
  );
}
