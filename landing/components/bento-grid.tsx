"use client";
import { cn } from "@/lib/utils";
import React from "react";
import { motion } from "framer-motion";
import { Copy, ShieldCheck, Activity, Globe, Zap, Server } from "lucide-react";

export function BentoGridSection() {
    const features = [
        {
            title: "Visión X-RAY™",
            description: "Visibilidad total de Capa 2/3 con fingerprinting activo.",
            header: <SkeletonOne />,
            icon: <Activity className="h-4 w-4 text-neutral-500" />,
            className: "md:col-span-2",
        },
        {
            title: "Defensa Activa",
            description: "Respuesta automática y aislamiento de amenazas en milisegundos.",
            header: <SkeletonTwo />,
            icon: <ShieldCheck className="h-4 w-4 text-neutral-500" />,
            className: "md:col-span-1",
        },
        {
            title: "Inteligencia Global",
            description: "Feeds de amenazas en tiempo real de 500M+ endpoints.",
            header: <SkeletonThree />,
            icon: <Globe className="h-4 w-4 text-neutral-500" />,
            className: "md:col-span-1",
        },
        {
            title: "Cero Overhead",
            description: "Agente ultraligero (<50MB) sin impacto en el rendimiento.",
            header: <SkeletonFour />,
            icon: <Zap className="h-4 w-4 text-neutral-500" />,
            className: "md:col-span-2",
        },
    ];

    return (
        <div className="max-w-7xl mx-auto py-20 px-4 md:px-8 relative z-10">
            <h2 className="text-4xl md:text-5xl font-bold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-neutral-200 to-neutral-500">
                Capacidades de Grado Militar
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-7xl mx-auto">
                {features.map((feature, i) => (
                    <BentoGridItem
                        key={i}
                        title={feature.title}
                        description={feature.description}
                        header={feature.header}
                        icon={feature.icon}
                        className={feature.className}
                    />
                ))}
            </div>
        </div>
    );
}

const SkeletonOne = () => {
    return (
        <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800 p-4 border border-neutral-800">
            <div className="flex flex-row gap-2 items-center">
                <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                <div className="h-2 w-2 bg-neutral-700 rounded-full" />
                <div className="h-2 w-2 bg-neutral-700 rounded-full" />
            </div>
            <div className="mt-4 space-y-2">
                <div className="h-2 w-3/4 bg-neutral-700 rounded" />
                <div className="h-2 w-1/2 bg-neutral-700 rounded" />
                <div className="h-2 w-full bg-neutral-700 rounded" />
            </div>
        </div>
    );
};
const SkeletonTwo = () => (
    <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800 border border-neutral-800 relative overflow-hidden">
        <motion.div
            animate={{ top: ["0%", "100%"] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute left-0 right-0 h-1 bg-cyan-500/50 blur-sm top-0"
        />
    </div>
);
const SkeletonThree = () => (
    <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800 border border-neutral-800 items-center justify-center">
        <div className="relative">
            <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20" />
            <Globe className="text-blue-400 w-12 h-12" />
        </div>
    </div>
);
const SkeletonFour = () => (
    <div className="flex flex-1 w-full h-full min-h-[6rem] rounded-xl bg-gradient-to-br from-neutral-900 to-neutral-800 border border-neutral-800 items-center justify-center">
        <div className="text-4xl font-mono text-green-400">
            15<span className="text-sm text-neutral-500">ms</span>
        </div>
    </div>
);


export const BentoGridItem = ({
    className,
    title,
    description,
    header,
    icon,
}: {
    className?: string;
    title?: string | React.ReactNode;
    description?: string | React.ReactNode;
    header?: React.ReactNode;
    icon?: React.ReactNode;
}) => {
    return (
        <div
            className={cn(
                "row-span-1 rounded-xl group/bento hover:shadow-xl transition duration-200 shadow-input dark:shadow-none p-4 dark:bg-black/50 dark:border-white/[0.2] bg-white border border-transparent justify-between flex flex-col space-y-4 backdrop-blur-sm",
                className
            )}
        >
            {header}
            <div className="group-hover/bento:translate-x-2 transition duration-200">
                {icon}
                <div className="font-sans font-bold text-neutral-600 dark:text-neutral-200 mb-2 mt-2">
                    {title}
                </div>
                <div className="font-sans font-normal text-neutral-600 text-xs dark:text-neutral-300">
                    {description}
                </div>
            </div>
        </div>
    );
};
