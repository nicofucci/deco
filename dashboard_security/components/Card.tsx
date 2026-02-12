import React from "react";
import clsx from "clsx";

interface CardProps {
    title: string;
    value?: string | number;
    description?: string;
    icon?: React.ElementType;
    className?: string;
    children?: React.ReactNode;
}

export function Card({ title, value, description, icon: Icon, className, children }: CardProps) {
    return (
        <div className={clsx("rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-950", className)}>
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</h3>
                {Icon && <Icon className="h-4 w-4 text-slate-500 dark:text-slate-400" />}
            </div>
            {value !== undefined && (
                <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{value}</div>
            )}
            {description && (
                <p className="text-xs text-slate-500 dark:text-slate-400">{description}</p>
            )}
            {children}
        </div>
    );
}
