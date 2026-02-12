"use client";

import { Sidebar } from "@/components/Sidebar";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        const token = localStorage.getItem("deco_partner_api_key");
        if (!token) {
            router.push("/login");
            return;
        }
        const userData = localStorage.getItem("deco_partner_user");
        if (userData) {
            setUser(JSON.parse(userData));
        }
    }, [router]);

    if (!user) return null; // Or loading spinner

    return (
        <div className="flex h-screen bg-slate-900 text-slate-100">
            <Sidebar />
            <div className="flex flex-1 flex-col overflow-hidden">
                <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-950 px-6">
                    <div className="flex items-center space-x-4">
                        <span className="rounded-full bg-blue-900/30 px-3 py-1 text-xs font-medium text-blue-400 border border-blue-900">
                            Partner Console
                        </span>
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="text-sm text-right">
                            <div className="font-medium text-white">{user.name}</div>
                            <div className="text-xs text-slate-500">{user.email}</div>
                        </div>
                    </div>
                </header>
                <main className="flex-1 overflow-y-auto p-6">
                    {children}
                </main>
            </div>
        </div>
    );
}
