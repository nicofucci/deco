import type { Metadata } from "next";
import { Sidebar } from "@/components/Sidebar";
import { Topbar } from "@/components/Topbar";
import { ClientProvider } from "@/providers/ClientProvider";

export const metadata: Metadata = {
    title: "Resumen",
};

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <ClientProvider>
            <div className="flex h-screen bg-slate-50 dark:bg-slate-950">
                <Sidebar />
                <div className="flex flex-1 flex-col overflow-hidden">
                    <Topbar />
                    <main className="flex-1 overflow-y-auto p-6">
                        {children}
                    </main>
                </div>
            </div>
        </ClientProvider>
    );
}
