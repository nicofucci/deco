"use client";
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial, Html, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

export function AiOrb() {
    return (
        <div className="w-full h-full absolute inset-0 z-0">
            <Canvas camera={{ position: [0, 0, 3] }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#06b6d4" />
                <pointLight position={[-10, -10, -10]} intensity={1} color="#8b5cf6" />

                <AnimatedSphere />
                <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
            </Canvas>
        </div>
    );
}

function AnimatedSphere() {
    const meshRef = useRef<THREE.Mesh>(null);
    const hoverCheck = useRef(false);

    useFrame((state) => {
        if (!meshRef.current) return;

        // Breathing effect
        const t = state.clock.getElapsedTime();
        meshRef.current.rotation.x = t * 0.1;
        meshRef.current.rotation.y = t * 0.15;

        // Mouse interaction (simulated with mouse position if needed, or simple movement)
        // For now, simple breathing distortion is handled by material
    });

    return (
        <Sphere ref={meshRef} args={[1, 64, 64]} scale={1.2}>
            <MeshDistortMaterial
                color="#000000"
                emissive="#06b6d4"
                emissiveIntensity={0.8}
                roughness={0.1}
                metalness={1}
                distort={0.4}
                speed={1.5}
                side={THREE.DoubleSide}
            />

            {/* Outer Holographic Shell */}
            <mesh scale={1.2}>
                <sphereGeometry args={[1, 32, 32]} />
                <meshBasicMaterial color="#8b5cf6" wireframe transparent opacity={0.1} />
            </mesh>
        </Sphere>
    );
}
