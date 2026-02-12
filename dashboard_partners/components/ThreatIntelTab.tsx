
import React, { useState, useEffect } from 'react';
import {
    Shield, AlertTriangle, Cloud, Lock, ExternalLink,
    RefreshCw, Filter, AlertOctagon
} from 'lucide-react';
import { getClientThreatMatches, getGlobalThreats } from '@/lib/partner-api';

// Types (simplified)
interface GlobalThreat {
    id: string;
    source: string;
    cve: string;
    title: string;
    published_at: string;
    tags: string[];
    exploit_status: string;
    risk_score_base: number;
}

interface ClientMatch {
    id: string;
    cve: string;
    title: string;
    asset_ip: string;
    asset_hostname: string;
    match_reason: string;
    risk_level: string;
}

export default function ThreatIntelTab({ clientId }: { clientId: string }) {
    const [activeView, setActiveView] = useState<'matches' | 'global'>('matches');
    const [matches, setMatches] = useState<ClientMatch[]>([]);
    const [globalThreats, setGlobalThreats] = useState<GlobalThreat[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, [clientId]);

    const loadData = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem("deco_partner_api_key");
            if (!token) return;

            const [matchesData, globalData] = await Promise.all([
                getClientThreatMatches(token, clientId),
                getGlobalThreats(token)
            ]);

            setMatches(matchesData);
            setGlobalThreats(globalData);
        } catch (e) {
            console.error("Failed to load WTI data", e);
        } finally {
            setLoading(false);
        }
    };

    const getRiskColor = (level: string) => {
        switch (level.toLowerCase()) {
            case 'critical': return 'text-red-500 bg-red-950 border-red-900';
            case 'high': return 'text-orange-500 bg-orange-950 border-orange-900';
            case 'medium': return 'text-yellow-500 bg-yellow-950 border-yellow-900';
            default: return 'text-blue-500 bg-blue-950 border-blue-900';
        }
    };

    if (loading) return <div className="p-8 text-center text-slate-500">Cargando Inteligencia de Amenazas...</div>;

    return (
        <div className="space-y-6">
            {/* Header Actions */}
            <div className="flex justify-between items-center bg-slate-900/50 p-4 rounded-lg border border-slate-800">
                <div>
                    <h2 className="text-xl font-bold flex items-center gap-2 text-white">
                        <Cloud className="w-5 h-5 text-cyan-400" />
                        Web Threat Intelligence (WTI)
                    </h2>
                    <p className="text-sm text-slate-400">Inteligencia global correlacionada con activos locales.</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveView('matches')}
                        className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${activeView === 'matches' ? 'bg-cyan-900 text-cyan-200 border border-cyan-700' : 'text-slate-400 hover:text-white'}`}
                    >
                        Impacto Cliente ({matches.length})
                    </button>
                    <button
                        onClick={() => setActiveView('global')}
                        className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${activeView === 'global' ? 'bg-indigo-900 text-indigo-200 border border-indigo-700' : 'text-slate-400 hover:text-white'}`}
                    >
                        Feed Global
                    </button>
                    <button onClick={loadData} className="p-2 hover:bg-slate-800 rounded text-slate-400">
                        <RefreshCw className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {activeView === 'matches' && (
                <div className="grid gap-4">
                    {matches.length === 0 ? (
                        <div className="p-10 border border-slate-800 rounded-lg text-center bg-slate-900/30">
                            <Shield className="w-12 h-12 text-green-500 mx-auto mb-4 opacity-50" />
                            <h3 className="text-lg font-medium text-white mb-1">Sin amenazas correlacionadas</h3>
                            <p className="text-slate-400 text-sm">No se han detectado intersecciones entre el feed global y los activos del cliente.</p>
                        </div>
                    ) : (
                        matches.map(match => (
                            <div key={match.id} className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col md:flex-row gap-4 items-start md:items-center">
                                <div className={`p-3 rounded-full border ${getRiskColor(match.risk_level)} bg-opacity-20`}>
                                    <AlertOctagon className="w-6 h-6" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h3 className="text-lg font-bold text-white">{match.title}</h3>
                                        <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono">{match.cve}</span>
                                    </div>
                                    <div className="text-sm text-slate-400 flex flex-wrap gap-x-4 gap-y-1">
                                        <span className="flex items-center gap-1"><Lock className="w-3 h-3" /> Afecta a: <span className="text-slate-200">{match.asset_hostname || match.asset_ip}</span></span>
                                        <span className="flex items-center gap-1"><Filter className="w-3 h-3" /> Razón: {match.match_reason}</span>
                                    </div>
                                </div>
                                <div>
                                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold uppercase rounded shadow-lg shadow-blue-900/20">
                                        Ver Mitigación
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {activeView === 'global' && (
                <div className="overflow-x-auto bg-slate-900 rounded-lg border border-slate-800">
                    <table className="w-full text-left text-sm text-slate-400">
                        <thead className="bg-slate-950 text-slate-200 uppercase text-xs font-bold">
                            <tr>
                                <th className="px-4 py-3">CVE</th>
                                <th className="px-4 py-3">Título</th>
                                <th className="px-4 py-3">Fecha</th>
                                <th className="px-4 py-3">Source</th>
                                <th className="px-4 py-3">Tags</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800">
                            {globalThreats.map(threat => (
                                <tr key={threat.id} className="hover:bg-slate-800/50">
                                    <td className="px-4 py-3 font-mono text-white">{threat.cve}</td>
                                    <td className="px-4 py-3 text-slate-300 font-medium">{threat.title}</td>
                                    <td className="px-4 py-3">{new Date(threat.published_at).toLocaleDateString()}</td>
                                    <td className="px-4 py-3 uppercase text-xs font-bold tracking-wider">{threat.source}</td>
                                    <td className="px-4 py-3">
                                        <div className="flex gap-1 flex-wrap">
                                            {threat.tags.map(tag => (
                                                <span key={tag} className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700 text-slate-400">
                                                    {tag}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
