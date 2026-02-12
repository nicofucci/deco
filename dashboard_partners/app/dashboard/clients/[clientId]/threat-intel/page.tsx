"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
    getGlobalThreats,
    getClientThreatMatches,
    getClientThreatSummary
} from "@/lib/partner-api";
import { ShieldAlert, Globe, Zap, CheckCircle, AlertTriangle } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import Link from "next/link";

export default function ThreatIntelPage() {
    const { clientId } = useParams();
    const clientIdStr = clientId as string;
    const { t } = useI18n();

    const [globalThreats, setGlobalThreats] = useState<any[]>([]);
    const [matches, setMatches] = useState<any[]>([]);
    const [summary, setSummary] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) return;

        Promise.all([
            getGlobalThreats(token),
            getClientThreatMatches(token, clientIdStr),
            getClientThreatSummary(token, clientIdStr)
        ]).then(([globalRes, matchesRes, summaryRes]) => {
            setGlobalThreats(globalRes);
            setMatches(matchesRes);
            setSummary(summaryRes);
        }).catch(err => {
            console.error(err);
        }).finally(() => {
            setLoading(false);
        });
    }, [clientIdStr]);

    if (loading) return <div className="p-6 text-slate-400">Loading Threat Intel...</div>;

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white flex items-center">
                <Globe className="mr-3 h-6 w-6 text-blue-400" />
                Web Threat Intelligence (WTI)
            </h1>

            {/* Panel 3: Immediate Alerts (Top Priority) */}
            {summary && summary.critical_matches > 0 && (
                <div className="rounded-lg border border-red-900/50 bg-red-900/20 p-4 animate-pulse">
                    <div className="flex items-start">
                        <ShieldAlert className="h-6 w-6 text-red-500 mr-3 mt-1" />
                        <div>
                            <h3 className="text-lg font-bold text-white">Critical Threat Matches Detected</h3>
                            <p className="text-red-300">
                                {summary.critical_matches} critical vulnerabilities match this client's assets. Immediate action is required.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Panel 2: Impact on this client */}
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold text-white flex items-center">
                        <AlertTriangle className="mr-2 h-5 w-5 text-yellow-500" />
                        Impact on Customer Assets
                    </h2>

                    <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden">
                        {matches.length === 0 ? (
                            <div className="p-6 text-slate-500 text-center">No threats currently matching client assets.</div>
                        ) : (
                            <div className="divide-y divide-slate-800">
                                {matches.map((match) => (
                                    <div key={match.id} className="p-4 hover:bg-slate-800/50 transition-colors">
                                        <div className="flex justify-between items-start mb-2">
                                            <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${match.risk_level === 'critical' ? 'bg-red-900/40 text-red-400 border border-red-900' :
                                                    'bg-yellow-900/40 text-yellow-400 border border-yellow-900'
                                                }`}>
                                                {match.risk_level}
                                            </span>
                                            <span className="text-xs text-slate-500">Reason: {match.match_reason}</span>
                                        </div>
                                        <h4 className="text-white font-medium">{match.cve}</h4>
                                        <p className="text-slate-300 text-sm mt-1">{match.title}</p>
                                        <div className="mt-3 flex items-center text-xs text-slate-500">
                                            <span className="bg-slate-800 px-2 py-1 rounded border border-slate-700 mr-2">
                                                Asset: {match.asset_ip} ({match.asset_hostname || 'N/A'})
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Panel 1: Global Threats */}
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold text-white flex items-center">
                        <Globe className="mr-2 h-5 w-5 text-blue-500" />
                        Global Threat Feed
                    </h2>

                    <div className="rounded-lg border border-slate-800 bg-slate-900 overflow-hidden max-h-[600px] overflow-y-auto">
                        <div className="divide-y divide-slate-800">
                            {globalThreats.map((threat) => (
                                <div key={threat.id} className="p-4 hover:bg-slate-800/50 transition-colors">
                                    <div className="flex justify-between items-start">
                                        <div className="flex items-center space-x-2">
                                            <span className="text-blue-400 text-sm font-bold">{threat.cve}</span>
                                            {threat.exploit_status === 'confirmed' && (
                                                <span className="px-1.5 py-0.5 rounded bg-red-900/30 text-red-400 text-[10px] border border-red-900 uppercase">
                                                    Exploit Active
                                                </span>
                                            )}
                                        </div>
                                        <span className="text-xs text-slate-500">{new Date(threat.published_at).toLocaleDateString()}</span>
                                    </div>
                                    <p className="text-slate-300 text-sm mt-1 line-clamp-2">{threat.title}</p>
                                    <div className="mt-2 flex flex-wrap gap-1">
                                        {threat.tags.map((tag: string) => (
                                            <span key={tag} className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
