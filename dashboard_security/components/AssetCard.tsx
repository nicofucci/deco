import Link from "next/link";
import { Server } from "lucide-react";
import { Card } from "./Card";

interface Asset {
    id: string;
    ip: string;
    hostname?: string;
    os_info?: string;
    status?: string;
    open_ports?: number[];
    last_scan_at?: string;
}

interface AssetCardProps {
    asset: Asset;
    findingCount?: number;
}

export function AssetCard({ asset, findingCount = 0 }: AssetCardProps) {
    const openPortsLabel = asset.open_ports && asset.open_ports.length > 0
        ? asset.open_ports.slice(0, 4).join(", ") + (asset.open_ports.length > 4 ? "..." : "")
        : "N/A";

    return (
        <Link href={`/dashboard/assets/${asset.id}`}>
            <Card
                title={asset.hostname || "Unknown Host"}
                icon={Server}
                className="cursor-pointer transition-shadow hover:shadow-md"
            >
                <div className="mt-4 space-y-2">
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-500 dark:text-slate-400">IP Address:</span>
                        <span className="font-medium text-slate-900 dark:text-white">{asset.ip}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-500 dark:text-slate-400">Puertos:</span>
                        <span className="font-medium text-slate-900 dark:text-white">{openPortsLabel}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-500 dark:text-slate-400">Findings:</span>
                        <span className="font-medium text-slate-900 dark:text-white">{findingCount}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-500 dark:text-slate-400">Último escaneo:</span>
                        <span className="font-medium text-slate-900 dark:text-white">
                            {asset.last_scan_at ? new Date(asset.last_scan_at).toLocaleString() : "N/A"}
                        </span>
                    </div>
                    <div className="mt-4 flex items-center justify-between">
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${(asset.status || 'active') === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                            }`}>
                            {(asset.status || 'activo').toUpperCase()}
                        </span>
                    </div>
                </div>
            </Card>
        </Link>
    );
}
