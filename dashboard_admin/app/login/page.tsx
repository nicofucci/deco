"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck, Lock, User } from "lucide-react";

const getApiUrl = () => {
    if (typeof window !== 'undefined') {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return "http://127.0.0.1:18001";
        }
    }
    return process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "https://api.deco-security.com";
};

export default function LoginPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const res = await fetch(`${getApiUrl()}/api/master/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Error de autenticación");
            }

            const data = await res.json();

            // Save Session
            localStorage.setItem("deco_admin_master_key", data.token);
            document.cookie = "deco_admin_session=true; path=/; max-age=86400; SameSite=Strict";

            router.push("/dashboard/overview");

        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-950">
            <div className="w-full max-w-md rounded-lg bg-slate-900 p-8 shadow-2xl border border-slate-800">
                <div className="mb-8 flex flex-col items-center text-center">
                    <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-900/30 text-blue-500 border border-blue-900">
                        <ShieldCheck className="h-10 w-10" />
                    </div>
                    <h1 className="text-2xl font-bold text-white">Master Console</h1>
                    <p className="text-sm text-slate-500 mt-2">Acceso Administrativo</p>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-900/20 border border-red-900 text-red-400 text-sm rounded">
                        {error}
                    </div>
                )}

                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">Usuario</label>
                        <div className="relative">
                            <User className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full bg-slate-800 border border-slate-700 rounded pl-9 pr-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                                placeholder="Usuario"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-slate-400 mb-1">Contraseña</label>
                        <div className="relative">
                            <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-slate-800 border border-slate-700 rounded pl-9 pr-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                                placeholder="••••••••"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded font-bold transition-colors mt-6"
                    >
                        {loading ? "Verificando..." : "Iniciar Sesión"}
                    </button>
                </form>
            </div>
        </div>
    );
}
