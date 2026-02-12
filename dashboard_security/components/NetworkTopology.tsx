"use client";

import dynamic from 'next/dynamic';
import { useMemo } from 'react';

// ForceGraph is client-side only
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

interface Asset {
    id: string;
    ip: string;
    hostname?: string;
    device_type: string;
    status: string;
}

interface Node {
    id: string;
    name: string;
    ip?: string;
    group: string;
    status: string;
    val: number;
    x?: number;
    y?: number;
}

export default function NetworkTopology({ assets }: { assets: Asset[] }) {
    const data = useMemo(() => {
        if (!assets || assets.length === 0) return { nodes: [], links: [] };

        // Central Gateway (simulated)
        const nodes: Node[] = [{ id: 'gateway', name: 'Gateway', group: 'router', status: 'stable', val: 10 }];
        const links: any[] = [];

        assets.forEach(asset => {
            nodes.push({
                id: asset.id,
                name: asset.hostname || asset.ip,
                ip: asset.ip,
                group: asset.device_type,
                status: asset.status,
                val: 5
            });

            // Connect everyone to gateway for now (star topology assumption for LAN)
            links.push({
                source: 'gateway',
                target: asset.id
            });
        });

        return { nodes, links };
    }, [assets]);

    return (
        <div style={{ height: "500px", border: "1px solid #333", borderRadius: "8px", overflow: "hidden" }}>
            <ForceGraph2D
                graphData={data}
                nodeAutoColorBy="group"
                nodeLabel={(node: any) => `${node.name} (${node.ip || ''}) - ${node.group}`}
                backgroundColor="#0a0a0a"
                linkColor={() => "#444"}
                nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                    if (typeof node.x !== 'number' || typeof node.y !== 'number') return;

                    const label = node.name;
                    const fontSize = 12 / globalScale;
                    ctx.font = `${fontSize}px Sans-Serif`;
                    const textWidth = ctx.measureText(label).width;
                    // const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

                    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                    if (node.status === 'new') ctx.fillStyle = 'rgba(0, 255, 0, 0.8)';
                    if (node.status === 'at_risk') ctx.fillStyle = 'rgba(255, 0, 0, 0.8)';
                    if (node.status === 'gone') ctx.fillStyle = 'rgba(100, 100, 100, 0.5)';

                    ctx.beginPath();
                    ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
                    ctx.fill();

                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#fff';
                    if (node.id === 'gateway') ctx.fillStyle = '#00CED1';

                    ctx.fillText(label, node.x, node.y + 8);
                }}
            />
        </div>
    );
}
