interface Job {
    id: string;
    type: string;
    target: string;
    status: string;
    created_at: string;
    finished_at?: string;
}

import { Trash2 } from "lucide-react";
import { useI18n } from "@/lib/i18n";

interface JobTableProps {
    jobs: Job[];
    onDelete: (id: string) => void;
}

export function JobTable({ jobs, onDelete }: JobTableProps) {
    const { t } = useI18n();
    return (
        <div className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-800">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
                <thead className="bg-slate-50 dark:bg-slate-900">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('id')}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('type')}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('target')}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('status')}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('created')}
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('finished')}
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            {t('actions')}
                        </th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white dark:divide-slate-800 dark:bg-slate-950">
                    {jobs.map((job) => (
                        <tr key={job.id}>
                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                {job.id.slice(0, 8)}...
                            </td>
                            <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-900 dark:text-white">
                                {job.type}
                            </td>
                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                {job.target}
                            </td>
                            <td className="whitespace-nowrap px-6 py-4">
                                <span
                                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${job.status === "done"
                                        ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                                        : job.status === "running"
                                            ? "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
                                            : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300"
                                        }`}
                                >
                                    {job.status.toUpperCase()}
                                </span>
                            </td>
                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                {new Date(job.created_at).toLocaleString()}
                            </td>
                            <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500 dark:text-slate-400">
                                {job.finished_at ? new Date(job.finished_at).toLocaleString() : t('pending')}
                            </td>
                            <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                                <button
                                    onClick={() => onDelete(job.id)}
                                    className="text-slate-400 hover:text-red-600 transition-colors"
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
    );
}
