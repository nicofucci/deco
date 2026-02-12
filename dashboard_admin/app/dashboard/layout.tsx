import Sidebar from "@/components/Sidebar";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex h-screen bg-slate-900 text-slate-100">
            <Sidebar />
            <div className="flex flex-1 flex-col overflow-hidden">
                <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-950 px-6">
                    <div className="flex items-center space-x-4">
                        <span className="rounded-full bg-green-900/30 px-3 py-1 text-xs font-medium text-green-400 border border-green-900">
                            System: ONLINE
                        </span>
                        <span className="text-xs text-slate-500">v0.1.0</span>
                    </div>
                    <div className="text-sm font-medium text-slate-400">
                        {process.env.NEXT_PUBLIC_ADMIN_PANEL_NAME}
                    </div>
                </header>
                <main className="flex-1 overflow-y-auto p-6">
                    {children}
                </main>
            </div>
        </div>
    );
}
