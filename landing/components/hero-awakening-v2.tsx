"use client";
import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sphere, Stars, Trail, MeshDistortMaterial } from '@react-three/drei';
import { motion } from 'framer-motion';
import { Vector3 } from 'three';

export function HeroAwakeningV2() {
    return (
        <div className="relative h-screen w-full bg-black overflow-hidden sticky top-0">

            {/* 1. 3D Scene */}
            <div className="absolute inset-0 z-0">
                <Canvas camera={{ position: [0, 0, 5] }}>
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[10, 10, 5]} intensity={2} color="#06b6d4" />
                    <pointLight position={[-10, -10, -5]} intensity={2} color="#8b5cf6" />

                    <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

                    <LivingOrb />
                    <FloatingParticles />
                </Canvas>
            </div>

            {/* 2. Cinematic Copy */}
            <div className="absolute inset-0 z-10 flex flex-col items-center justify-center pointer-events-none">
                <div className="text-center">
                    <motion.h1
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        className="text-7xl md:text-9xl font-black tracking-tighter text-white mix-blend-difference mb-4"
                    >
                        ANTICIPA.
                    </motion.h1>
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 1, duration: 1 }}
                        className="flex items-center justify-center gap-4 text-ai-cyan font-mono tracking-[0.3em] text-sm md:text-base uppercase"
                    >
                        <span className="animate-pulse">●</span>
                        <span>Deco no reacciona</span>
                        <span className="animate-pulse">●</span>
                    </motion.div>
                </div>
            </div>

            <div className="absolute bottom-10 left-0 w-full text-center z-20">
                <p className="text-neutral-500 font-mono text-xs tracking-widest animate-bounce">SCROLL PARA ACCEDER AL NÚCLEO</p>
            </div>
        </div>
    );
}

function LivingOrb() {
    const mesh = useRef<any>(null);

    useFrame((state) => {
        if (!mesh.current) return;
        const t = state.clock.getElapsedTime();
        mesh.current.rotation.x = t * 0.2;
        mesh.current.rotation.y = t * 0.3;
        // Breathing scale
        const scale = 1 + Math.sin(t * 1.5) * 0.1;
        mesh.current.scale.set(scale, scale, scale);
    });

    return (
        <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
            <Sphere ref={mesh} args={[1, 100, 100]} scale={1.5}>
                <MeshDistortMaterial
                    color="#000000"
                    emissive="#06b6d4"
                    emissiveIntensity={0.4}
                    roughness={0.1}
                    metalness={1}
                    distort={0.4}
                    speed={2}
                    wireframe={true} // High-tech look
                />
            </Sphere>
            {/* Inner Core */}
            <Sphere args={[0.8, 64, 64]}>
                <meshBasicMaterial color="#000000" />
            </Sphere>
        </Float>
    )
}

function FloatingParticles() {
    // Simple orbiting particles
    return (
        <group>
            {[...Array(20)].map((_, i) => (
                <Float key={i} speed={1 + Math.random()} rotationIntensity={2} floatIntensity={4} position={[
                    (Math.random() - 0.5) * 10,
                    (Math.random() - 0.5) * 10,
                    (Math.random() - 0.5) * 5
                ]}>
                    <Sphere args={[0.02, 16, 16]}>
                        <meshBasicMaterial color="#10b981" />
                    </Sphere>
                </Float>
            ))}
        </group>
    )
}
