"use client";

import React, { useMemo } from "react";

interface WorldMapProps {
    data: {
        country: string;
        code: string;
        count: number;
        lat: number;
        lng: number;
    }[];
}

const WorldMap: React.FC<WorldMapProps> = ({ data }) => {
    // Simple projection helper (Mercator-ish)
    const project = (lat: number, lng: number) => {
        const x = (lng + 180) * (800 / 360);
        const latRad = lat * Math.PI / 180;
        const mercN = Math.log(Math.tan((Math.PI / 4) + (latRad / 2)));
        const y = (400 / 2) - (400 * mercN / (2 * Math.PI));
        return [x, Math.max(0, Math.min(400, y))];
    };

    return (
        <div className="flex flex-col md:flex-row gap-6 h-full">
            {/* Map Section */}
            <div className="flex-1 relative rounded-xl overflow-hidden bg-slate-900/50 border border-slate-800 shadow-2xl flex items-center justify-center">
                <div className="absolute top-4 left-4 z-10">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                        Global Threat Grid
                    </h3>
                    <p className="text-xs text-slate-400">Live Agent Distribution</p>
                </div>

                {/* Background Grid */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(30,41,59,0.5)_1px,transparent_1px),linear-gradient(90deg,rgba(30,41,59,0.5)_1px,transparent_1px)] bg-[size:40px_40px] opacity-20"></div>

                <div className="relative w-full h-full p-4">
                    {/* Simplified World Map SVG (Abstract) */}
                    <svg viewBox="0 0 800 400" className="w-full h-full drop-shadow-[0_0_10px_rgba(59,130,246,0.5)]">
                        <defs>
                            <filter id="glow">
                                <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                                <feMerge>
                                    <feMergeNode in="coloredBlur" />
                                    <feMergeNode in="SourceGraphic" />
                                </feMerge>
                            </filter>
                        </defs>

                        {/* Abstract Continents (Simplified Paths) */}
                        <g fill="#1e293b" stroke="#334155" strokeWidth="1">
                            {/* North America */}
                            <path d="M50,50 L300,50 L250,200 L100,150 Z" opacity="0.5" />
                            {/* South America */}
                            <path d="M220,210 L320,210 L300,350 L240,320 Z" opacity="0.5" />
                            {/* Europe/Asia */}
                            <path d="M350,40 L750,40 L700,200 L400,180 Z" opacity="0.5" />
                            {/* Africa */}
                            <path d="M380,190 L500,190 L480,330 L400,300 Z" opacity="0.5" />
                            {/* Australia */}
                            <path d="M600,250 L750,250 L730,350 L620,330 Z" opacity="0.5" />
                        </g>

                        {/* Data Markers */}
                        {data.map((item) => {
                            const [cx, cy] = project(item.lat, item.lng);
                            return (
                                <g key={item.code} className="cursor-pointer group">
                                    <circle cx={cx} cy={cy} r="4" fill="#ef4444" className="animate-ping opacity-75" />
                                    <circle cx={cx} cy={cy} r="4" fill="#ef4444" filter="url(#glow)" />
                                    <circle cx={cx} cy={cy} r="15" fill="transparent" stroke="#ef4444" strokeWidth="1" opacity="0" className="group-hover:opacity-50 transition-opacity" />

                                    {/* Tooltip on Hover */}
                                    <g className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                        <rect x={cx + 10} y={cy - 25} width="100" height="40" rx="4" fill="#0f172a" stroke="#334155" />
                                        <text x={cx + 20} y={cy - 10} fill="white" fontSize="10" fontWeight="bold">{item.country}</text>
                                        <text x={cx + 20} y={cy + 5} fill="#94a3b8" fontSize="9">Agents: {item.count}</text>
                                    </g>
                                </g>
                            );
                        })}
                    </svg>

                    <div className="absolute bottom-4 right-4 text-[10px] text-slate-600">
                        * Abstract Visualization
                    </div>
                </div>
            </div>

            {/* List Section */}
            <div className="w-full md:w-64 flex flex-col gap-3">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Top Locations</h3>
                <div className="space-y-2 overflow-y-auto max-h-[400px] pr-2 custom-scrollbar">
                    {data.sort((a, b) => b.count - a.count).map((item) => (
                        <div key={item.code} className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-blue-500/50 transition-colors group cursor-pointer">
                            <div className="flex items-center gap-3">
                                <span className="text-lg">{getFlagEmoji(item.code)}</span>
                                <div className="flex flex-col">
                                    <span className="text-sm font-medium text-slate-200 group-hover:text-blue-400 transition-colors">{item.country}</span>
                                    <span className="text-[10px] text-slate-500">{item.code}</span>
                                </div>
                            </div>
                            <div className="flex flex-col items-end">
                                <span className="text-xs font-bold text-white bg-slate-800 px-2 py-1 rounded-full border border-slate-700 group-hover:border-blue-500/30 transition-colors">
                                    {item.count}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Helper to get flag emoji from country code
function getFlagEmoji(countryCode: string) {
    const map: Record<string, string> = {
        "USA": "🇺🇸",
        "ESP": "🇪🇸",
        "DEU": "🇩🇪",
        "JPN": "🇯🇵",
        "BRA": "🇧🇷",
        "GBR": "🇬🇧",
        "AUS": "🇦🇺"
    };
    return map[countryCode] || "🏳️";
}

export default WorldMap;
