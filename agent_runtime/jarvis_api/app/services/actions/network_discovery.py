import asyncio
import ipaddress
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from app.services.kali_runner import kali_runner

logger = logging.getLogger(__name__)


class NetworkDiscoveryService:
    """Orquesta el escaneo act_80 con validaciones adicionales y parseo de Nmap."""

    def __init__(self):
        self.script_path = "/opt/deco/agent_runtime/scripts/01_network_discovery.sh"
        self.remote_output_base = "/tmp/deco_network_discovery"
        self.timeout_seconds = 60 * 60  # 60 minutos
        self._semaphore = asyncio.Semaphore(1)

    def _validate_target(self, target: str, allow_public: bool = False) -> str:
        """Valida que el target sea privado (RFC1918) salvo override explícito."""
        try:
            network = ipaddress.ip_network(target, strict=False)
            if not allow_public and not network.is_private:
                raise HTTPException(status_code=400, detail="Target fuera de rango privado (RFC1918). Añade allow_public=true para forzar.")
            return str(network)
        except ValueError:
            try:
                address = ipaddress.ip_address(target)
                if not allow_public and not address.is_private:
                    raise HTTPException(status_code=400, detail="Target fuera de rango privado (RFC1918). Añade allow_public=true para forzar.")
                return str(address)
            except ValueError:
                raise HTTPException(status_code=400, detail="Target inválido. Usa un CIDR o IP válida.")

    def _parse_nmap_xml(self, xml_path: Path) -> Dict[str, Any]:
        """Parsea XML de Nmap para construir metadata básica."""
        hosts: List[Dict[str, Any]] = []

        if not xml_path.exists():
            logger.warning(f"No se encontró XML en {xml_path}")
            return {"hosts": hosts}

        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(xml_path)
            root = tree.getroot()

            for host in root.findall("host"):
                status = host.find("status")
                if status is not None and status.get("state") != "up":
                    continue

                address = host.find("address[@addrtype='ipv4']")
                ip = address.get("addr") if address is not None else ""

                hostname_elem = host.find("hostnames/hostname")
                hostname = hostname_elem.get("name") if hostname_elem is not None else ""

                ports_data: List[Dict[str, Any]] = []
                for port in host.findall("ports/port"):
                    state_elem = port.find("state")
                    if state_elem is None or state_elem.get("state") != "open":
                        continue

                    service_elem = port.find("service")
                    ports_data.append({
                        "port": int(port.get("portid", "0")),
                        "protocol": port.get("protocol", ""),
                        "state": state_elem.get("state", ""),
                        "service": service_elem.get("name") if service_elem is not None else ""
                    })

                hosts.append({
                    "ip": ip,
                    "hostname": hostname,
                    "ports": ports_data
                })

        except Exception as e:
            logger.error(f"Error parseando XML de Nmap: {e}")

        return {"hosts": hosts}

    async def run(
        self,
        target: str,
        profile: str = "standard",
        tenant_slug: str = "global",
        node_config: Optional[Dict[str, Any]] = None,
        allow_public: bool = False
    ) -> Dict[str, Any]:
        """Ejecuta el escaneo act_80 con control de concurrencia y timeout."""
        validated_target = self._validate_target(target, allow_public=allow_public)

        if self._semaphore.locked():
            raise HTTPException(status_code=409, detail="Ya hay un escaneo de Network Discovery en curso (act_80). Intenta más tarde.")

        try:
            async with self._semaphore:
                return await asyncio.wait_for(
                    self._execute_scan(
                        target=validated_target,
                        profile=profile,
                        tenant_slug=tenant_slug,
                        node_config=node_config
                    ),
                    timeout=self.timeout_seconds + 30
                )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Tiempo máximo de ejecución alcanzado (60 minutos).")

    async def _execute_scan(
        self,
        target: str,
        profile: str,
        tenant_slug: str,
        node_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        profile_norm = profile.lower() if profile else "standard"
        execution_remote_dir = f"{self.remote_output_base}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        logger.info(f"Ejecutando act_80 sobre {target} con perfil {profile_norm} (output: {execution_remote_dir})")

        result = await kali_runner.run_script(
            action_id="act_80",
            script_path=self.script_path,
            args=[target, profile_norm, execution_remote_dir],
            tenant_slug=tenant_slug,
            node_config=node_config,
            timeout_seconds=self.timeout_seconds,
            remote_output_dir=execution_remote_dir
        )

        report_path = Path(result.get("report_path", ""))
        report_path.mkdir(parents=True, exist_ok=True)
        report_id = report_path.name

        parsed = self._parse_nmap_xml(report_path / "scan_raw.xml")

        metadata = {
            "execution_id": result.get("execution_id"),
            "action_id": "act_80",
            "action_name": "Network Discovery (Complete)",
            "target": target,
            "profile": profile_norm,
            "timestamp": datetime.now().isoformat(),
            "status": result.get("status"),
            "exit_code": result.get("exit_code"),
            "hosts": parsed.get("hosts", [])
        }

        with open(report_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        result.update({
            "report_id": report_id,
            "metadata": metadata
        })

        return result


network_discovery_service = NetworkDiscoveryService()
