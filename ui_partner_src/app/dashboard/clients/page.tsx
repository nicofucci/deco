"use client";

import { useEffect, useState } from "react";
import { getMyClients, createClient, getClientApiKey, deleteClient } from "@/lib/api";
import { Plus, Copy, Eye, Trash, Settings } from "lucide-react";
import Link from "next/link";
import { useI18n } from "@/lib/i18n";

export default function ClientsPage() {
    const [clients, setClients] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [newClientName, setNewClientName] = useState("");
    const [newClientEmail, setNewClientEmail] = useState("");
    const [createdApiKey, setCreatedApiKey] = useState("");
    const [createdAgentApiKey, setCreatedAgentApiKey] = useState("");
    const [selectedClient, setSelectedClient] = useState<any>(null);
    const { t } = useI18n();

    const fetchClients = async () => {
        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;
        try {
            const res = await getMyClients(token);
            setClients(res);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClients();
    }, []);

    const handleCreateClient = async (e: React.FormEvent) => {
        e.preventDefault();
        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;
        try {
            const res = await createClient(token, newClientName, newClientEmail);
            setCreatedApiKey(res.client_panel_api_key);
            setCreatedAgentApiKey(res.agent_api_key);
            fetchClients();
        } catch (e) {
            alert(t('error_create_client'));
        }
    };

    const copyText = (text: string) => {
        navigator.clipboard.writeText(text);
        alert(t('copied_clipboard'));
    };

    const handleDeleteClient = async (clientId: string) => {
        if (!confirm(t('confirm_delete_client'))) return;

        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;
        try {
            await deleteClient(token, clientId);
            alert(t('client_deleted'));
            fetchClients();
        } catch (e) {
            alert(t('error_delete_client'));
        }
    };

    if (loading) return <div className="p-6 text-slate-400">{t('loading_clients')}</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-white">{t('my_clients')}</h1>
                <button
                    onClick={() => setShowModal(true)}
                    className="flex items-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                >
                    <Plus className="mr-2 h-4 w-4" />
                    {t('generate_new')}
                </button>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden">
                <table className="min-w-full divide-y divide-slate-800">
                    <thead className="bg-slate-950">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">{t('name_label')}</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">{t('email_label')}</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">{t('agents')}</th>
                            <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">{t('action')}</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-900">
                        {clients.map((client: any) => (
                            <tr key={client.id} className="hover:bg-slate-800/50 transition-colors">
                                <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-white">{client.name}</td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-400">{client.contact_email}</td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">{client.total_agents}</td>
                                <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300 flex space-x-3">
                                    <button onClick={() => setSelectedClient(client)} className="text-slate-400 hover:text-white" title={t('view_details')}>
                                        <Eye className="h-4 w-4" />
                                    </button>
                                    <Link href={`/dashboard/clients/${client.id}`} className="text-purple-400 hover:text-purple-300" title={t('manage_client')}>
                                        <Settings className="h-4 w-4" />
                                    </Link>
                                    <button onClick={() => copyText(client.api_key)} className="text-blue-400 hover:text-blue-300" title={t('copy') + " API Key"}>
                                        <Copy className="h-4 w-4" />
                                    </button>
                                    <button onClick={() => handleDeleteClient(client.id)} className="text-red-400 hover:text-red-300" title={t('delete_client')}>
                                        <Trash className="h-4 w-4" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Modal Crear Cliente */}
            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="w-full max-w-md rounded-lg bg-slate-900 p-6 border border-slate-800 shadow-xl">
                        <h2 className="text-lg font-bold text-white mb-4">{t('register_new_client')}</h2>
                        {!createdApiKey ? (
                            <form onSubmit={handleCreateClient} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-300">{t('client_name')}</label>
                                    <input
                                        type="text"
                                        required
                                        value={newClientName}
                                        onChange={(e) => setNewClientName(e.target.value)}
                                        className="mt-1 block w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300">{t('contact_email')}</label>
                                    <input
                                        type="email"
                                        required
                                        value={newClientEmail}
                                        onChange={(e) => setNewClientEmail(e.target.value)}
                                        className="mt-1 block w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                                    />
                                </div>
                                <div className="flex justify-end space-x-3 mt-6">
                                    <button
                                        type="button"
                                        onClick={() => setShowModal(false)}
                                        className="rounded-md px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800"
                                    >
                                        {t('cancel')}
                                    </button>
                                    <button
                                        type="submit"
                                        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                                    >
                                        {t('create_client')}
                                    </button>
                                </div>
                            </form>
                        ) : (
                            <div className="space-y-4">
                                <div className="rounded-md bg-green-900/20 p-4 border border-green-900">
                                    <p className="text-green-400 text-sm font-medium">{t('client_created_success')}</p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">{t('api_key_client_panel')}</label>
                                    <div className="flex items-center space-x-2">
                                        <code className="flex-1 rounded bg-slate-950 p-2 text-xs text-slate-300 break-all border border-slate-800">
                                            {createdApiKey}
                                        </code>
                                        <button
                                            onClick={() => copyText(createdApiKey)}
                                            className="p-2 text-blue-400 hover:bg-slate-800 rounded"
                                        >
                                            <Copy className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">{t('api_key_agent')}</label>
                                    <div className="flex items-center space-x-2">
                                        <code className="flex-1 rounded bg-slate-950 p-2 text-xs text-slate-300 break-all border border-slate-800">
                                            {createdAgentApiKey}
                                        </code>
                                        <button
                                            onClick={() => copyText(createdAgentApiKey)}
                                            className="p-2 text-blue-400 hover:bg-slate-800 rounded"
                                        >
                                            <Copy className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                                <div className="flex justify-end mt-6">
                                    <button
                                        onClick={() => {
                                            setShowModal(false);
                                            setCreatedApiKey("");
                                            setCreatedAgentApiKey("");
                                            setNewClientName("");
                                            setNewClientEmail("");
                                        }}
                                        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                                    >
                                        {t('close')}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Modal Detalles Cliente */}
            {selectedClient && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="w-full max-w-lg rounded-lg bg-slate-900 p-6 border border-slate-800 shadow-xl">
                        <h2 className="text-lg font-bold text-white mb-6">{t('client_details')}</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-xs font-medium text-slate-500 uppercase">{t('name_label')}</label>
                                <p className="text-white text-sm mt-1">{selectedClient.name}</p>
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-slate-500 uppercase">{t('email_label')}</label>
                                <p className="text-white text-sm mt-1">{selectedClient.contact_email}</p>
                            </div>

                            <div className="pt-4 border-t border-slate-800">
                                <label className="block text-xs font-medium text-blue-400 uppercase mb-2">{t('api_key_agent')}</label>
                                <div className="flex items-center space-x-2">
                                    <code className="flex-1 rounded bg-slate-950 p-3 text-xs text-slate-300 break-all border border-slate-800 font-mono">
                                        {selectedClient.agent_api_key || t('no_available')}
                                    </code>
                                    <button
                                        onClick={() => copyText(selectedClient.agent_api_key)}
                                        className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded"
                                        title={t('copy')}
                                    >
                                        <Copy className="h-4 w-4" />
                                    </button>
                                </div>
                                <p className="text-xs text-slate-500 mt-1">{t('use_agent_key_msg')}</p>
                            </div>

                            <div className="pt-2">
                                <label className="block text-xs font-medium text-purple-400 uppercase mb-2">{t('api_key_client_panel')}</label>
                                <div className="flex items-center space-x-2">
                                    <code className="flex-1 rounded bg-slate-950 p-3 text-xs text-slate-300 break-all border border-slate-800 font-mono">
                                        {selectedClient.client_panel_api_key || selectedClient.api_key}
                                    </code>
                                    <button
                                        onClick={() => copyText(selectedClient.client_panel_api_key || selectedClient.api_key)}
                                        className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded"
                                        title={t('copy')}
                                    >
                                        <Copy className="h-4 w-4" />
                                    </button>
                                </div>
                                <p className="text-xs text-slate-500 mt-1">{t('use_client_key_msg')}</p>
                            </div>
                        </div>

                        <div className="flex justify-end mt-8">
                            <button
                                onClick={() => setSelectedClient(null)}
                                className="rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
                            >
                                {t('close')}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
