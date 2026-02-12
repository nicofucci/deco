"use client";

import { useEffect, useState } from "react";
import { getMasterFindings } from "@/lib/api";
import { Search, Filter, Download, ChevronLeft, ChevronRight, AlertTriangle, Shield, Activity } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export default function FindingsPage() {
    const { t } = useI18n();
    const [findings, setFindings] = useState<any[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [severity, setSeverity] = useState("");

    // Filters
    const [page, setPage] = useState(1);
    const [limit] = useState(20);

    const fetchFindings = async () => {
        setLoading(true);
        const key = (typeof window !== 'undefined') ? (localStorage.getItem("deco_admin_master_key") || "") : "";
        if (!key) return;

        try {
            const skip = (page - 1) * limit;
            const res = await getMasterFindings(key, skip, limit, severity);
            console.log("Findings response:", res);
            setFindings(Array.isArray(res.items) ? res.items : []);
            setTotal(res.total || 0);
        } catch (e) {
            console.error(e);
            setFindings([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFindings();
    }, [page, severity]);

    const totalPages = Math.ceil(total / limit);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-white flex items-center">
                        <AlertTriangle className="mr-2 h-6 w-6 text-yellow-400" />
                        {t('findings')}
                    </h1>
                    <p className="text-slate-400 mt-1">
                        {t('global_findings_view')}
                    </p>
                </div>
                <button className="flex items-center px-4 py-2 bg-slate-800 text-slate-300 rounded hover:bg-slate-700 transition-colors">
                    <Download className="h-4 w-4 mr-2" />
                    Export
                </button>
            </div>

            {/* Filters */}
            <div className="flex gap-4 bg-slate-900/50 p-4 rounded-lg border border-slate-800">
                <select
                    value={severity}
                    onChange={(e) => { setSeverity(e.target.value); setPage(1); }}
                    className="bg-slate-950 border border-slate-800 rounded px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-blue-500"
                >
                    <option value="">All Severities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                </select>
            </div>

            {/* Table */}
            <div className="bg-slate-900/50 rounded-lg border border-slate-800 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-800">
                        <thead className="bg-slate-950">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Client</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Severity</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Title</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Asset</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Date</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-slate-900/30 divide-y divide-slate-800">
                            {loading ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-4 text-center text-slate-400">
                                        Loading findings...
                                    </td>
                                </tr>
                            ) : findings.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-4 text-center text-slate-400">
                                        No findings found.
                                    </td>
                                </tr>
                            ) : findings.map((finding) => (
                                <tr key={finding.id} className="hover:bg-slate-800/50 transition-colors">
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">{finding.client_name || "N/A"}</td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm">
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${finding.severity === 'critical' ? 'bg-red-900/50 text-red-400 border border-red-900' :
                                                finding.severity === 'high' ? 'bg-orange-900/50 text-orange-400 border border-orange-900' :
                                                    finding.severity === 'medium' ? 'bg-yellow-900/50 text-yellow-400 border border-yellow-900' :
                                                        'bg-blue-900/50 text-blue-400 border border-blue-900'
                                            }`}>
                                            {finding.severity.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-white font-medium">{finding.title}</td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">{finding.asset_host || finding.asset_ip || "N/A"}</td>
                                    <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">
                                        {new Date(finding.created_at).toLocaleDateString()}
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
