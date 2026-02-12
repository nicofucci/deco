"use client";
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, OrbitControls } from '@react-three/drei';

export function ThreatMap() {
    return (
        <div className="w-full h-[700px] bg-black relative flex flex-col items-center justify-center overflow-hidden">
            <div className="absolute top-10 z-10 text-center px-4">
                <h2 className="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-neutral-500">
                    Inteligencia de Amenazas Global
                </h2>
                <p className="text-neutral-400 mt-2 max-w-xl mx-auto">
                    Telemetría de ataques en tiempo real desde más de 500M de sensores en todo el mundo. Anticipate al próximo golpe.
                </p>
            </div>

            <div className="w-full h-full absolute inset-0 z-0">
                <Canvas camera={{ position: [0, 0, 2.5] }}>
                    <PointsGlobe />
                    <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.8} />
                </Canvas>
            </div>

            <div className="absolute bottom-10 z-10 flex gap-4 md:gap-12 flex-wrap justify-center px-4">
                <Stat label="Ataques Bloqueados" value="2,401,920" color="text-red-500" />
                <Stat label="Agentes Activos" value="84,210" color="text-cyan-500" />
                <Stat label="Amenazas Zero-Day" value="12" color="text-purple-500" />
            </div>
        </div>
    );
}

function Stat({ label, value, color }: { label: string, value: string, color: string }) {
    return (
        <div className="text-center bg-black/50 backdrop-blur-md p-4 rounded-xl border border-neutral-800">
            <div className={`text-2xl md:text-3xl font-mono font-bold ${color}`}>{value}</div>
            <div className="text-xs text-neutral-500 uppercase tracking-widest mt-1">{label}</div>
        </div>
    )
}

function PointsGlobe(props: any) {
    const ref = useRef<any>(null);

    const sphere = useMemo(() => {
        const count = 4000; // More points for density
        const positions = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            const theta = 2 * Math.PI * Math.random();
            const phi = Math.acos(2 * Math.random() - 1);
            const r = 1.3; // Slightly larger
            const x = r * Math.sin(phi) * Math.cos(theta);
            const y = r * Math.sin(phi) * Math.sin(theta);
            const z = r * Math.cos(phi);
            positions[i * 3] = x;
            positions[i * 3 + 1] = y;
            positions[i * 3 + 2] = z;
        }
        return positions;
    }, []);

    useFrame((state, delta) => {
        if (ref.current) {
            ref.current.rotation.y += delta / 10;
        }
    });

    return (
        <group rotation={[0, 0, Math.PI / 4]}>
            <Points ref={ref} positions={sphere} stride={3} frustumCulled={false} {...props}>
                <PointMaterial
                    transparent
                    color="#f43f5e" // Rose/Red for threat vibe
                    size={0.005} // Smaller, sharper points
                    sizeAttenuation={true}
                    depthWrite={false}
                />
            </Points>
            {/* Inner Core */}
            <mesh scale={[1.25, 1.25, 1.25]}>
                <sphereGeometry args={[1, 32, 32]} />
                <meshBasicMaterial color="#000" transparent opacity={0.9} />
            </mesh>
        </group>
    );
}
