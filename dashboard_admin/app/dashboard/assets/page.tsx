"use client";

import { useEffect, useState } from "react";
import { getMasterAssets } from "@/lib/api";
import { Search, Filter, Download, ChevronLeft, ChevronRight, Shield, Server, Globe } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export default function AssetsPage() {
    const { t } = useI18n();
    const [assets, setAssets] = useState<any[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Filters
    const [page, setPage] = useState(1);
    const [limit] = useState(20);
    const [search, setSearch] = useState("");
    const [debouncedSearch, setDebouncedSearch] = useState("");

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(search);
            setPage(1);
        }, 500);
        return () => clearTimeout(timer);
    }, [search]);

    const fetchAssets = async () => {
        setLoading(true);
        const key = (typeof window !== 'undefined') ? (localStorage.getItem("deco_admin_master_key") || "") : "";
        if (!key) {
            setError("Falta la master key.");
            setLoading(false);
            return;
        }
        try {
            const skip = (page - 1) * limit;
            const res = await getMasterAssets(key, skip, limit, debouncedSearch);
            console.log("Assets response:", res);
            setAssets(Array.isArray(res.items) ? res.items : []);
            setTotal(res.total || 0);
            setError(null);
        } catch (e) {
            console.error(e);
            setError("Error al cargar activos.");
            setAssets([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAssets();
    }, [page, debouncedSearch]);

    const totalPages = Math.ceil(total / limit);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center">
                        <Server className="mr-2 h-6 w-6 text-blue-400" />
                        {t('assets')}
                    </h1>
                    <p className="text-slate-400 mt-1">
                        {t('global_assets_view')}
                    </p>
                </div>
                <button className="flex items-center px-4 py-2 bg-slate-800 text-slate-300 rounded hover:bg-slate-700 transition-colors">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                </button>
            </div>

            {/* Filters */}
            <div className="flex gap-4 bg-slate-900/50 p-4 rounded-lg border border-slate-800">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-500" />
                    <input
                        type="text"
                        placeholder="Search assets..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded pl-10 pr-4 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
                    />
                </div>
                <button className="flex items-center px-4 py-2 bg-slate-800 text-slate-300 rounded hover:bg-slate-700 transition-colors">
                    <Filter className="h-4 w-4 mr-2" />
                    Filters
                </button>
            </div>

            {/* Table */}
            <div className="bg-slate-900/50 rounded-lg border border-slate-800 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-800">
                        <thead className="bg-slate-950">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Client</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Asset</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">IP Address</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Open Ports</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Last Scan</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-slate-900/30 divide-y divide-slate-800">
                            {loading ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-4 text-center text-slate-400">
                                        Loading assets...
                                    </td>
                                </tr>
                            ) : error ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-4 text-center text-red-400">
                                        {error}
                                    </td>
                                </tr>
                            ) : assets.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-4 text-center text-slate-400">
                                        No assets found.
                                    </td>
                                </tr>
                            ) : assets.map((asset) => (
                                <tr key={asset.id} className="hover:bg-slate-800/50 transition-colors">
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">{asset.client_name || "N/A"}</td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-white flex items-center">
                                        <Globe className="h-4 w-4 mr-2 text-blue-400" />
                                        {asset.hostname}
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">{asset.ip}</td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">
                                        {asset.open_ports && asset.open_ports.length > 0 ? (
                                            <div className="flex gap-1 flex-wrap">
                                                {asset.open_ports.slice(0, 3).map((p: any) => (
                                                    <span key={p} className="px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-300">{p}</span>
                                                ))}
                                                {asset.open_ports.length > 3 && (
                                                    <span className="px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-300">+{asset.open_ports.length - 3}</span>
                                                )}
                                            </div>
                                        ) : (
                                            <span className="text-slate-500 italic">None</span>
                                        )}
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">
                                        {asset.last_scan_at ? new Date(asset.last_scan_at).toLocaleDateString() : "Never"}
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                                        <button className="text-blue-400 hover:text-blue-300">Details</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                <div className="bg-slate-950 px-4 py-3 border-t border-slate-800 flex items-center justify-between sm:px-6">
                    <div className="flex-1 flex justify-between sm:hidden">
                        <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1}
                            className="relative inline-flex items-center px-4 py-2 border border-slate-700 text-sm font-medium rounded-md text-slate-300 bg-slate-900 hover:bg-slate-800 disabled:opacity-50"
                        >
                            Previous
                        </button>
                        <button
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages}
                            className="ml-3 relative inline-flex items-center px-4 py-2 border border-slate-700 text-sm font-medium rounded-md text-slate-300 bg-slate-900 hover:bg-slate-800 disabled:opacity-50"
                        >
                            Next
                        </button>
                    </div>
                    <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                        <div>
                            <p className="text-sm text-slate-400">
                                Showing <span className="font-medium">{(page - 1) * limit + 1}</span> to <span className="font-medium">{Math.min(page * limit, total)}</span> of <span className="font-medium">{total}</span> results
                            </p>
                        </div>
                        <div>
                            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                                <button
                                    onClick={() => setPage(p => Math.max(1, p - 1))}
                                    disabled={page === 1}
                                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-slate-700 bg-slate-900 text-sm font-medium text-slate-400 hover:bg-slate-800 disabled:opacity-50"
                                >
                                    <span className="sr-only">Previous</span>
                                    <ChevronLeft className="h-5 w-5" aria-hidden="true" />
                                </button>
                                <button
                                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                    disabled={page === totalPages}
                                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-slate-700 bg-slate-900 text-sm font-medium text-slate-400 hover:bg-slate-800 disabled:opacity-50"
                                >
                                    <span className="sr-only">Next</span>
                                    <ChevronRight className="h-5 w-5" aria-hidden="true" />
                                </button>
                            </nav>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
