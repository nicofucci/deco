"use client";
import React, { useState } from "react";
import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { Shield } from "lucide-react";

export function Navbar() {
    const { scrollY } = useScroll();
    const [visible, setVisible] = useState(true);

    useMotionValueEvent(scrollY, "change", (current) => {
        if (typeof current === "number") {
            if (current > 100) {
                setVisible(true);
            }
        }
    });

    return (
        <motion.nav
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className={cn(
                "fixed top-4 inset-x-0 max-w-2xl mx-auto z-50 px-8 py-3 rounded-full border border-neutral-800 bg-black/50 backdrop-blur-md shadow-[0px_0px_20px_0px_rgba(0,0,0,0.5)] flex items-center justify-between space-x-4",
            )}
        >
            <Link href="/" className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-cyan-500 fill-cyan-500/20" />
                <span className="text-sm font-bold text-neutral-100 tracking-wide">DECO</span>
            </Link>

            <div className="flex items-center gap-6 text-sm font-medium text-neutral-300">
                <Link href="#features" className="hover:text-cyan-400 transition-colors">Características</Link>
                <Link href="#xray" className="hover:text-cyan-400 transition-colors">X-RAY™</Link>
                <Link href="#threats" className="hover:text-cyan-400 transition-colors">Intel</Link>
            </div>

            <button className="px-4 py-1.5 rounded-full bg-cyan-600/20 text-cyan-400 border border-cyan-500/50 text-xs font-semibold hover:bg-cyan-500 hover:text-white transition-all duration-200">
                Ingresar
            </button>
        </motion.nav>
    );
}
