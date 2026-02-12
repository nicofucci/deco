"use client";
import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Box, Sphere, Line, Text, Html, OrbitControls } from '@react-three/drei';
import { motion } from 'framer-motion';
import * as THREE from 'three';

export function HeroDigitalTwin() {
    return (
        <div className="relative h-screen w-full bg-slate-950 overflow-hidden">

            {/* Title Overlay */}
            <div className="absolute top-8 left-8 z-10 pointer-events-none">
                <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-ai-cyan rounded-full animate-pulse" />
                    <span className="text-ai-cyan font-mono text-xs tracking-widest">LIVE_INFRASTRUCTURE_VIEW</span>
                </div>
                <h1 className="text-4xl md:text-6xl font-black text-white tracking-tighter">
                    TU RED,<br />
                    <span className="text-ai-cyan">VISUALIZADA.</span>
                </h1>
            </div>

            {/* 3D Scene */}
            <Canvas orthographic camera={{ position: [20, 20, 20], zoom: 40, near: 0.1, far: 200 }}>
                <ambientLight intensity={0.5} />
                <directionalLight position={[10, 10, 5]} intensity={1} color="#ffffff" />
                <pointLight position={[-10, 10, -10]} intensity={0.5} color="#06b6d4" />

                <NetworkGrid />
                <IsometricCity />

                <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} minPolarAngle={Math.PI / 4} maxPolarAngle={Math.PI / 3} />
            </Canvas>

            {/* Legend / Stats overlay */}
            <div className="absolute bottom-8 right-8 z-10 flex flex-col gap-2 text-right pointer-events-none">
                <div className="bg-slate-900/80 backdrop-blur p-4 border border-slate-800 rounded">
                    <div className="text-xs text-slate-400 font-mono mb-1">NODES_ONLINE</div>
                    <div className="text-2xl text-white font-mono font-bold">142</div>
                </div>
                <div className="bg-slate-900/80 backdrop-blur p-4 border border-slate-800 rounded">
                    <div className="text-xs text-slate-400 font-mono mb-1">TRAFFIC_FLOW</div>
                    <div className="text-2xl text-ai-cyan font-mono font-bold">2.4 GB/s</div>
                </div>
            </div>
        </div>
    );
}

function NetworkGrid() {
    return (
        <gridHelper args={[100, 50, 0x1e293b, 0x0f172a]} position={[0, -1, 0]} />
    )
}

function IsometricCity() {
    // Generate some random buildings/servers
    const buildings = [
        { pos: [0, 0, 0], size: [2, 4, 2], type: 'CORE' },
        { pos: [4, 0, 2], size: [1, 2, 1], type: 'SERVER' },
        { pos: [-4, 0, 3], size: [1, 3, 1], type: 'SERVER' },
        { pos: [2, 0, -5], size: [1.5, 1, 1.5], type: 'DATABASE' },
        { pos: [-3, 0, -3], size: [1, 1.5, 1], type: 'ENDPOINT' },
        { pos: [5, 0, -2], size: [1.2, 2.5, 1.2], type: 'SERVER' },
    ];

    return (
        <group>
            {buildings.map((b, i) => (
                <Building key={i} position={b.pos} size={b.size} type={b.type} />
            ))}
            <DataConnections />
        </group>
    )
}

function Building({ position, size, type }: any) {
    const [hovered, setHover] = useState(false);
    const color = type === 'CORE' ? '#3b82f6' : (type === 'DATABASE' ? '#10b981' : '#64748b');
    const hoverColor = '#06b6d4';

    return (
        <group position={[position[0], position[1] + size[1] / 2 - 1, position[2]]}>
            <Box
                args={size}
                onPointerOver={() => setHover(true)}
                onPointerOut={() => setHover(false)}
            >
                <meshStandardMaterial
                    color={hovered ? hoverColor : color}
                    roughness={0.2}
                    metalness={0.8}
                    transparent
                    opacity={0.9}
                />
            </Box>

            {/* Annotation Label */}
            {hovered && (
                <Html position={[0, size[1] / 2 + 0.5, 0]} center distanceFactor={15}>
                    <div className="bg-slate-900/90 text-white px-2 py-1 rounded text-[10px] font-mono border border-ai-cyan whitespace-nowrap">
                        {type}_NODE // ONLINE
                    </div>
                </Html>
            )}
        </group>
    )
}

function DataConnections() {
    // animated lines simulated
    return (
        <group>
            {/* Lines connecting to center [0,0,0] */}
            <Line points={[[4, 0, 2], [0, 0, 0]]} color="#3b82f6" lineWidth={1} transparent opacity={0.5} />
            <Line points={[[-4, 0, 3], [0, 0, 0]]} color="#3b82f6" lineWidth={1} transparent opacity={0.5} />
            <Line points={[[2, 0, -5], [0, 0, 0]]} color="#3b82f6" lineWidth={1} transparent opacity={0.5} />
            <Line points={[[-3, 0, -3], [0, 0, 0]]} color="#3b82f6" lineWidth={1} transparent opacity={0.5} />
            <Line points={[[5, 0, -2], [0, 0, 0]]} color="#3b82f6" lineWidth={1} transparent opacity={0.5} />
        </group>
    )
}
