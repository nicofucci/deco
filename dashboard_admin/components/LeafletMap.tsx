"use client";

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect } from "react";

// Fix for default marker icon in Next.js
// delete (L.Icon.Default.prototype as any)._getIconUrl;
// L.Icon.Default.mergeOptions({
//     iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
//     iconUrl: require("leaflet/dist/images/marker-icon.png"),
//     shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
// });

const customIcon = (status: string) => new L.DivIcon({
    className: "custom-marker",
    html: `<div class="relative">
             <div class="w-4 h-4 ${status === 'online' ? 'bg-green-500' : 'bg-slate-500'} rounded-full animate-ping absolute opacity-75"></div>
             <div class="w-4 h-4 ${status === 'online' ? 'bg-green-600' : 'bg-slate-600'} rounded-full relative border-2 border-white shadow-lg"></div>
           </div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
});

interface LeafletMapProps {
    data: {
        lat: number;
        lon: number;
        agent_id: string;
        hostname: string;
        status: string;
        country: string;
    }[];
}

export default function LeafletMap({ data }: LeafletMapProps) {
    return (
        <div className="h-full w-full rounded-xl overflow-hidden relative z-0">
            <MapContainer
                center={[20, 0]}
                zoom={2}
                scrollWheelZoom={false}
                style={{ height: "100%", width: "100%", background: "#1e293b" }}
                attributionControl={false}
            >
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />

                {data.map((item) => (
                    <Marker
                        key={item.agent_id}
                        position={[item.lat, item.lon]}
                        icon={customIcon(item.status)}
                    >
                        <Popup className="custom-popup">
                            <div className="p-2 text-slate-900">
                                <h3 className="font-bold text-sm">{item.hostname}</h3>
                                <p className="text-xs">Status: <span className={item.status === 'online' ? 'text-green-600 font-bold' : 'text-slate-500'}>{item.status.toUpperCase()}</span></p>
                                <p className="text-xs text-slate-500">{item.country}</p>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>

            {/* Overlay Stats */}
            <div className="absolute top-4 right-4 z-[1000] bg-slate-900/80 backdrop-blur-md border border-slate-700 p-3 rounded-lg shadow-xl max-h-[300px] overflow-y-auto custom-scrollbar w-48">
                <h4 className="text-xs font-bold text-slate-400 uppercase mb-2 tracking-wider">Active Agents</h4>
                {data.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">No public agents detected.</p>
                ) : (
                    <div className="space-y-2">
                        {data.map((item) => (
                            <div key={item.agent_id} className="flex justify-between items-center text-xs">
                                <span className="text-slate-300 flex items-center gap-2 truncate max-w-[100px]" title={item.hostname}>
                                    <span className={`w-1.5 h-1.5 rounded-full ${item.status === 'online' ? 'bg-green-500' : 'bg-slate-500'}`}></span>
                                    {item.hostname}
                                </span>
                                <span className="font-mono text-slate-500 text-[10px]">{item.country.substring(0, 3).toUpperCase()}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
