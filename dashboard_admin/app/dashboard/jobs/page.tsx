"use client";

import { useEffect, useState } from "react";
import { getJobs, deleteJob, getJobResults, getJobDownloadUrl } from "@/lib/api";
import { Trash2, Eye, Download, X } from "lucide-react";

export default function JobsPage() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedJob, setSelectedJob] = useState<any>(null);
    const [resultsLoading, setResultsLoading] = useState(false);
    const [resultsData, setResultsData] = useState<any>(null);

    useEffect(() => {
        fetchJobs();
    }, []);

    const fetchJobs = async () => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;
        try {
            const res = await getJobs(key);
            setJobs(res);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteJob = async (jobId: string) => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;
        if (!confirm("¿Estás seguro de que deseas eliminar este job?")) return;

        try {
            await deleteJob(key, jobId);
            setJobs(jobs.filter((j: any) => j.id !== jobId));
        } catch (e) {
            console.error("Error deleting job", e);
            alert("Error al eliminar el job");
        }
    };

    const handleViewResults = async (job: any) => {
        setSelectedJob(job);
        setResultsLoading(true);
        setResultsData(null);

        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;

        try {
            const res = await getJobResults(key, job.id);
            setResultsData(res);
        } catch (e) {
            console.error(e);
            setResultsData({ error: "No se pudieron cargar los resultados." });
        } finally {
            setResultsLoading(false);
        }
    };

    const handleDownload = (jobId: string) => {
        const url = getJobDownloadUrl(jobId);
        // Add master key if needed via query param or handle auth differently for direct links
        // For now, assuming browser session or we need to fetch blob.
        // Actually, the download endpoint expects header. We can't easily do headers in <a> tag.
        // We'll fetch blob and save.
        downloadFile(jobId);
    };

    const downloadFile = async (jobId: string) => {
        const key = localStorage.getItem("deco_admin_master_key");
        if (!key) return;
        try {
            const res = await fetch(getJobDownloadUrl(jobId), {
                headers: { "X-Admin-Master-Key": key }
            });
            if (!res.ok) throw new Error("Download failed");
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `scan_result_${jobId}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (e) {
            console.error(e);
            alert("Error al descargar archivo");
        }
    };

    if (loading) return <div className="p-6 text-slate-400">Cargando jobs...</div>;

    return (
        <div className="space-y-6 relative">
            <h1 className="text-2xl font-bold text-white">Historial de Jobs Global</h1>
            <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden">
                <table className="min-w-full divide-y divide-slate-800">
                    <thead className="bg-slate-950">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Cliente</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Tipo</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Target</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Estado</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Fecha</th>
                            <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-900">
                        {jobs.map((job: any) => (
                            <tr key={job.id} className="hover:bg-slate-800/50 transition-colors">
                                <td className="whitespace-nowrap px-6 py-4 text-sm font-mono text-slate-500">{job.id.substring(0, 8)}...</td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-400">{job.client_name}</td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-white">{job.type}</td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">{job.target}</td>
                                <td className="whitespace-nowrap px-6 py-4">
                                    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${job.status === 'done' ? 'bg-green-900/30 text-green-400' :
                                        job.status === 'running' ? 'bg-blue-900/30 text-blue-400' :
                                            job.status === 'error' ? 'bg-red-900/30 text-red-400' :
                                                'bg-gray-800 text-gray-400'
                                        }`}>
                                        {job.status.toUpperCase()}
                                    </span>
                                </td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500">{new Date(job.created_at).toLocaleString()}</td>
                                <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium space-x-2">
                                    {job.status === 'done' && (
                                        <>
                                            <button
                                                onClick={() => handleViewResults(job)}
                                                className="text-slate-400 hover:text-blue-500 transition-colors"
                                                title="Ver Resultados"
                                            >
                                                <Eye className="h-4 w-4" />
                                            </button>
                                            <button
                                                onClick={() => downloadFile(job.id)}
                                                className="text-slate-400 hover:text-green-500 transition-colors"
                                                title="Descargar Resultados"
                                            >
                                                <Download className="h-4 w-4" />
                                            </button>
                                        </>
                                    )}
                                    <button
                                        onClick={() => handleDeleteJob(job.id)}
                                        className="text-slate-400 hover:text-red-500 transition-colors"
                                        title="Eliminar Job"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Results Modal */}
            {selectedJob && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <div className="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
                        <div className="flex justify-between items-center p-4 border-b border-slate-800">
                            <h3 className="text-lg font-bold text-white">Resultados: {selectedJob.type} - {selectedJob.target}</h3>
                            <button onClick={() => setSelectedJob(null)} className="text-slate-400 hover:text-white">
                                <X className="h-5 w-5" />
                            </button>
                        </div>
                        <div className="flex-1 overflow-auto p-4 bg-slate-950 font-mono text-xs text-green-400">
                            {resultsLoading ? (
                                <div className="text-center py-10 text-slate-500">Cargando datos...</div>
                            ) : (
                                <pre>{JSON.stringify(resultsData?.raw_data || resultsData, null, 2)}</pre>
                            )}
                        </div>
                        <div className="p-4 border-t border-slate-800 flex justify-end">
                            <button
                                onClick={() => setSelectedJob(null)}
                                className="px-4 py-2 bg-slate-800 text-white rounded hover:bg-slate-700"
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
