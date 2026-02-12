"use client";

import { useEffect, useState } from "react";
import { useClient } from "@/providers/ClientProvider";
import { getJobs, createJob, getAgents, deleteJob } from "@/lib/client-api";
import { JobTable } from "@/components/JobTable";
import { Plus, RefreshCw, Network } from "lucide-react";
import { Agent } from "@/types";
import { useI18n } from "@/lib/i18n";

export default function JobsPage() {
    const { apiKey } = useClient();
    const { t } = useI18n();
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [showForm, setShowForm] = useState(false);

    // Form state
    const [target, setTarget] = useState("");
    const [type, setType] = useState("discovery");

    // Agent Selection
    const [agents, setAgents] = useState<Agent[]>([]);
    const [selectedAgentId, setSelectedAgentId] = useState("");
    const [useAgentNetwork, setUseAgentNetwork] = useState(false);

    const fetchJobs = async () => {
        if (!apiKey) return;
        setLoading(true);
        try {
            const data = await getJobs(apiKey);
            // Sort by date desc
            data.sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
            setJobs(data);
        } catch (e) {
            console.error("Error fetching jobs", e);
        } finally {
            setLoading(false);
        }
    };

    const fetchAgents = async () => {
        if (!apiKey) return;
        try {
            const data = await getAgents(apiKey);
            setAgents(data);
            if (data.length > 0 && !selectedAgentId) {
                setSelectedAgentId(data[0].id);
            }
        } catch (e) {
            console.error("Error fetching agents", e);
        }
    };

    useEffect(() => {
        fetchJobs();
        fetchAgents();
    }, [apiKey]);

    // Handle Agent Change
    const handleAgentChange = (agentId: string) => {
        setSelectedAgentId(agentId);
        if (useAgentNetwork) {
            const agent = agents.find(a => a.id === agentId);
            if (agent?.primary_cidr) {
                setTarget(agent.primary_cidr);
            }
        }
    };

    // Handle Mode Toggle
    const toggleAgentNetwork = (enabled: boolean) => {
        setUseAgentNetwork(enabled);
        if (enabled) {
            const agent = agents.find(a => a.id === selectedAgentId);
            if (agent?.primary_cidr) {
                setTarget(agent.primary_cidr);
                setType("discovery"); // Default to discovery for network scan
            } else {
                alert(t('agent_no_cidr'));
                setUseAgentNetwork(false);
            }
        } else {
            setTarget("");
        }
    };

    const handleCreateJob = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreating(true);
        try {
            await createJob(apiKey!, { type, target, agent_id: selectedAgentId });
            setShowForm(false);
            setTarget("");
            setUseAgentNetwork(false);
            fetchJobs(); // Refresh list
        } catch (e) {
            const message = e instanceof Error ? e.message : t('error_create_job');
            alert(`${t('error_create_job')}: ${message}`);
            console.error("Error creando job", e);
        } finally {
            setCreating(false);
        }
    };

    const handleDeleteJob = async (jobId: string) => {
        if (!apiKey) return;
        if (!confirm(t('confirm_delete_job'))) return;

        try {
            await deleteJob(apiKey, jobId);
            // Optimistic update or refresh
            setJobs(jobs.filter((j: any) => j.id !== jobId));
        } catch (e) {
            console.error("Error deleting job", e);
            alert(t('error_delete_job'));
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('job_management')}</h1>
                <div className="flex space-x-2">
                    <button
                        onClick={fetchJobs}
                        className="flex items-center rounded-md bg-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-300 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                    >
                        <RefreshCw className="mr-2 h-4 w-4" />
                        {t('refresh')}
                    </button>
                    <button
                        onClick={() => setShowForm(!showForm)}
                        className="flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
                    >
                        <Plus className="mr-2 h-4 w-4" />
                        {t('new_scan')}
                    </button>
                </div>
            </div>

            {showForm && (
                <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950">
                    <h3 className="mb-4 text-lg font-medium text-slate-900 dark:text-white">{t('configure_new_job')}</h3>
                    <form onSubmit={handleCreateJob} className="space-y-4">

                        {/* Agent Selection */}
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">{t('executing_agent')}</label>
                            <select
                                value={selectedAgentId}
                                onChange={(e) => handleAgentChange(e.target.value)}
                                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-white"
                            >
                                {agents.map(agent => (
                                    <option key={agent.id} value={agent.id}>
                                        {agent.hostname} ({agent.status}) {agent.local_ip ? `- ${agent.local_ip}` : ""}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Target Source Selection */}
                        <div className="space-y-3 bg-slate-50 dark:bg-slate-900 p-4 rounded-md border border-slate-200 dark:border-slate-800">
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">{t('target_source')}</label>
                            <div className="flex space-x-4">
                                <label className="flex items-center space-x-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="targetSource"
                                        checked={!useAgentNetwork && target === ""}
                                        onChange={() => { setUseAgentNetwork(false); setTarget(""); }}
                                        className="text-blue-600 focus:ring-blue-500"
                                    />
                                    <span className="text-sm text-slate-700 dark:text-slate-300">{t('manual')}</span>
                                </label>
                                <label className="flex items-center space-x-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="targetSource"
                                        checked={useAgentNetwork && target === (agents.find(a => a.id === selectedAgentId)?.primary_cidr || "")}
                                        onChange={() => {
                                            const agent = agents.find(a => a.id === selectedAgentId);
                                            if (agent?.primary_cidr) {
                                                setUseAgentNetwork(true);
                                                setTarget(agent.primary_cidr);
                                                setType("discovery");
                                            } else {
                                                alert(t('agent_no_cidr'));
                                            }
                                        }}
                                        className="text-blue-600 focus:ring-blue-500"
                                    />
                                    <span className="text-sm text-slate-700 dark:text-slate-300">{t('agent_network_cidr')}</span>
                                </label>
                                <label className="flex items-center space-x-2 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="targetSource"
                                        checked={useAgentNetwork && target === (agents.find(a => a.id === selectedAgentId)?.local_ip || "")}
                                        onChange={() => {
                                            const agent = agents.find(a => a.id === selectedAgentId);
                                            if (agent?.local_ip) {
                                                setUseAgentNetwork(true);
                                                setTarget(agent.local_ip);
                                                setType("full"); // Default to full scan for single host
                                            } else {
                                                alert(t('agent_no_ip'));
                                            }
                                        }}
                                        className="text-blue-600 focus:ring-blue-500"
                                    />
                                    <span className="text-sm text-slate-700 dark:text-slate-300">{t('agent_ip')}</span>
                                </label>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">{t('target')} (IP/Hostname)</label>
                                <input
                                    type="text"
                                    value={target}
                                    onChange={(e) => setTarget(e.target.value)}
                                    disabled={useAgentNetwork}
                                    className={`mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-white ${useAgentNetwork ? 'bg-slate-100 dark:bg-slate-800 cursor-not-allowed' : ''}`}
                                    placeholder={t('target_placeholder')}
                                    required
                                />
                                {useAgentNetwork && (
                                    <p className="mt-1 text-xs text-blue-600 dark:text-blue-400">
                                        {t('target_auto_msg')}
                                    </p>
                                )}
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">{t('scan_type')}</label>
                                <select
                                    value={type}
                                    onChange={(e) => setType(e.target.value)}
                                    className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-900 dark:text-white"
                                >
                                    <option value="discovery">Discovery (Rápido)</option>
                                    <option value="full">Full Scan (Puertos + Versiones)</option>
                                </select>
                            </div>
                        </div>
                        <div className="flex justify-end space-x-2">
                            <button
                                type="button"
                                onClick={() => setShowForm(false)}
                                className="rounded-md px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                            >
                                {t('cancel')}
                            </button>
                            <button
                                type="submit"
                                disabled={creating}
                                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                            >
                                {creating ? t('creating') : t('launch_job')}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {loading ? (
                <div>{t('loading_jobs')}</div>
            ) : (
                <JobTable jobs={jobs} onDelete={handleDeleteJob} />
            )}
        </div>
    );
}
