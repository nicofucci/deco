"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Handshake } from "lucide-react";
import { validatePartnerKey } from "@/lib/partner-api";

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
            const data = await validatePartnerKey(apiKey);
            // Save key consistently with client console
            localStorage.setItem("deco_partner_api_key", apiKey);
            localStorage.setItem("deco_partner_user", JSON.stringify({
                id: data.partner_id,
                name: data.name,
                email: data.email,
                mode: data.account_mode
            }));
            router.push("/dashboard/overview");
        } catch (err: any) {
            setError(err.message || "API Key inválida o error de conexión");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-950">
            <div className="w-full max-w-md rounded-lg bg-slate-900 p-8 shadow-2xl border border-slate-800">
                <div className="mb-8 flex flex-col items-center">
                    <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-900/30 text-blue-500 border border-blue-900">
                        <Handshake className="h-10 w-10" />
                    </div>
                    <h1 className="text-2xl font-bold text-white">
                        Deco Partner
                    </h1>
                    <p className="text-sm text-slate-400">
                        Acceso para Colaboradores
                    </p>
                </div>

                <form onSubmit={handleLogin} className="space-y-6">
                    <div>
                        <label htmlFor="apiKey" className="block text-sm font-medium text-slate-300">
                            Partner API Key
                        </label>
                        <input
                            id="apiKey"
                            type="text"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            className="mt-2 block w-full rounded-md border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm font-mono"
                            placeholder="Ingrese su Partner API Key"
                            required
                        />
                    </div>

                    {error && (
                        <div className="rounded-md bg-red-900/30 border border-red-900 p-3 text-sm text-red-400">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full flex justify-center rounded-md bg-blue-600 px-4 py-3 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading ? "Verificando..." : "Ingresar"}
                    </button>
                </form>
            </div>
        </div>
    );
}
