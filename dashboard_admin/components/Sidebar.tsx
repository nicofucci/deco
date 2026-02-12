"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, Users, Radio, Activity, AlertTriangle, Briefcase, Server, Shield, LogOut, Database, BrainCircuit } from "lucide-react";
import clsx from "clsx";
import { useI18n } from "@/lib/i18n";

const navigation = [
    { name: 'overview', href: '/dashboard/overview', icon: LayoutDashboard },
    { name: 'clients', href: '/dashboard/clients', icon: Users },
    { name: 'assets', href: '/dashboard/assets', icon: Database },
    { name: 'agents', href: '/dashboard/agents', icon: Radio },
    { name: 'jobs', href: '/dashboard/jobs', icon: Activity },
    { name: 'findings', href: '/dashboard/findings', icon: AlertTriangle },
    { name: 'ia', href: '/dashboard/ia', icon: BrainCircuit },
    { name: 'partners', href: '/dashboard/partners', icon: Briefcase },
    { name: 'system', href: '/dashboard/system', icon: Server },
];

export default function Sidebar() {
    const pathname = usePathname();
    const router = useRouter();
    const { t, language, setLanguage } = useI18n();

    const handleLogout = () => {
        document.cookie = "deco_admin_session=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;";
        localStorage.removeItem("deco_admin_master_key");
        router.push("/login");
    };

    return (
        <div className="flex h-full w-64 flex-col bg-slate-900 border-r border-slate-800">
            <div className="flex h-16 items-center px-6 border-b border-slate-800 justify-between">
                <div className="flex items-center">
                    <Shield className="h-8 w-8 text-blue-500 mr-2" />
                    <span className="text-lg font-bold text-white">Deco Tower</span>
                </div>
            </div>

            <div className="px-4 py-2 flex justify-center space-x-2 border-b border-slate-800/50">
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
                {navigation.map((item) => {
                    const isActive = pathname.startsWith(item.href);
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={clsx(
                                "group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors",
                                isActive
                                    ? "bg-slate-800 text-white"
                                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                            )}
                        >
                            <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                            {t(item.name)}
                        </Link>
                    );
                })}
                <div className="my-4 border-t border-slate-800 mx-2"></div>
                <Link href="/dashboard/risk" className="block px-4 py-2 hover:bg-slate-800 rounded transition-colors text-rose-400">{t('risk_ai')}</Link>
                <Link href="/dashboard/reports" className="block px-4 py-2 hover:bg-slate-800 rounded transition-colors">{t('reports')}</Link>
                <Link href="/dashboard/billing" className="block px-4 py-2 hover:bg-slate-800 rounded transition-colors text-yellow-400">{t('billing')}</Link>
                <Link href="/dashboard/mobile" className="block px-4 py-2 hover:bg-slate-800 rounded transition-colors text-blue-400">App Móvil</Link>
            </nav>
            <div className="border-t border-slate-800 p-4">
                <button
                    onClick={handleLogout}
                    className="flex w-full items-center rounded-md px-2 py-2 text-sm font-medium text-red-400 hover:bg-slate-900 hover:text-red-300"
                >
                    <LogOut className="mr-3 h-5 w-5" />
                    Cerrar Sesión
                </button>
            </div>
        </div>
    );
}
