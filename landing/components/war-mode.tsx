"use client";
import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Icosahedron, Box } from '@react-three/drei';
import * as THREE from 'three';

export function WarMode() {
    return (
        <div className="relative h-screen w-full bg-slate-950 overflow-hidden flex items-center justify-center">

            {/* Massive Header */}
            <div className="absolute top-20 left-0 w-full text-center z-20 pointer-events-none">
                <h2 className="text-[10vw] font-black text-transparent bg-clip-text bg-gradient-to-b from-neutral-800 to-transparent leading-none select-none">
                    WAR ZOOM
                </h2>
            </div>

            <div className="absolute inset-0 z-0 opacity-40">
                <Canvas camera={{ position: [0, 10, 10] }}>
                    <ambientLight intensity={0.5} />
                    <pointLight position={[10, 10, 10]} color="#ef4444" intensity={2} />
                    <ConflictZone />
                </Canvas>
            </div>

            {/* Content Card */}
            <div className="relative z-10 max-w-2xl text-center bg-black/80 backdrop-blur-xl border border-red-900/30 p-12 rounded-2xl mx-6">
                <div className="flex items-center justify-center gap-2 mb-6">
                    <div className="w-3 h-3 bg-red-500 animate-ping rounded-full" />
                    <span className="text-red-500 font-mono tracking-widest text-xs">AMENAZA ACTIVA DETECTADA</span>
                </div>
                <h3 className="text-4xl md:text-5xl font-bold text-white mb-6">El enemigo no duerme.</h3>
                <p className="text-xl text-neutral-400 mb-8">
                    Visualiza el conflicto en tiempo real. Deco Security despliega contramedidas activas mientras otros apenas generan alertas.
                </p>
                <div className="flex justify-center gap-4">
                    <div className="h-1 w-20 bg-red-600 rounded-full" />
                    <div className="h-1 w-20 bg-neutral-800 rounded-full" />
                    <div className="h-1 w-20 bg-neutral-800 rounded-full" />
                </div>
            </div>

        </div>
    );
}

function ConflictZone() {
    // A scene representing abstract conflict
    return (
        <group>
            {/* The Shield (Blue) */}
            <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
                <planeGeometry args={[20, 20, 32, 32]} />
                <meshStandardMaterial color="#000000" wireframe emissive="#06b6d4" emissiveIntensity={0.2} />
            </mesh>

            {/* The Attackers (Red Spikes) - Falling */}
            {[...Array(10)].map((_, i) => (
                <AttackProjectile key={i} offset={i} />
            ))}
        </group>
    )
}

function AttackProjectile({ offset }: { offset: number }) {
    const ref = useRef<any>(null);

    useFrame((state) => {
        if (ref.current) {
            const t = state.clock.getElapsedTime();
            // Fall down
            ref.current.position.y = 10 - ((t * 5 + offset * 2) % 15);
            // Reset rotation
            ref.current.rotation.x += 0.1;
            ref.current.rotation.z += 0.1;
        }
    });

    return (
        <Icosahedron ref={ref} args={[0.5, 0]} position={[Math.sin(offset) * 5, 10, Math.cos(offset) * 5]}>
            <meshStandardMaterial color="#ef4444" wireframe />
        </Icosahedron>
    )
}
