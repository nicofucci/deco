import { RiskBadge } from "./RiskBadge";
import { useI18n } from "@/lib/i18n";

interface Finding {
    id: string;
    title: string;
    severity: string;
    asset_id: string;
    asset_ip?: string;
    description: string;
    recommendation?: string;
}

interface FindingsTableProps {
    findings: Finding[];
    assets?: any[]; // Map asset_id to hostname/ip
}

export function FindingsTable({ findings, assets }: FindingsTableProps) {
    const { t } = useI18n();

    const getAssetName = (assetId: string, assetIp?: string) => {
        if (!assets) return assetId;
        const asset = assets.find((a) => a.id === assetId);
        if (asset) return asset.hostname || asset.ip;
        return assetIp || assetId;
    };

    return (
        <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-800">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
                <thead className="bg-slate-50 dark:bg-slate-900">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('severity')}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('title')}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('asset')}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('description')}
                        </th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white dark:divide-slate-800 dark:bg-slate-950">
                    {findings.map((finding) => (
                        <tr key={finding.id}>
                            <td className="whitespace-nowrap px-6 py-4">
                                <RiskBadge level={finding.severity} />
                            </td>
                            <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-900 dark:text-white">
                                {finding.title}
                            </td>
                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                {getAssetName(finding.asset_id, finding.asset_ip)}
                            </td>
                            <td className="px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                <div className="max-w-xs truncate" title={finding.description}>
                                    {finding.description}
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
