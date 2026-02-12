"use client";
import React from "react";
import Link from "next/link";
import { Shield, Twitter, Linkedin, Github } from "lucide-react";

export function Footer() {
    return (
        <footer className="w-full bg-black py-12 px-4 border-t border-neutral-900 z-50 relative">
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="flex items-center gap-2">
                    <Shield className="w-6 h-6 text-cyan-500" />
                    <span className="font-bold text-lg text-white">Deco-Security</span>
                </div>

                <div className="flex gap-6 text-sm text-neutral-400">
                    <Link href="#" className="hover:text-white transition">Privacidad</Link>
                    <Link href="#" className="hover:text-white transition">Términos</Link>
                    <Link href="#" className="hover:text-white transition">Estado</Link>
                    <Link href="/contact" className="hover:text-white transition">Contacto</Link>
                </div>

                <div className="flex gap-4">
                    <Link href="#" className="p-2 rounded-full bg-neutral-900 text-white hover:bg-neutral-800 transition"><Twitter className="w-4 h-4" /></Link>
                    <Link href="#" className="p-2 rounded-full bg-neutral-900 text-white hover:bg-neutral-800 transition"><Linkedin className="w-4 h-4" /></Link>
                    <Link href="#" className="p-2 rounded-full bg-neutral-900 text-white hover:bg-neutral-800 transition"><Github className="w-4 h-4" /></Link>
                </div>
            </div>
            <div className="text-center text-neutral-600 text-xs mt-8">
                © 2025 Deco-Security Inc. Todos los derechos reservados.
            </div>
        </footer>
    );
}
