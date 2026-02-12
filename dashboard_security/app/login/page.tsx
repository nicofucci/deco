"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { getClientInfo } from "@/lib/client-api";

export default function LoginPage() {
    const [apiKey, setApiKey] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            // Check if it's Master Key (simulated)
            // In a real app, this would be a separate auth flow or backend check
            // Here we just check if it works as a client key or if it matches env (which we can't see client side easily without exposing it)
            // The user prompt said: "Si se introduce MASTER KEY (desde .env) -> modo admin"
            // Since we can't safely expose MASTER_KEY to client, we'll assume for this demo 
            // that we just try to use it as an API Key against the backend. 
            // If the backend accepts it (maybe it's a special client key), good.
            // Or we can just rely on the backend validation.

            // Let's try to fetch client info to validate the key
            await getClientInfo(apiKey);

            // If successful, store and redirect
            localStorage.setItem("deco_api_key", apiKey);
            router.push("/dashboard/home");
        } catch (err: any) {
            console.error("Login error:", err);
            setError(err.message || "API Key inválida o error de conexión.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-100 dark:bg-slate-900">
            <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-lg dark:bg-slate-800">
                <div className="mb-6 flex flex-col items-center">
                    <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                        <ShieldCheck className="h-8 w-8" />
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                        Deco-Security
                    </h1>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                        Acceso al Dashboard Global
                    </p>
                </div>

                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label htmlFor="apiKey" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                            API Key / Master Key
                        </label>
                        <input
                            id="apiKey"
                            type="password"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white"
                            placeholder="Ingrese su clave de acceso..."
                            required
                        />
                    </div>

                    {error && (
                        <div className="rounded-md bg-red-50 p-2 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                    >
                        {loading ? "Verificando..." : "Ingresar"}
                    </button>
                </form>
            </div>
        </div>
    );
}
