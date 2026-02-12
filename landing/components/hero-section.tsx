"use client";
import React from "react";
import { Spotlight } from "@/components/ui/spotlight";
import { motion } from "framer-motion";

export function HeroSection() {
    return (
        <div className="h-screen w-full rounded-md flex md:items-center md:justify-center bg-transparent antialiased relative overflow-hidden">
            {/* Background Effects */}
            <Spotlight
                className="-top-40 left-0 md:left-60 md:-top-20"
                fill="white"
            />

            <div className="p-4 max-w-7xl mx-auto relative z-10 w-full pt-20 md:pt-0 flex flex-col items-center">

                <motion.div
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 1 }}
                    className="mb-8 p-1 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600"
                >
                    <div className="px-4 py-1 bg-black rounded-full text-xs font-bold text-white uppercase tracking-wider">
                        Nuevo: Motor X-RAY™ v2.0
                    </div>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-5xl md:text-8xl font-black text-center bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50 tracking-tighter"
                >
                    Protege Tu <br />
                    <span className="text-cyan-500 drop-shadow-[0_0_30px_rgba(6,182,212,0.5)]">
                        Infraestructura
                    </span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                    className="mt-6 font-normal text-lg md:text-xl text-neutral-300 max-w-2xl text-center mx-auto leading-relaxed"
                >
                    Deco-Security despliega defensa de **Nivel Militar** en tu red.
                    Visualiza amenazas invisibles con **X-RAY™**, bloquea ataques en tiempo real y duerme tranquilo.
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
                    className="flex flex-col md:flex-row justify-center mt-10 gap-6"
                >
                    <button className="relative inline-flex h-14 overflow-hidden rounded-full p-[1px] focus:outline-none transition-transform hover:scale-105 active:scale-95 shadow-[0_0_40px_rgba(6,182,212,0.3)]">
                        <span className="absolute inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#E2CBFF_0%,#393BB2_50%,#E2CBFF_100%)]" />
                        <span className="inline-flex h-full w-full cursor-pointer items-center justify-center rounded-full bg-slate-950 px-8 py-1 text-base font-bold text-white backdrop-blur-3xl">
                            Comenzar Prueba Gratis
                        </span>
                    </button>
                    <button className="px-8 py-4 rounded-full border border-neutral-700 text-neutral-300 font-semibold hover:bg-neutral-800 hover:text-white transition duration-200">
                        Ver Demo en Vivo
                    </button>
                </motion.div>
            </div>

        </div>
    );
}
