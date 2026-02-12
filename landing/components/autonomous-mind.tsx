"use client";
import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, MeshWobbleMaterial, Text } from '@react-three/drei';
import { motion } from 'framer-motion';

export function AutonomousMind() {
    const [activeWord, setActiveWord] = useState<string | null>(null);

    return (
        <div className="relative h-screen w-full bg-black flex flex-col md:flex-row items-center justify-center overflow-hidden">

            {/* Left: Interactive 3D Mind */}
            <div className="w-full md:w-1/2 h-[50vh] md:h-full relative z-10 transition-colors duration-500">
                <Canvas camera={{ position: [0, 0, 4] }}>
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[5, 5, 5]} intensity={1} />
                    <OrganicBrain activeWord={activeWord} />
                </Canvas>
            </div>

            {/* Right: Cognitive Triggers */}
            <div className="w-full md:w-1/2 h-full flex flex-col justify-center px-8 md:px-24 z-20 space-y-12 bg-gradient-to-l from-black via-black to-transparent">
                <MindTrigger word="APRENDE" desc="Adaptación continua a nuevos patrones." active={activeWord} onHover={setActiveWord} />
                <MindTrigger word="OBSERVA" desc="Visibilidad total de la capa de red." active={activeWord} onHover={setActiveWord} />
                <MindTrigger word="DECIDE" desc="Respuesta autónoma en milisegundos." active={activeWord} onHover={setActiveWord} />
            </div>

            {/* Background Gradient */}
            <div className={`absolute inset-0 z-0 transition-opacity duration-1000 opacity-20 bg-[radial-gradient(circle_at_30%_50%,var(--active-color),transparent_70%)]`} style={{
                '--active-color': activeWord === 'APRENDE' ? '#8b5cf6' : (activeWord === 'OBSERVA' ? '#06b6d4' : (activeWord === 'DECIDE' ? '#10b981' : '#000000'))
            } as any} />
        </div>
    );
}

function OrganicBrain({ activeWord }: { activeWord: string | null }) {
    const mesh = useRef<any>(null);

    useFrame((state) => {
        if (mesh.current) {
            mesh.current.rotation.y += 0.005;
            // Spikes in rotation speed when active
            if (activeWord) mesh.current.rotation.x += 0.01;
        }
    });

    const color = activeWord === 'APRENDE' ? '#8b5cf6' : (activeWord === 'OBSERVA' ? '#06b6d4' : (activeWord === 'DECIDE' ? '#10b981' : '#333333'));
    const speed = activeWord === 'DECIDE' ? 10 : (activeWord ? 5 : 1);
    const factor = activeWord ? 0.6 : 0.3;

    return (
        <Sphere ref={mesh} args={[1, 100, 100]} scale={1.8}>
            <MeshWobbleMaterial
                color={color}
                wireframe={true}
                factor={factor}
                speed={speed}
                transparent
                opacity={0.8}
            />
        </Sphere>
    )
}

function MindTrigger({ word, desc, active, onHover }: any) {
    const isActive = active === word;
    return (
        <div
            className="group cursor-pointer"
            onMouseEnter={() => onHover(word)}
            onMouseLeave={() => onHover(null)}
        >
            <h2 className={`text-5xl md:text-7xl font-bold tracking-tighter transition-all duration-300 ${isActive ? 'text-white translate-x-4' : 'text-neutral-800 group-hover:text-neutral-600'}`}>
                {word}
            </h2>
            <div className={`h-[1px] bg-white transition-all duration-500 overflow-hidden ${isActive ? 'w-full mt-4 opacity-100' : 'w-0 opacity-0'}`} />
            <p className={`mt-2 font-mono text-sm text-ai-cyan transition-all duration-300 ${isActive ? 'opacity-100 translate-x-4' : 'opacity-0'}`}>
                {'> ' + desc}
            </p>
        </div>
    )
}
