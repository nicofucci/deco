"use client";

import {
    Radar,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    ResponsiveContainer,
    Tooltip,
} from "recharts";

interface RiskRadarProps {
    data: any[];
}

export default function RiskRadar({ data }: RiskRadarProps) {
    return (
        <div className="h-[400px] w-full bg-slate-900/50 rounded-xl border border-slate-800 p-4">
            <h3 className="text-lg font-semibold text-white mb-4">Radar de Riesgo Multidimensional</h3>
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                    <PolarGrid stroke="#334155" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar
                        name="Nivel de Riesgo"
                        dataKey="A"
                        stroke="#f43f5e"
                        strokeWidth={3}
                        fill="#f43f5e"
                        fillOpacity={0.3}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }}
                        itemStyle={{ color: "#f43f5e" }}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
}
