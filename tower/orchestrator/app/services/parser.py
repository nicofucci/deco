from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class FindingData:
    def __init__(self, title: str, severity: str, description: str, recommendation: str):
        self.title = title
        self.severity = severity
        self.description = description
        self.recommendation = recommendation

class FindingsParser:
    """
    Motor de análisis inteligente para convertir resultados crudos en Findings estructurados.
    """

    SEVERITY_CRITICAL = "critical"
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"
    SEVERITY_INFO = "info"

    def parse(self, raw_data: Dict[str, Any]) -> List[FindingData]:
        """
        Analiza el raw_data y devuelve una lista de Findings detectados.
        """
        findings = []
        
        # Detectar tipo de herramienta (por ahora asumimos estructura genérica o nmap-simulado)
        tool = raw_data.get("tool", "unknown")
        
        # Lógica para puertos abiertos (común en discovery/nmap)
        # Esperamos una estructura tipo: {"open_ports": [22, 80], ...} o similar
        # O la estructura del simulador: {"raw_data": {"tool": "nmap-simulado", "hosts_found": 5, "target": "..."}}
        # El simulador actual no manda puertos detallados en el ejemplo, pero el requerimiento dice:
        # "Dado un JSON simulado con puertos (22, 80, 445, 3389)"
        
        # Vamos a soportar una lista de puertos en el root del raw_data o dentro de 'ports'
        ports = raw_data.get("ports", [])
        if not ports and "open_ports" in raw_data:
            ports = raw_data["open_ports"]
            
        # Si es un dict de hosts (nmap real), la lógica sería más compleja. 
        # Para esta fase, asumimos una lista plana de puertos detectados en el activo reportado.
        
        for port in ports:
            port_num = int(port)
            finding = self._analyze_port(port_num)
            if finding:
                findings.append(finding)

        # Reglas adicionales (ej. OS obsoleto, etc.) pueden ir aquí
        
        return findings

    def _analyze_port(self, port: int) -> Optional[FindingData]:
        if port == 445:
            return FindingData(
                title="Puerto SMB (445) Expuesto",
                severity=self.SEVERITY_CRITICAL,
                description="El puerto 445 (SMB) está abierto a internet o a la red. Esto es un vector de ataque crítico para ransomware (WannaCry, etc).",
                recommendation="Bloquear el puerto 445 en el firewall perimetral inmediatamente. Deshabilitar SMBv1 si está activo."
            )
        
        if port == 3389:
            return FindingData(
                title="RDP (3389) Expuesto",
                severity=self.SEVERITY_CRITICAL,
                description="El servicio de Escritorio Remoto (RDP) está expuesto. Es un objetivo frecuente para ataques de fuerza bruta.",
                recommendation="Cerrar el puerto 3389 al exterior. Usar VPN para acceso remoto. Habilitar NLA (Network Level Authentication)."
            )
            
        if port == 22:
            return FindingData(
                title="SSH (22) Expuesto",
                severity=self.SEVERITY_MEDIUM,
                description="El servicio SSH está accesible. Si no está bien configurado, es vulnerable a fuerza bruta.",
                recommendation="Restringir acceso por IP. Usar autenticación por llaves (no passwords). Cambiar puerto por defecto si es posible (seguridad por oscuridad, pero ayuda con el ruido)."
            )
            
        if port == 23:
            return FindingData(
                title="Telnet (23) Detectado",
                severity=self.SEVERITY_HIGH,
                description="Telnet es un protocolo inseguro que transmite credenciales en texto plano.",
                recommendation="Deshabilitar Telnet inmediatamente. Reemplazar por SSH."
            )
            
        if port in [80, 443]:
            return FindingData(
                title=f"Servicio Web ({port}) Detectado",
                severity=self.SEVERITY_LOW,
                description=f"Se detectó un servidor web en el puerto {port}.",
                recommendation="Asegurar que el servidor web esté actualizado. Usar HTTPS (443) y redirigir tráfico HTTP (80). Verificar cabeceras de seguridad."
            )
            
        if port == 1900: # UPnP
             return FindingData(
                title="UPnP (1900) Expuesto",
                severity=self.SEVERITY_HIGH,
                description="Universal Plug and Play (UPnP) expuesto puede permitir a atacantes reconfigurar el router.",
                recommendation="Deshabilitar UPnP en el router/firewall."
            )

        return None
