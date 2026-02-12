"use client";
import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial, Html } from '@react-three/drei';
import { motion } from 'framer-motion';
import * as THREE from 'three';

export function ConsciousCore() {
    const [activeState, setActiveState] = useState<'IDLE' | 'LEARN' | 'OBSERVE' | 'ACT'>('IDLE');

    return (
        <div className="relative py-40 w-full min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden">

            {/* Section Title */}
            <div className="absolute top-20 text-center z-10 w-full">
                <h2 className="text-xs font-mono text-neutral-600 tracking-[0.5em] mb-4">NÚCLEO CENTRAL v.9</h2>
                <div className="h-[1px] w-24 bg-neutral-800 mx-auto" />
            </div>

            {/* 3D Brain */}
            <div className="relative w-full h-[600px] z-0">
                <Canvas camera={{ position: [0, 0, 4] }}>
                    <ambientLight intensity={0.2} />
                    <directionalLight position={[5, 10, 5]} intensity={1} color="#ffffff" />
                    <pointLight position={[-10, -5, -5]} intensity={2} color="#06b6d4" />

                    <CoreMesh activeState={activeState} />
                </Canvas>
            </div>

            {/* Interactive Triggers */}
            <div className="absolute bottom-20 z-10 flex gap-8 md:gap-16">
                <CoreTrigger label="APRENDE" state="LEARN" active={activeState} onHover={setActiveState} />
                <CoreTrigger label="OBSERVA" state="OBSERVE" active={activeState} onHover={setActiveState} />
                <CoreTrigger label="ACTÚA" state="ACT" active={activeState} onHover={setActiveState} />
            </div>

        </div>
    );
}

function CoreMesh({ activeState }: { activeState: string }) {
    const meshRef = useRef<THREE.Mesh>(null);

    // Config based on state
    const config = {
        color: activeState === 'ACT' ? '#10b981' : (activeState === 'OBSERVE' ? '#06b6d4' : '#8b5cf6'),
        speed: activeState === 'ACT' ? 3 : (activeState === 'OBSERVE' ? 0.5 : 1),
        distort: activeState === 'ACT' ? 0.6 : 0.3,
        hoverScale: activeState !== 'IDLE' ? 1.3 : 1
    }

    useFrame((state) => {
        if (!meshRef.current) return;
        const t = state.clock.getElapsedTime();
        meshRef.current.rotation.x = t * 0.2;
        meshRef.current.rotation.y = t * 0.3;

        // Rapid jitter for ACT state
        if (activeState === 'ACT') {
            meshRef.current.rotation.z += 0.05;
        }
    });

    return (
        <Sphere ref={meshRef} args={[1, 100, 100]} scale={2}>
            <MeshDistortMaterial
                color="#000000"
                emissive={config.color}
                emissiveIntensity={0.5}
                roughness={0.2}
                metalness={0.9}
                distort={config.distort}
                speed={config.speed}
            />
        </Sphere>
    )
}

function CoreTrigger({ label, state, active, onHover }: any) {
    const isActive = active === state;
    return (
        <div
            onMouseEnter={() => onHover(state)}
            onMouseLeave={() => onHover('IDLE')}
            className="group cursor-pointer flex flex-col items-center gap-2"
        >
            <div className={`w-3 h-3 rounded-full border border-neutral-700 transition-all duration-300
                ${isActive ? 'bg-white shadow-[0_0_15px_white]' : 'group-hover:bg-neutral-500'}
            `} />
            <span className={`text-sm font-mono tracking-widest transition-all duration-300
                ${isActive ? 'text-white' : 'text-neutral-600 group-hover:text-neutral-400'}
            `}>
                {label}
            </span>
            {isActive && <motion.div layoutId="underline" className="w-full h-[1px] bg-white mt-1" />}
        </div>
    )
}
