"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Search, Server, Activity, FileText, LogOut } from "lucide-react";
import { useClient } from "@/providers/ClientProvider";
import clsx from "clsx";
import { useI18n } from "@/lib/i18n";

const navItems = [
    { name: "home", href: "/dashboard/home", icon: Home },
    { name: "findings", href: "/dashboard/findings", icon: Search },
    { name: "my_assets", href: "/dashboard/assets", icon: Server },
    { name: "jobs", href: "/dashboard/jobs", icon: Activity },
    { name: "reports", href: "/dashboard/reports", icon: FileText },
];

export function Sidebar() {
    const pathname = usePathname();
    const { logout } = useClient();
    const { t, language, setLanguage } = useI18n();

    return (
        <div className="flex h-full w-64 flex-col bg-slate-900 text-white">
            <div className="flex h-16 items-center justify-center border-b border-slate-800">
                <h1 className="text-xl font-bold text-blue-500">Deco-Security</h1>
            </div>

            <div className="px-4 py-2 flex justify-center space-x-2 border-b border-slate-800/50 border-2 border-red-500">
                <button
                    onClick={() => setLanguage('es')}
                    className={`text-xs px-2 py-1 rounded ${language === 'es' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                    ES
                </button>
                <button
                    onClick={() => setLanguage('en')}
                    className={`text-xs px-2 py-1 rounded ${language === 'en' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                    EN
                </button>
                <button
                    onClick={() => setLanguage('it')}
                    className={`text-xs px-2 py-1 rounded ${language === 'it' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                    IT
                </button>
            </div>

            <nav className="flex-1 space-y-1 px-2 py-4">
                {navItems.map((item) => {
                    const isActive = pathname.startsWith(item.href);
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={clsx(
                                "group flex items-center rounded-md px-2 py-2 text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-blue-600 text-white"
                                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                            )}
                        >
                            <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                            {t(item.name)}
                        </Link>
                    );
                })}
            </nav>
            <div className="border-t border-slate-800 p-4">
                <button
                    onClick={logout}
                    className="flex w-full items-center rounded-md px-2 py-2 text-sm font-medium text-red-400 hover:bg-slate-800 hover:text-red-300"
                >
                    <LogOut className="mr-3 h-5 w-5" />
                    {t('logout')}
                </button>
            </div>
        </div>
    );
}
