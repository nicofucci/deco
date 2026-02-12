from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.catalog import Service, Action, ActionCategory, ActionLevel, ServiceType, ServiceActionLink

router = APIRouter()

# --- ACCIONES TÉCNICAS (MOCK ~80) ---
MOCK_ACTIONS = [
    # 01-10: Recon & Scanning
    Action(id="act_01", code="01", name="Network Discovery", category=ActionCategory.SCANNING, level=ActionLevel.BASIC, script_path_kali="/opt/deco/agent_runtime/scripts/actions/01_network_scan.sh", description="Descubrimiento de hosts y puertos básicos.", tags=["network", "recon"]),
    Action(id="act_02", code="02", name="Service Enumeration", category=ActionCategory.SCANNING, level=ActionLevel.INTERMEDIATE, script_path_kali="/opt/deco/agent_runtime/scripts/actions/01_network_scan.sh", description="Enumeración detallada de servicios y versiones.", tags=["network", "enum"]),
    Action(id="act_03", code="03", name="Vuln Scan (Light)", category=ActionCategory.SCANNING, level=ActionLevel.BASIC, script_path_kali="/opt/deco/agent_runtime/scripts/actions/30_web_scan.sh", description="Escaneo rápido de vulnerabilidades conocidas.", tags=["vuln", "cve"]),
    
    # 10-20: Hardening & Compliance
    Action(id="act_10", code="10", name="Linux Hardening Check", category=ActionCategory.HARDENING, level=ActionLevel.INTERMEDIATE, script_path_kali="/opt/deco/agent_runtime/scripts/actions/10_server_hardening.sh", description="Auditoría de configuración segura en Linux.", tags=["linux", "hardening"]),
    Action(id="act_11", code="11", name="SSH Audit", category=ActionCategory.HARDENING, level=ActionLevel.BASIC, script_path_kali="/opt/deco/agent_runtime/scripts/actions/10_server_hardening.sh", description="Verificación de seguridad en configuración SSH.", tags=["ssh", "compliance"]),
    
    # 20-30: Wi-Fi & Network
    Action(id="act_20", code="20", name="Wi-Fi Spectrum Analysis", category=ActionCategory.RECON, level=ActionLevel.ADVANCED, script_path_kali="/opt/deco/agent_runtime/scripts/actions/20_wifi_audit.sh", description="Análisis de espectro y redes Wi-Fi cercanas.", tags=["wifi", "rf"]),
    Action(id="act_21", code="21", name="Rogue AP Detection", category=ActionCategory.SCANNING, level=ActionLevel.ADVANCED, script_path_kali="/opt/deco/agent_runtime/scripts/actions/20_wifi_audit.sh", description="Detección de puntos de acceso no autorizados.", tags=["wifi", "security"]),

    # 30-40: Web & App
    Action(id="act_30", code="30", name="Web Crawler", category=ActionCategory.OSINT, level=ActionLevel.BASIC, script_path_kali="/opt/deco/agent_runtime/scripts/actions/30_web_scan.sh", description="Mapeo de estructura de sitio web.", tags=["web", "spider"]),
    Action(id="act_31", code="31", name="SQLi Scanner", category=ActionCategory.EXPLOITATION, level=ActionLevel.ADVANCED, risk="high", script_path_kali="/opt/deco/agent_runtime/scripts/actions/30_web_scan.sh", description="Pruebas de inyección SQL.", tags=["web", "sqli"]),

    # 40-50: OT & IoT
    Action(id="act_40", code="40", name="Modbus Discovery", category=ActionCategory.SCANNING, level=ActionLevel.ADVANCED, script_path_kali="/opt/deco/agent_runtime/scripts/actions/40_ot_scan.sh", description="Detección de dispositivos Modbus/TCP.", tags=["ot", "scada"]),
    
    # 50-60: Privacy & OSINT
    Action(id="act_50", code="50", name="Email Breach Check", category=ActionCategory.OSINT, level=ActionLevel.BASIC, script_path_kali="/opt/deco/agent_runtime/scripts/actions/50_osint_scan.sh", description="Búsqueda de correos en filtraciones públicas.", tags=["osint", "privacy"]),
    
    # 60-70: Phishing
    Action(id="act_60", code="60", name="Domain Typosquatting", category=ActionCategory.OSINT, level=ActionLevel.INTERMEDIATE, script_path_kali="/opt/deco/agent_runtime/scripts/actions/50_osint_scan.sh", description="Búsqueda de dominios similares maliciosos.", tags=["phishing", "brand"]),

    # 70-80: Incident Response
    Action(id="act_70", code="70", name="Log Collection", category=ActionCategory.REPORTING, level=ActionLevel.BASIC, script_path_kali="/opt/deco/agent_runtime/scripts/actions/70_log_collector.sh", description="Recolección de logs de sistema.", tags=["ir", "forensics"]),
    
    # 80-84: Complete Network Scan (Multi-Stage)
    Action(id="act_80", code="80", name="Network Discovery (Complete)", category=ActionCategory.SCANNING, level=ActionLevel.ADVANCED, script_path_kali="/opt/deco/agent_runtime/scripts/01_network_discovery.sh", description="Descubrimiento exhaustivo de todos los dispositivos en la red.", tags=["network", "discovery", "complete"]),
    Action(id="act_81", code="81", name="OS Detection (Complete)", category=ActionCategory.SCANNING, level=ActionLevel.ADVANCED, script_path_kali="/opt/deco/agent_runtime/scripts/services/network_scan_complete/02_os_detection.sh", description="Identificación de sistemas operativos y servicios.", tags=["os", "fingerprint", "complete"]),
    Action(id="act_82", code="82", name="Vulnerability Scan (Complete)", category=ActionCategory.SCANNING, level=ActionLevel.ADVANCED, script_path_kali="/opt/deco/agent_runtime/scripts/services/network_scan_complete/03_vulnerability_scan.sh", description="Escaneo profundo de vulnerabilidades con NSE, Nikto y Enum4Linux.", tags=["vuln", "cve", "complete"]),
    Action(id="act_83", code="83", name="Exploit Research", category=ActionCategory.EXPLOITATION, level=ActionLevel.ADVANCED, risk="medium", script_path_kali="/opt/deco/agent_runtime/scripts/services/network_scan_complete/04_exploit_research.sh", description="Investigación de exploits disponibles para vulnerabilidades encontradas.", tags=["exploit", "research", "complete"]),
]

