"use client";

import { useClient } from "@/providers/ClientProvider";

export function Topbar() {
    const { clientInfo } = useClient();

    return (
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 dark:border-slate-800 dark:bg-slate-950">
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
                Dashboard Global
            </h2>
            <div className="flex items-center space-x-4">
                <div className="text-right">
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                        {clientInfo?.name || "Cargando..."}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                        {clientInfo?.email || ""}
                    </p>
                </div>
                <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                    {clientInfo?.name ? clientInfo.name[0].toUpperCase() : "?"}
                </div>
            </div>
        </header>
    );
}
