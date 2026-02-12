"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getClientInfo } from "@/lib/client-api";

interface ClientContextType {
    apiKey: string | null;
    clientInfo: any | null;
    riskLevel: string;
    setApiKey: (key: string) => void;
    logout: () => void;
}

const ClientContext = createContext<ClientContextType>({
    apiKey: null,
    clientInfo: null,
    riskLevel: "Unknown",
    setApiKey: () => { },
    logout: () => { },
});

export const useClient = () => useContext(ClientContext);

export function ClientProvider({ children }: { children: React.ReactNode }) {
    const [apiKey, setApiKeyState] = useState<string | null>(null);
    const [clientInfo, setClientInfo] = useState<any | null>(null);
    const [riskLevel, setRiskLevel] = useState("Unknown");
    const router = useRouter();

    useEffect(() => {
        // Load from localStorage on mount
        const storedKey = localStorage.getItem("deco_api_key");
        if (storedKey) {
            setApiKey(storedKey);
        }
    }, []);

    const setApiKey = async (key: string) => {
        setApiKeyState(key);
        localStorage.setItem("deco_api_key", key);

        try {
            const info = await getClientInfo(key);
            setClientInfo(info);
            // In a real app, risk level might come from client info or a separate call
            // For now, we'll default or fetch it later
            setRiskLevel("Calculando...");
        } catch (e) {
            console.error("Invalid API Key", e);
            logout();
        }
    };

    const logout = () => {
        setApiKeyState(null);
        setClientInfo(null);
        localStorage.removeItem("deco_api_key");
        router.push("/login");
    };

    return (
        <ClientContext.Provider value={{ apiKey, clientInfo, riskLevel, setApiKey, logout }}>
            {children}
        </ClientContext.Provider>
    );
}