# --- SERVICIOS DE NEGOCIO (12) ---
MOCK_SERVICES = [
    Service(
        id="srv_soc", slug="soc-basic", name="SOC-as-a-Service Básico", category="Monitorización", type=ServiceType.MANAGED, level=ActionLevel.INTERMEDIATE,
        description="Monitorización de eventos críticos, detección de anomalías simples, revisión periódica de logs.",
        tags=["soc", "monitoring"],
        pipeline=[ServiceActionLink(action_id="act_01", order=1, role="discovery"), ServiceActionLink(action_id="act_70", order=2, role="log_collection")]
    ),
    Service(
        id="srv_mdr", slug="mdr", name="MDR (Managed Detection & Response)", category="Respuesta", type=ServiceType.MANAGED, level=ActionLevel.ADVANCED,
        description="Correlación de alertas, priorización de incidentes, guías de respuesta paso a paso.",
        tags=["mdr", "ir"],
        pipeline=[ServiceActionLink(action_id="act_70", order=1, role="triage"), ServiceActionLink(action_id="act_10", order=2, role="containment")]
    ),
    Service(
        id="srv_bas", slug="bas", name="BAS – Breach & Attack Simulation", category="Simulación", type=ServiceType.PENTEST, level=ActionLevel.ADVANCED,
        description="Escaneos de red y servicios, simulaciones de ataque controladas.",
        tags=["bas", "simulation"],
        pipeline=[ServiceActionLink(action_id="act_01", order=1, role="recon"), ServiceActionLink(action_id="act_31", order=2, role="attack_sim")]
    ),
    Service(
        id="srv_devsecops", slug="devsecops", name="DevSecOps & CI/CD Seguro", category="Desarrollo", type=ServiceType.DEVSECOPS, level=ActionLevel.INTERMEDIATE,
        description="Escaneos de vulnerabilidades en código/repos, revisiones básicas de pipelines.",
        tags=["devops", "code"],
        pipeline=[ServiceActionLink(action_id="act_03", order=1, role="sast")]
    ),
    Service(
        id="srv_asm", slug="asm", name="Auditoría de Superficie de Ataque (ASM)", category="Infraestructura", type=ServiceType.PENTEST, level=ActionLevel.BASIC,
        description="Descubrimiento de activos, mapeo de puertos/servicios expuestos.",
        tags=["asm", "recon"],
        pipeline=[ServiceActionLink(action_id="act_01", order=1, role="discovery"), ServiceActionLink(action_id="act_02", order=2, role="enumeration")]
    ),
    Service(
        id="srv_hardening", slug="hardening", name="Hardening 360º", category="Infraestructura", type=ServiceType.PENTEST, level=ActionLevel.INTERMEDIATE,
        description="Comprobación de configuraciones inseguras y recomendaciones de hardening.",
        tags=["hardening", "servers"],
        pipeline=[ServiceActionLink(action_id="act_10", order=1, role="linux_audit"), ServiceActionLink(action_id="act_11", order=2, role="ssh_audit")]
    ),
    Service(
        id="srv_wifi", slug="wifi-sec", name="Seguridad Wi-Fi & Redes", category="Redes", type=ServiceType.PENTEST, level=ActionLevel.ADVANCED,
        description="Revisión de redes, cifrados, contraseñas débiles y segmentación.",
        tags=["wifi", "network"],
        pipeline=[ServiceActionLink(action_id="act_20", order=1, role="spectrum"), ServiceActionLink(action_id="act_21", order=2, role="rogue_scan")]
    ),
    Service(
        id="srv_ot", slug="ot-sec", name="Seguridad OT/5G", category="Industrial", type=ServiceType.PENTEST, level=ActionLevel.ADVANCED,
        description="Detección de dispositivos industriales / IoT y revisión de riesgos.",
        tags=["ot", "iot", "5g"],
        pipeline=[ServiceActionLink(action_id="act_40", order=1, role="modbus_scan")]
    ),
    Service(
        id="srv_privacy", slug="privacy", name="Privacidad y Huella Digital", category="Privacidad", type=ServiceType.MANAGED, level=ActionLevel.BASIC,
        description="Revisión de servicios expuestos y datos sensibles accesibles.",
        tags=["privacy", "osint"],
        pipeline=[ServiceActionLink(action_id="act_50", order=1, role="leak_check")]
    ),
    Service(
        id="srv_phishing", slug="phishing", name="Phishing & Concienciación", category="Ingeniería Social", type=ServiceType.TRAINING, level=ActionLevel.BASIC,
        description="Simulaciones básicas de phishing y recomendaciones de formación.",
        tags=["phishing", "training"],
        pipeline=[ServiceActionLink(action_id="act_60", order=1, role="domain_check")]
    ),
    Service(
        id="srv_ir", slug="ir-basic", name="Respuesta a Incidentes (IR)", category="Respuesta", type=ServiceType.MANAGED, level=ActionLevel.ADVANCED,
        description="Recogida de evidencias y snapshot de estado post-incidente.",
        tags=["ir", "forensics"],
        pipeline=[ServiceActionLink(action_id="act_70", order=1, role="evidence_collection")]
    ),
    Service(
        id="srv_report", slug="reporting", name="Reporting y Cumplimiento", category="Gestión", type=ServiceType.MANAGED, level=ActionLevel.BASIC,
        description="Generación de informes estructurados para auditorías.",
        tags=["compliance", "reporting"],
        pipeline=[ServiceActionLink(action_id="act_10", order=1, role="audit_check")]
    ),
    Service(
        id="srv_network_scan_complete", slug="network-scan-complete", name="Scaneo Completo de Red", category="Seguridad de Red", type=ServiceType.PENTEST, level=ActionLevel.ADVANCED,
        description="Análisis exhaustivo de seguridad de red en 4 etapas: descubrimiento completo de dispositivos (PCs, móviles, cámaras, APs), detección de SO y servicios, escaneo profundo de vulnerabilidades, e investigación de exploits. Incluye análisis con IA y reportes técnicos y ejecutivos.",
        tags=["network", "complete", "pentest", "vuln", "exploit"],
        pipeline=[
            ServiceActionLink(action_id="act_80", order=1, role="discovery"),
            ServiceActionLink(action_id="act_81", order=2, role="os_detection"),
            ServiceActionLink(action_id="act_82", order=3, role="vuln_scan"),
            ServiceActionLink(action_id="act_83", order=4, role="exploit_research")
        ]
    ),
]

@router.get("/services", response_model=List[Service])
async def get_services():
    return MOCK_SERVICES

@router.get("/services/{service_id}", response_model=Service)
async def get_service(service_id: str):
    service = next((s for s in MOCK_SERVICES if s.id == service_id), None)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.get("/actions", response_model=List[Action])
async def get_actions():
    return MOCK_ACTIONS

@router.get("/actions/{action_id}", response_model=Action)
async def get_action(action_id: str):
    action = next((a for a in MOCK_ACTIONS if a.id == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action
