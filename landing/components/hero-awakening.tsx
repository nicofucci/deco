"use client";
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Float } from '@react-three/drei';
import * as random from 'maath/random/dist/maath-random.esm';
import { motion } from 'framer-motion';

export function HeroAwakening() {
    return (
        <div className="relative h-screen w-full bg-black overflow-hidden pointer-events-none md:pointer-events-auto">

            {/* 1. 3D Neural Field */}
            <div className="absolute inset-0 z-0">
                <Canvas camera={{ position: [0, 0, 1] }}>
                    <NeuralParticles />
                </Canvas>
            </div>

            {/* 2. Text Awakening (Glitch & Reveal) */}
            <div className="absolute inset-0 z-10 flex items-center justify-center pointer-events-none">
                <div className="text-center max-w-4xl px-6">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, filter: "blur(10px)" }}
                        animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
                        transition={{ duration: 2, ease: "circOut" }}
                    >
                        <h1 className="text-6xl md:text-9xl font-black tracking-tighter text-white mb-6 mix-blend-difference" style={{ textShadow: "0 0 40px rgba(255,255,255,0.3)" }}>
                            ANTICIPA.
                        </h1>
                    </motion.div>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1.5, duration: 2 }}
                        className="text-xl md:text-2xl text-neutral-400 font-light tracking-wide max-w-2xl mx-auto"
                    >
                        Deco-Security no monitorea amenazas. <br />
                        <span className="text-ai-cyan font-normal">Las extermina antes de que existan.</span>
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 50 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 3, duration: 1 }}
                        className="mt-16 pointer-events-auto"
                    >
                        <button className="group relative px-12 py-5 bg-transparent overflow-hidden rounded-none border-l border-r border-white/30 text-white font-mono text-sm tracking-[0.2em] hover:bg-white/5 transition-all">
                            <span className="relative z-10 group-hover:text-ai-cyan transition-colors">INICIAR_DEFENSA_v10</span>
                            <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-in-out" />
                            {/* Glitch lines */}
                            <div className="absolute top-0 left-0 w-full h-[1px] bg-ai-cyan/50 animate-scan-vertical opacity-0 group-hover:opacity-100" />
                        </button>
                    </motion.div>
                </div>
            </div>

            {/* 3. Vignette & Grain Overlay */}
            <div className="absolute inset-0 z-20 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_0%,black_100%)] opacity-80" />
            <div className="absolute inset-0 z-[21] pointer-events-none opacity-[0.03] mix-blend-overlay" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")' }} />
        </div>
    );
}

function NeuralParticles(props: any) {
    const ref = useRef<any>(null);
    const sphere = useMemo(() => random.inSphere(new Float32Array(5000), { radius: 1.2 }), []);

    useFrame((state, delta) => {
        if (ref.current) {
            ref.current.rotation.x -= delta / 15;
            ref.current.rotation.y -= delta / 20;
        }
    });

    return (
        <group rotation={[0, 0, Math.PI / 4]}>
            <Points ref={ref} positions={sphere} stride={3} frustumCulled={false} {...props}>
                <PointMaterial
                    transparent
                    color="#ffffff"
                    size={0.003}
                    sizeAttenuation={true}
                    depthWrite={false}
                    opacity={0.4}
                />
            </Points>
        </group>
    );
}
