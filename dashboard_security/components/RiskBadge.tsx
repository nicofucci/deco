import clsx from "clsx";

interface RiskBadgeProps {
    level: string;
}

export function RiskBadge({ level }: RiskBadgeProps) {
    const normalizedLevel = level.toLowerCase();

    let colorClass = "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300";

    if (normalizedLevel === "critical" || normalizedLevel === "crítico") {
        colorClass = "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300";
    } else if (normalizedLevel === "high" || normalizedLevel === "alto") {
        colorClass = "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300";
    } else if (normalizedLevel === "medium" || normalizedLevel === "medio") {
        colorClass = "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300";
    } else if (normalizedLevel === "low" || normalizedLevel === "bajo") {
        colorClass = "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300";
    }

    return (
        <span className={clsx("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", colorClass)}>
            {level.toUpperCase()}
        </span>
    );
}
