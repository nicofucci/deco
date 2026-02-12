"use client";
import React from 'react';
import { Canvas } from '@react-three/fiber';
import { Line, Sphere, Html } from '@react-three/drei';
import { motion } from 'framer-motion';

export function ArchitectureFlow() {
    return (
        <div className="relative h-screen bg-slate-50 overflow-hidden text-slate-900">
            <div className="absolute inset-0 z-0">
                <Canvas camera={{ position: [0, 0, 10] }}>
                    <ambientLight intensity={1} />
                    <FlowDiagram />
                </Canvas>
            </div>

            <div className="absolute top-20 left-8 md:left-20 z-10 max-w-xl">
                <h2 className="text-4xl font-bold mb-6 text-slate-900">Arquitectura Unificada</h2>
                <ul className="space-y-6">
                    <FeatureItem number="01" title="Sensores Ligeros" desc="Despliegue en endpoint sin afectar rendimiento." />
                    <FeatureItem number="02" title="Inteligencia Central" desc="Procesamiento masivo en el núcleo de Deco." />
                    <FeatureItem number="03" title="Defensa Autónoma" desc="Ejecución de bloqueos sin intervención humana." />
                </ul>
            </div>
        </div>
    );
}

function FeatureItem({ number, title, desc }: any) {
    return (
        <li className="flex gap-4 group">
            <span className="font-mono text-slate-300 font-bold text-xl group-hover:text-blue-500 transition-colors">{number}</span>
            <div>
                <h3 className="font-bold text-lg mb-1">{title}</h3>
                <p className="text-slate-500 leading-relaxed text-sm">{desc}</p>
            </div>
        </li>
    )
}

function FlowDiagram() {
    // Center Node
    const center = [3, 0, 0] as const;

    // Satellites
    const satellites = [
        [6, 3, 0],
        [6, -3, 0],
        [8, 1, 2],
        [8, -1, -2]
    ];

    return (
        <group>
            {/* Center Core */}
            <mesh position={center}>
                <sphereGeometry args={[1.5, 32, 32]} />
                <meshStandardMaterial color="#3b82f6" />
                <Html position={[0, 2, 0]} center>
                    <div className="bg-white px-3 py-1 rounded shadow-lg text-xs font-bold text-blue-600">DECO CORE</div>
                </Html>
            </mesh>

            {/* Satellite Nodes & Lines */}
            {satellites.map((pos: any, i) => (
                <group key={i}>
                    <mesh position={pos}>
                        <sphereGeometry args={[0.3, 16, 16]} />
                        <meshStandardMaterial color="#94a3b8" />
                    </mesh>
                    {/* Beam to Center */}
                    <Line
                        points={[pos, center]}
                        color="#cbd5e1"
                        lineWidth={1}
                        dashed={true}
                        dashScale={2}
                        dashSize={1}
                        gapSize={1}
                    />
                </group>
            ))}
        </group>
    )
}
