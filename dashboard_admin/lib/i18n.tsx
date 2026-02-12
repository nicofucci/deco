"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

type Language = 'es' | 'en' | 'it';

interface I18nContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string) => string;
}

const translations = {
    es: {
        "dashboard": "Panel de Control",
        "overview": "Resumen",
        "clients": "Clientes",
        "my_clients": "Mis Clientes",
        "assets": "Activos",
        "my_assets": "Mis Activos",
        "agents": "Agentes",
        "findings": "Hallazgos",
        "vulnerabilities": "Vulnerabilidades",
        "jobs": "Trabajos",
        "risk_ai": "Riesgo & IA",
        "reports": "Reportes",
        "billing": "Facturación",
        "earnings": "Ingresos",
        "api_keys": "Claves API",
        "profile": "Mi Perfil",
        "system": "Sistema",
        "logout": "Cerrar Sesión",
        "welcome": "Bienvenido",
        "home": "Inicio",
        "active_threats": "Amenazas Activas",
        "global_risk": "Riesgo Global",
        "managed_assets": "Activos Gestionados",
        "online_agents": "Agentes Online",
        "ia": "IA Predictiva",
        "partners": "Socios",
        "reports_center": "Centro de Reportes",
        "reports_desc": "Genera y descarga informes de seguridad en formato PDF.",
        "generate_new": "Generar Nuevo",
        "select_client": "Seleccionar Cliente",
        "exec_report": "Reporte Ejecutivo",
        "exec_desc": "Resumen gerencial",
        "tech_report": "Reporte Técnico",
        "tech_desc": "Detalles técnicos",
        "generating": "Generando PDF...",
        "report_generated": "Reporte Generado",
        "download": "Descargar",
        "history": "Historial de Reportes",
        "date": "Fecha",
        "severity": "Severidad",
        "action": "Acción",
        "ai_predictive": "IA Predictiva",
        "ai_desc": "Análisis de riesgos y recomendaciones automáticas",
        "ai_model": "Modelo Experimental v1.0",
        "risk": "Riesgo",
        "detected": "Detectado",
        "no_predictions": "No hay predicciones de riesgo activas en este momento.",
        "manage_client": "Gestionar Cliente",
        "remote_control": "Control Remoto",
        "scan_launcher": "Lanzador de Escaneos",
        "network_status": "Estado de Red",
        "new_client": "Nuevo Cliente",
        "name": "Nombre",
        "email": "Email",
        "security_summary": "Resumen de Seguridad",
        "detected_assets": "Activos Detectados",
        "total_findings": "Total Hallazgos",
        "critical_findings": "Hallazgos Críticos",
        "high_findings": "Hallazgos Altos",
        "severity_distribution": "Distribución de Severidad",
        "latest_findings": "Últimos Hallazgos"
    },
    en: {
        "dashboard": "Dashboard",
        "overview": "Overview",
        "clients": "Clients",
        "my_clients": "My Clients",
        "assets": "Assets",
        "my_assets": "My Assets",
        "agents": "Agents",
        "findings": "Findings",
        "vulnerabilities": "Vulnerabilities",
        "jobs": "Jobs",
        "risk_ai": "Risk & AI",
        "reports": "Reports",
        "billing": "Billing",
        "earnings": "Earnings",
        "api_keys": "API Keys",
        "profile": "My Profile",
        "system": "System",
        "logout": "Logout",
        "welcome": "Welcome",
        "home": "Home",
        "active_threats": "Active Threats",
        "global_risk": "Global Risk",
        "managed_assets": "Managed Assets",
        "online_agents": "Online Agents",
        "ia": "Predictive AI",
        "partners": "Partners",
        "reports_center": "Reports Center",
        "reports_desc": "Generate and download security reports in PDF format.",
        "generate_new": "Generate New",
        "select_client": "Select Client",
        "exec_report": "Executive Report",
        "exec_desc": "Management summary",
        "tech_report": "Technical Report",
        "tech_desc": "Technical details",
        "generating": "Generating PDF...",
        "report_generated": "Report Generated",
        "download": "Download",
        "history": "Report History",
        "date": "Date",
        "severity": "Severity",
        "action": "Action",
        "ai_predictive": "Predictive AI",
        "ai_desc": "Risk analysis and automatic recommendations",
        "ai_model": "Experimental Model v1.0",
        "risk": "Risk",
        "detected": "Detected",
        "no_predictions": "No active risk predictions at this moment.",
        "manage_client": "Manage Client",
        "remote_control": "Remote Control",
        "scan_launcher": "Scan Launcher",
        "network_status": "Network Status",
        "new_client": "New Client",
        "name": "Name",
        "email": "Email",
        "security_summary": "Security Summary",
        "detected_assets": "Detected Assets",
        "total_findings": "Total Findings",
        "critical_findings": "Critical Findings",
        "high_findings": "High Findings",
        "severity_distribution": "Severity Distribution",
        "latest_findings": "Latest Findings"
    },
    it: {
        "dashboard": "Pannello di Controllo",
        "overview": "Panoramica",
        "clients": "Clienti",
        "my_clients": "I Miei Clienti",
        "assets": "Asset",
        "my_assets": "I Miei Asset",
        "agents": "Agenti",
        "findings": "Risultati",
        "vulnerabilities": "Vulnerabilità",
        "jobs": "Lavori",
        "risk_ai": "Rischio & IA",
        "reports": "Report",
        "billing": "Fatturazione",
        "earnings": "Guadagni",
        "api_keys": "Chiavi API",
        "profile": "Il Mio Profilo",
        "system": "Sistema",
        "logout": "Disconnettersi",
        "welcome": "Benvenuto",
        "home": "Home",
        "active_threats": "Minacce Attive",
        "global_risk": "Rischio Globale",
        "managed_assets": "Asset Gestiti",
        "online_agents": "Agenti Online",
        "ia": "IA Predittiva",
        "partners": "Partner",
        "reports_center": "Centro Report",
        "reports_desc": "Genera e scarica report di sicurezza in formato PDF.",
        "generate_new": "Genera Nuovo",
        "select_client": "Seleziona Cliente",
        "exec_report": "Report Esecutivo",
        "exec_desc": "Riepilogo manageriale",
        "tech_report": "Report Tecnico",
        "tech_desc": "Dettagli tecnici",
        "generating": "Generazione PDF...",
        "report_generated": "Report Generato",
        "download": "Scarica",
        "history": "Cronologia Report",
        "date": "Data",
        "severity": "Gravità",
        "action": "Azione",
        "ai_predictive": "IA Predittiva",
        "ai_desc": "Analisi dei rischi e raccomandazioni automatiche",
        "ai_model": "Modello Sperimentale v1.0",
        "risk": "Rischio",
        "detected": "Rilevato",
        "no_predictions": "Nessuna previsione di rischio attiva al momento.",
        "manage_client": "Gestisci Cliente",
        "remote_control": "Controllo Remoto",
        "scan_launcher": "Avvio Scansione",
        "network_status": "Stato della Rete",
        "new_client": "Nuovo Cliente",
        "name": "Nome",
        "email": "Email",
        "security_summary": "Riepilogo Sicurezza",
        "detected_assets": "Asset Rilevati",
        "total_findings": "Totale Risultati",
        "critical_findings": "Risultati Critici",
        "high_findings": "Risultati Alti",
        "severity_distribution": "Distribuzione Gravità",
        "latest_findings": "Ultimi Risultati"
    }
};

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export function I18nProvider({ children }: { children: React.ReactNode }) {
    const [language, setLanguage] = useState<Language>(() => {
        if (typeof window !== 'undefined') {
            return (localStorage.getItem('deco_lang') as Language) || 'es';
        }
        return 'es';
    });

    const handleSetLanguage = (lang: Language) => {
        setLanguage(lang);
        localStorage.setItem('deco_lang', lang);
    };

    const t = (key: string) => {
        return translations[language][key as keyof typeof translations['es']] || key;
    };

    return (
        <I18nContext.Provider value={{ language, setLanguage: handleSetLanguage, t }}>
            {children}
        </I18nContext.Provider>
    );
}

export function useI18n() {
    const context = useContext(I18nContext);
    if (!context) {
        throw new Error('useI18n must be used within an I18nProvider');
    }
    return context;
}
