import asyncio
import os
import logging
import json
import shlex
import shutil
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from app.services.ollama_client import JarvisOllamaClient
import httpx

logger = logging.getLogger(__name__)

class KaliRunner:
    """Motor de ejecución para acciones en Kali-2025."""
    
    def __init__(self, host: str = "kali-2025", user: str = "kali", key_path: str = None):
        self.host = host
        self.user = user
        self.key_path = key_path
        # Detectar si estamos en modo simulación (si no hay conexión real configurada)
        self.mock_mode = os.getenv("DECO_MOCK_KALI", "true").lower() == "true"
        self.reports_base_path = "/opt/deco/reports"
        self.ollama_client = JarvisOllamaClient()

    async def run_action(self, action_id: str, script_path: str, target: str, params: Dict[str, Any] = None, node_config: Dict[str, Any] = None, tenant_slug: str = "global") -> Dict[str, Any]:
        """Ejecuta una acción individual."""
        execution_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Estructura de carpetas Multi-Tenant: /reports/{tenant}/{action}/{timestamp}
        report_path = f"{self.reports_base_path}/{tenant_slug}/{action_id}/{timestamp}_{execution_id}"
        
        # Determinar host de ejecución
        exec_host = self.host
        exec_user = self.user
        
        if node_config:
            exec_host = node_config.get("host", self.host)
            exec_user = node_config.get("user", self.user)
            logger.info(f"Using custom node: {exec_host} ({node_config.get('name', 'Unknown')})")
        
        logger.info(f"Starting execution {execution_id} for action {action_id} on {target} via {exec_host} (Tenant: {tenant_slug})")
        
        # Determinar modo de ejecución
        if self.mock_mode:
            return await self._run_mock(execution_id, action_id, script_path, target, report_path)
        
        # Si el host es local, ejecutar directamente sin SSH
        if exec_host in ["localhost", "127.0.0.1"]:
            logger.info(f"Executing locally on {exec_host}")
            return await self._run_local(execution_id, action_id, script_path, target, report_path, output_dir="/tmp/deco_results")
        else:
            # Si es kali-2025, asegurar que esté encendida
            if exec_host == "kali-2025":
                await self._ensure_vm_started("kali-2025")

                try:
                    return await self._run_qemu_script(
                        execution_id=execution_id,
                        action_id=action_id,
                        script_path=script_path,
                        args=[target],
                        report_path=report_path,
                        timeout_seconds=3600,
                        remote_output_dir="/tmp/deco_results"
                    )
                except Exception as e:
                    logger.error(f"QEMU Agent execution failed: {e}. Falling back to SSH.")

            # Ejecución real vía SSH
            return await self._run_ssh(execution_id, action_id, script_path, target, report_path, host=exec_host, user=exec_user, remote_output_dir="/tmp/deco_results")

    async def run_script(
        self,
        action_id: str,
        script_path: str,
        args: List[str],
        tenant_slug: str = "global",
        node_config: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 3600,
        remote_output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ejecuta un script arbitrario con soporte de timeouts y sincronización de artefactos."""
        execution_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.reports_base_path}/{tenant_slug}/{action_id}/{timestamp}_{execution_id}"

        exec_host = self.host
        exec_user = self.user

        if node_config:
            exec_host = node_config.get("host", self.host)
            exec_user = node_config.get("user", self.user)
            logger.info(f"Using custom node: {exec_host} ({node_config.get('name', 'Unknown')})")

        logger.info(f"Starting script {script_path} (action {action_id}) on {exec_host} with args {args}")

        if self.mock_mode:
            return await self._run_mock_script(
                execution_id=execution_id,
                action_id=action_id,
                script_path=script_path,
                args=args,
                report_path=report_path
            )

        if exec_host in ["localhost", "127.0.0.1"]:
            logger.info(f"Executing locally on {exec_host}")
            return await self._run_local_script(
                execution_id=execution_id,
                action_id=action_id,
                script_path=script_path,
                args=args,
                report_path=report_path,
                timeout_seconds=timeout_seconds,
                output_dir=remote_output_dir
        )

        if exec_host == "kali-2025":
            await self._ensure_vm_started("kali-2025")
            # Fallback to QEMU agent if SSH is problematic or as primary method
            try:
                return await self._run_qemu_script(
                    execution_id=execution_id,
                    action_id=action_id,
                    script_path=script_path,
                    args=args,
                    report_path=report_path,
                    timeout_seconds=timeout_seconds,
                    remote_output_dir=remote_output_dir
                )
            except Exception as e:
                logger.error(f"QEMU Agent execution failed: {e}. Falling back to SSH.")

        return await self._run_ssh_script(
            execution_id=execution_id,
            action_id=action_id,
            script_path=script_path,
            args=args,
            report_path=report_path,
            host=exec_host,
            user=exec_user,
            timeout_seconds=timeout_seconds,
            remote_output_dir=remote_output_dir
        )

    async def _run_qemu_script(self, execution_id: str, action_id: str, script_path: str, args: List[str], report_path: str, timeout_seconds: int, remote_output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Ejecuta scripts usando qemu-agent (bypassing network/SSH)."""
        # Asegurar que el directorio de reporte existe desde el principio
        os.makedirs(report_path, exist_ok=True)
        
        try:
            vm_name = "kali-2025"
            remote_script_path = f"/tmp/{execution_id}.sh"
            
            # 1. Leer contenido del script local
            with open(script_path, "rb") as f:
                script_content = f.read()
                
            # 2. Escribir script en VM usando guest-file-write
            # Primero abrir archivo
            open_cmd = ["virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name, json.dumps({"execute": "guest-file-open", "arguments": {"path": remote_script_path, "mode": "w+"}})]
            proc = await asyncio.create_subprocess_exec(
                *open_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                raise Exception(f"Failed to open remote file via qemu-agent: {stderr.decode()}")
                
            try:
                file_handle = json.loads(stdout.decode())["return"]
            except Exception as e:
                logger.error(f"Failed to parse qemu-agent output: {stdout.decode()}")
                raise e
            
            # Escribir contenido (base64)
            content_b64 = base64.b64encode(script_content).decode()
            
            proc = await asyncio.create_subprocess_exec(
                "virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name,
                json.dumps({"execute": "guest-file-write", "arguments": {"handle": file_handle, "buf-b64": content_b64}}),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            # Cerrar archivo
            proc = await asyncio.create_subprocess_exec(
                "virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name,
                json.dumps({"execute": "guest-file-close", "arguments": {"handle": file_handle}}),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            # 3. Dar permisos +x
            proc = await asyncio.create_subprocess_exec(
                "virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name,
                json.dumps({"execute": "guest-exec", "arguments": {"path": "/usr/bin/chmod", "arg": ["+x", remote_script_path], "capture-output": True}}),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            
            # 4. Ejecutar script
            # Construir comando con argumentos
            # Si hay output dir, crearlo antes (hacky via bash -c)
            full_cmd = f"{remote_script_path} {' '.join(shlex.quote(a) for a in args)}"
            if remote_output_dir:
                full_cmd = f"mkdir -p {remote_output_dir} && {full_cmd}"
            
            # Ejecutar via bash para manejar redirecciones/env si fuera necesario
            exec_args = {"path": "/bin/bash", "arg": ["-c", full_cmd], "capture-output": True}
            
            logger.info(f"Executing via QEMU Agent: {full_cmd}")
            
            proc = await asyncio.create_subprocess_exec(
                "virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name,
                json.dumps({"execute": "guest-exec", "arguments": exec_args}),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                 raise Exception(f"Failed to execute command via qemu-agent: {stderr.decode()}")

            try:
                pid_data = json.loads(stdout.decode())
                pid = pid_data["return"]["pid"]
            except Exception as e:
                logger.error(f"Failed to parse PID from qemu-agent: {stdout.decode()}")
                raise e
            
            # 5. Polling de estado
            start_time = datetime.now()
            exit_code = -1
            stdout_decoded = ""
            stderr_decoded = ""
            
            while True:
                if (datetime.now() - start_time).total_seconds() > timeout_seconds:
                    # Timeout logic here (kill pid not implemented easily via agent without another exec)
                    stderr_decoded = "Execution timed out"
                    break
                    
                await asyncio.sleep(2)
                proc = await asyncio.create_subprocess_exec(
                    "virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name,
                    json.dumps({"execute": "guest-exec-status", "arguments": {"pid": pid}}),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                status_data = json.loads(stdout.decode())
                
                if status_data["return"]["exited"]:
                    exit_code = status_data["return"]["exitcode"]
                    if "out-data" in status_data["return"]:
                        stdout_decoded = base64.b64decode(status_data["return"]["out-data"]).decode(errors='replace')
                    if "err-data" in status_data["return"]:
                        stderr_decoded = base64.b64decode(status_data["return"]["err-data"]).decode(errors='replace')
                    break
            
            status = "completed" if exit_code == 0 else "failed"
            
            # 6. Recuperar artefactos (si existen)
            # Esto es complejo con qemu-agent (leer archivo por archivo). 
            # Por simplicidad, usaremos un truco: cat de los archivos clave y reconstruirlos localmente.
            # O mejor, intentar SCP inverso si SSH funcionara... pero no funciona.
            # Vamos a leer solo los archivos críticos conocidos: scan_results.txt, scan_raw.xml
            
            
            if remote_output_dir:
                artifacts_to_fetch = ["scan_results.txt", "scan_raw.xml"]
                for artifact in artifacts_to_fetch:
                    try:
                        remote_file = f"{remote_output_dir}/{artifact}"
                        proc = await asyncio.create_subprocess_exec(
                            "virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name,
                            json.dumps({"execute": "guest-file-open", "arguments": {"path": remote_file, "mode": "r"}}),
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        stdout, _ = await proc.communicate()
                        res = json.loads(stdout.decode())
                        if "return" in res:
                            handle = res["return"]
                            # Leer (asumiendo que cabe en buffer, si no habría que loop)
                            proc = await asyncio.create_subprocess_exec(
                                "virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name,
                                json.dumps({"execute": "guest-file-read", "arguments": {"handle": handle, "count": 10000000}}),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                            stdout, _ = await proc.communicate()
                            read_res = json.loads(stdout.decode())
                            content = base64.b64decode(read_res["return"]["buf-b64"])
                            
                            with open(f"{report_path}/{artifact}", "wb") as f:
                                f.write(content)
                                
                            # Cerrar
                            await asyncio.create_subprocess_exec(
                                "virsh", "-c", "qemu:///system", "qemu-agent-command", vm_name,
                                json.dumps({"execute": "guest-file-close", "arguments": {"handle": handle}}),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                    except Exception as e:
                        logger.warning(f"Could not fetch artifact {artifact}: {e}")

            metadata = {
                "execution_id": execution_id,
                "action_id": action_id,
                "target": args[0] if args else "",
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "exit_code": exit_code,
            }
            with open(f"{report_path}/metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            await self._generate_ai_report(
                report_path=report_path,
                execution_id=execution_id,
                action_id=action_id,
                target=metadata.get("target", ""),
                status=status,
                stdout=stdout_decoded,
                stderr=stderr_decoded
            )

            return {
                "execution_id": execution_id,
                "status": status,
                "exit_code": exit_code,
                "stdout": stdout_decoded,
                "stderr": stderr_decoded,
                "report_path": report_path,
                "report_id": os.path.basename(report_path)
            }

        except Exception as e:
            logger.error(f"Error executing QEMU script: {e}")
            
            # Generar metadata de error
            metadata = {
                "execution_id": execution_id,
                "action_id": action_id,
                "target": args[0] if args else "",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "exit_code": -1,
                "error": str(e)
            }
            try:
                with open(f"{report_path}/metadata.json", "w") as f:
                    json.dump(metadata, f, indent=2)
            except Exception as write_err:
                logger.error(f"Failed to write error metadata: {write_err}")

            return {
                "execution_id": execution_id,
                "status": "error",
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "report_path": report_path,
                "report_id": os.path.basename(report_path)
            }

    async def _ensure_vm_started(self, vm_name: str):
        """Asegura que la VM especificada esté corriendo."""
        try:
            # Verificar estado
            proc = await asyncio.create_subprocess_exec(
                "virsh", "-c", "qemu:///system", "domstate", vm_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            state = stdout.decode().strip()
            
            if "running" not in state:
                logger.info(f"VM {vm_name} is not running (State: {state}). Starting...")
                start_proc = await asyncio.create_subprocess_exec(
                    "virsh", "-c", "qemu:///system", "start", vm_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await start_proc.communicate()
                
                # Esperar a que arranque (simple wait por ahora)
                logger.info(f"Waiting for {vm_name} to boot...")
                await asyncio.sleep(10) # Espera conservadora
        except Exception as e:
            logger.error(f"Error managing VM {vm_name}: {e}")
            # No lanzamos excepción para intentar la conexión SSH de todos modos
            pass

    async def _generate_ai_report(self, report_path: str, execution_id: str, action_id: str, target: str, status: str, stdout: str, stderr: str):
        """Genera un reporte analizado por IA."""
        try:
            # 1. Intentar leer XML y parsearlo
            parsed_data = None
            xml_path = f"{report_path}/scan_raw.xml"
            
            if os.path.exists(xml_path):
                try:
                    with open(xml_path, "r") as f:
                        xml_content = f.read()
                    
                    # Call Orchestrator Parser
                    orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://orchestrator_api:8000")
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(f"{orchestrator_url}/parser/nmap", content=xml_content)
                        if resp.status_code == 200:
                            parsed_data = resp.json()
                            logger.info("Successfully parsed Nmap XML via Orchestrator")
                        else:
                            logger.warning(f"Failed to parse Nmap XML: {resp.status_code} - {resp.text}")
                except Exception as e:
                    logger.error(f"Error processing XML: {e}")

            # 2. Construir Prompt
            if parsed_data and "hosts" in parsed_data:
                # Usar datos estructurados
                hosts_summary = json.dumps(parsed_data["hosts"], indent=2)
                data_context = f"**Datos Estructurados del Escaneo (JSON):**\n```json\n{hosts_summary}\n```"
            else:
                # Fallback a stdout
                data_context = f"**Datos técnicos del escaneo (Raw Output):**\n```\n{stdout[:8000]}\n```"

            # Prompt para análisis de seguridad estilo ejecutivo
            prompt = f"""Actúa como un consultor senior de ciberseguridad especializado en informes para directivos no técnicos.

He realizado un servicio de "Network Discovery – Descubrimiento de hosts y puertos básicos" en la infraestructura del cliente.

{data_context}

Genera un INFORME EJECUTIVO en español, claro y profesional, siguiendo esta estructura:

# Network Discovery – Descubrimiento de Hosts y Puertos

**Cliente:** [Nombre del Cliente]  
**Fecha:** {datetime.now().strftime("%d/%m/%Y")}  
**Objetivo Analizado:** {target}  
**Realizado por:** Jarvis Security Platform

---

## 1. Resumen Ejecutivo

[Explica en 8-10 líneas qué se hizo, por qué es importante, hallazgos clave y recomendaciones principales. Usa lenguaje de negocio, NO jerga técnica]

**Hallazgos Clave:**
- [3-5 hallazgos principales en viñetas]

**Recomendaciones Principales:**
- [3-5 acciones prioritarias en viñetas]

---

## 2. Objetivo y Alcance

**Objetivo:** Identificar todos los dispositivos conectados a la red y los servicios que ofrecen, para evaluar posibles riesgos de seguridad.

**Alcance:** Se analizó el segmento de red {target}

**Fuera de alcance:** Pruebas de penetración, análisis de vulnerabilidades específicas, auditoría de configuraciones.

---

## 3. Metodología

Se utilizaron herramientas profesionales de análisis de red para:
- Identificar dispositivos conectados (como hacer un "censo" de la red)
- Detectar puertos abiertos (puertas de entrada digitales a servicios)
- Reconocer servicios activos (qué aplicaciones están ofreciendo cada dispositivo)

**Nota importante:** No se realizaron ataques ni intrusiones. El objetivo fue obtener una "radiografía" de lo que está visible en la red.

---

## 4. Resultados Globales

[Analiza los datos del escaneo y crea una tabla de dispositivos detectados]

### Tabla 1 – Resumen de dispositivos descubiertos

| ID | Dispositivo | IP | Puertos Abiertos | Nivel de Riesgo |
|----|-------------|-------|------------------|-----------------|
| [Genera filas basadas en los datos del escaneo] |

**Resumen:** [5-8 líneas explicando cuántos dispositivos se encontraron, si hay equipos sospechosos, etc.]

---

## 5. Exposición de Puertos y Servicios

**¿Qué es un puerto abierto?**  
Un puerto abierto es como una puerta de entrada digital por la que se ofrecen servicios (páginas web, correo, acceso remoto). Cuantos más puertos abiertos sin necesidad, mayor es la superficie de ataque para un atacante.

### Tabla 2 – Principales puertos y servicios detectados

| Dispositivo | IP | Puerto | Servicio | Comentario | Riesgo |
|-------------|-----|--------|----------|------------|--------|
| [Genera filas con los puertos más relevantes detectados] |

---

## 6. Riesgos Principales Identificados

### Riesgo 1 – [Nombre del Riesgo]
**Descripción:** [2-4 líneas en lenguaje de negocio]  
**Impacto potencial:** [Pérdida de datos, interrupción de servicio, multas regulatorias]  
**Ejemplo:** Un atacante podría...

### Riesgo 2 – [Nombre del Riesgo]
[Repetir estructura]

[Identifica 3-5 riesgos basados en los datos técnicos]

---

## 7. Recomendaciones Prioritarias

### Tabla 3 – Plan de acción recomendado

| Prioridad | Acción | Responsable | Plazo | Beneficio |
|-----------|--------|-------------|-------|-----------|
| Alta | [Acción específica basada en hallazgos] | IT / MSP | 30 días | [Beneficio de negocio] |
| [Genera filas con acciones priorizadas] |

**Nota:** Las acciones están ordenadas por urgencia y diseñadas para reducir riesgos sin frenar las operaciones del negocio.

---

## 8. Conclusiones

[Resume en 5-8 líneas:
- Nivel de exposición general
- Grado de control actual
- Beneficios de aplicar recomendaciones
- Posibles servicios futuros]

---

## Anexo Técnico

Información técnica completa disponible para el equipo de IT:
- Log detallado del escaneo
- Listado completo de puertos
- Datos técnicos sin procesar

---

**IMPORTANTE:**
- NO inventes datos. Usa SOLO la información del escaneo proporcionado.
- Si falta algún dato, indica "No disponible" o "Requiere análisis adicional".
- Mantén un tono profesional sin alarmismo.
- Conecta cada hallazgo con impacto de negocio (dinero, operaciones, reputación).
"""

            logger.info(f"Generating AI report for {execution_id}...")
            
            # Llamar a Ollama (en un executor para no bloquear el event loop)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.ollama_client.chat(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3.1:8b-instruct-q4_K_M"
                )
            )
            
            if "error" in response:
                raise Exception(f"Ollama error: {response['error']}")
            
            ai_report = response.get("message", {}).get("content", "")
            
            if not ai_report:
                raise Exception("Empty response from LLM")
            
            # Escribir reporte de IA
            with open(f"{report_path}/report_ai.md", "w") as f:
                f.write(ai_report)
                
            logger.info(f"AI report generated successfully for {execution_id}")

            # Ingest into Orchestrator
            try:
                orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://orchestrator_api:8000")
                ingest_data = {
                    "scan_id": execution_id,
                    "resumen_tecnico": ai_report,
                    "riesgos_principales": ["Ver reporte detallado"],
                    "recomendaciones": ["Ver reporte detallado"]
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.post(f"{orchestrator_url}/reports/ingest-data", json=ingest_data)
                    if resp.status_code == 200:
                        logger.info(f"Report ingested into Orchestrator: {resp.json()}")
                    else:
                        logger.error(f"Failed to ingest report: {resp.text}")
            except Exception as e:
                logger.error(f"Error ingesting report: {e}")
            
        except Exception as e:
            logger.error(f"Error generating AI report: {e}. Falling back to raw output.")
            # Fallback: escribir salida cruda
            with open(f"{report_path}/report_ai.md", "w") as f:
                f.write(f"# Execution Report: {execution_id}\n\n")
                f.write(f"**Target:** {target}\n")
                f.write(f"**Status:** {status}\n")
                f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
                f.write("**Nota:** No se pudo generar reporte con IA. Mostrando salida cruda.\n\n")
                f.write("## Standard Output\n")
                f.write("```bash\n")
                f.write(stdout)
                f.write("\n```\n\n")
                if stderr:
                    f.write("## Standard Error\n")
                    f.write("```bash\n")
                    f.write(stderr)
                    f.write("\n```\n")

    async def _run_local_script(self, execution_id: str, action_id: str, script_path: str, args: List[str], report_path: str, timeout_seconds: int, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Ejecuta scripts locales con argumentos personalizados."""
        os.chmod(script_path, 0o755)
        os.makedirs(report_path, exist_ok=True)

        cmd = [script_path] + args
        logger.info(f"Executing local script: {' '.join(cmd)}")

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
            timed_out = False
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            stdout, stderr = b"", f"Execution timed out after {timeout_seconds}s".encode()
            timed_out = True

        stdout_decoded = stdout.decode().strip()
        stderr_decoded = stderr.decode().strip()
        exit_code = -1 if timed_out else process.returncode
        status = "completed" if exit_code == 0 else ("timeout" if timed_out else "failed")

        if output_dir and os.path.isdir(output_dir):
            try:
                shutil.copytree(output_dir, report_path, dirs_exist_ok=True)
                logger.info(f"Copied artifacts from {output_dir} to {report_path}")
            except Exception as e:
                logger.error(f"Error copying local artifacts: {e}")

        metadata = {
            "execution_id": execution_id,
            "action_id": action_id,
            "target": args[0] if args else "",
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "exit_code": exit_code,
        }
        with open(f"{report_path}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        await self._generate_ai_report(
            report_path=report_path,
            execution_id=execution_id,
            action_id=action_id,
            target=metadata.get("target", ""),
            status=status,
            stdout=stdout_decoded,
            stderr=stderr_decoded
        )

        return {
            "execution_id": execution_id,
            "status": status,
            "exit_code": exit_code,
            "stdout": stdout_decoded,
            "stderr": stderr_decoded,
            "report_path": report_path,
            "report_id": os.path.basename(report_path)
        }

    async def _run_mock_script(self, execution_id: str, action_id: str, script_path: str, args: List[str], report_path: str) -> Dict[str, Any]:
        """Simula ejecución de scripts para desarrollo."""
        await asyncio.sleep(1)
        os.makedirs(report_path, exist_ok=True)

        sample_xml = """<nmaprun><host><status state="up"/><address addr="192.168.0.10" addrtype="ipv4"/><hostnames><hostname name="demo-host"/></hostnames><ports><port protocol="tcp" portid="22"><state state="open"/><service name="ssh"/></port></ports></host></nmaprun>"""
        with open(f"{report_path}/scan_raw.xml", "w") as f:
            f.write(sample_xml)
        with open(f"{report_path}/scan_results.txt", "w") as f:
            f.write("Mock nmap output for testing\n")

        metadata = {
            "execution_id": execution_id,
            "action_id": action_id,
            "target": args[0] if args else "",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "exit_code": 0,
            "mock": True
        }
        with open(f"{report_path}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        await self._generate_ai_report(
            report_path=report_path,
            execution_id=execution_id,
            action_id=action_id,
            target=metadata.get("target", ""),
            status="completed",
            stdout="[MOCK] Script executed.",
            stderr=""
        )

        return {
            "execution_id": execution_id,
            "status": "completed",
            "exit_code": 0,
            "stdout": "[MOCK] Executed script",
            "stderr": "",
            "report_path": report_path,
            "report_id": os.path.basename(report_path),
            "artifacts": ["scan_raw.xml", "scan_results.txt", "metadata.json", "report_ai.md"]
        }

    async def _run_ssh_script(self, execution_id: str, action_id: str, script_path: str, args: List[str], report_path: str, host: str, user: str, timeout_seconds: int, remote_output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Ejecuta scripts en nodo remoto y sincroniza artefactos."""
        try:
            remote_script_path = f"/tmp/{execution_id}.sh"
            use_sshpass = (host == "kali-2025" and user == "kali")

            if use_sshpass:
                scp_cmd = [
                    "sshpass", "-p", "leoslo23",
                    "scp",
                    "-o", "StrictHostKeyChecking=no",
                    script_path,
                    f"{user}@{host}:{remote_script_path}"
                ]
            else:
                scp_cmd = [
                    "scp",
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=no",
                    script_path,
                    f"{user}@{host}:{remote_script_path}"
                ]

                if self.key_path:
                    scp_cmd.insert(1, "-i")
                    scp_cmd.insert(2, self.key_path)

            logger.info(f"Copying script via SCP to {host}")

            scp_proc = await asyncio.create_subprocess_exec(
                *scp_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, scp_stderr = await scp_proc.communicate()

            if scp_proc.returncode != 0:
                raise Exception(f"Failed to copy script: {scp_stderr.decode()}")

            # Dar permisos de ejecución
            if use_sshpass:
                chmod_cmd = [
                    "sshpass", "-p", "leoslo23",
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    f"{user}@{host}",
                    f"chmod +x {remote_script_path}"
                ]
            else:
                chmod_cmd = [
                    "ssh",
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=no",
                    f"{user}@{host}",
                    f"chmod +x {remote_script_path}"
                ]

                if self.key_path:
                    chmod_cmd.insert(1, "-i")
                    chmod_cmd.insert(2, self.key_path)

            await asyncio.create_subprocess_exec(
                *chmod_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            quoted_args = " ".join(shlex.quote(arg) for arg in args)
            remote_cmd = f"{remote_script_path} {quoted_args}".strip()

            if remote_output_dir:
                remote_cmd = f"mkdir -p {shlex.quote(remote_output_dir)} && {remote_cmd}"

            if timeout_seconds:
                remote_cmd = f"timeout {timeout_seconds}s {remote_cmd}"

            if use_sshpass:
                cmd = [
                    "sshpass", "-p", "leoslo23",
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    f"{user}@{host}",
                    remote_cmd
                ]
            else:
                cmd = [
                    "ssh",
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=no",
                    f"{user}@{host}",
                    remote_cmd
                ]

                if self.key_path:
                    cmd.insert(1, "-i")
                    cmd.insert(2, self.key_path)

            logger.info(f"Executing SSH script: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds + 30)
                timed_out = False
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                stdout, stderr = b"", f"Execution timed out after {timeout_seconds}s".encode()
                timed_out = True

            stdout_decoded = stdout.decode().strip()
            stderr_decoded = stderr.decode().strip()
            exit_code = -1 if timed_out else process.returncode
            status = "completed" if exit_code == 0 else ("timeout" if timed_out else "failed")

            os.makedirs(report_path, exist_ok=True)

            if remote_output_dir:
                if use_sshpass:
                    fetch_cmd = [
                        "sshpass", "-p", "leoslo23",
                        "scp", "-r",
                        "-o", "StrictHostKeyChecking=no",
                        f"{user}@{host}:{remote_output_dir}/",
                        report_path
                    ]
                else:
                    fetch_cmd = [
                        "scp", "-r",
                        "-o", "BatchMode=yes",
                        "-o", "StrictHostKeyChecking=no",
                        f"{user}@{host}:{remote_output_dir}/",
                        report_path
                    ]

                    if self.key_path:
                        fetch_cmd.insert(1, "-i")
                        fetch_cmd.insert(2, self.key_path)

                fetch_proc = await asyncio.create_subprocess_exec(
                    *fetch_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, fetch_stderr = await fetch_proc.communicate()

                if fetch_proc.returncode != 0:
                    logger.error(f"Failed to fetch artifacts: {fetch_stderr.decode()}")
                else:
                    logger.info(f"Artifacts downloaded to {report_path}")

            metadata = {
                "execution_id": execution_id,
                "action_id": action_id,
                "target": args[0] if args else "",
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "exit_code": exit_code,
            }

            with open(f"{report_path}/metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            await self._generate_ai_report(
                report_path=report_path,
                execution_id=execution_id,
                action_id=action_id,
                target=metadata.get("target", ""),
                status=status,
                stdout=stdout_decoded,
                stderr=stderr_decoded
            )

            return {
                "execution_id": execution_id,
                "status": status,
                "exit_code": exit_code,
                "stdout": stdout_decoded,
                "stderr": stderr_decoded,
                "report_path": report_path,
                "report_id": os.path.basename(report_path)
            }

        except Exception as e:
            logger.error(f"Error executing SSH script: {e}")
            return {
                "execution_id": execution_id,
                "status": "error",
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "report_path": report_path,
                "report_id": os.path.basename(report_path)
            }

    async def _run_local(self, execution_id: str, action_id: str, script_path: str, target: str, report_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Ejecuta el script localmente usando subprocess."""
        try:
            # Asegurar permisos de ejecución
            os.chmod(script_path, 0o755)
            
            # Crear directorio de reporte
            os.makedirs(report_path, exist_ok=True)
            
            # Ejecutar comando
            process = await asyncio.create_subprocess_exec(
                script_path, target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            stdout_decoded = stdout.decode().strip()
            stderr_decoded = stderr.decode().strip()
            
            status = "completed" if process.returncode == 0 else "failed"
            
            # Copy artifacts if output_dir is specified
            if output_dir and os.path.isdir(output_dir):
                try:
                    for item in os.listdir(output_dir):
                        s = os.path.join(output_dir, item)
                        d = os.path.join(report_path, item)
                        if os.path.isfile(s):
                            shutil.copy2(s, d)
                    logger.info(f"Copied artifacts from {output_dir} to {report_path}")
                except Exception as e:
                    logger.error(f"Error copying local artifacts: {e}")
            
            # Generar metadata.json
            import json
            metadata = {
                "execution_id": execution_id,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "exit_code": process.returncode,
                "action_name": action_id
            }
            with open(f"{report_path}/metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
                
            # Generar report_ai.md con análisis de IA
            await self._generate_ai_report(
                report_path=report_path,
                execution_id=execution_id,
                action_id=action_id,
                target=target,
                status=status,
                stdout=stdout_decoded,
                stderr=stderr_decoded
            )
            
            return {
                "execution_id": execution_id,
                "status": status,
                "exit_code": process.returncode,
                "stdout": stdout_decoded,
                "stderr": stderr_decoded,
                "report_path": report_path
            }
        except Exception as e:
            logger.error(f"Error executing local script: {e}")
            return {
                "execution_id": execution_id,
                "status": "error",
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "report_path": report_path
            }

    async def _run_mock(self, execution_id: str, action_id: str, script_path: str, target: str, report_path: str) -> Dict[str, Any]:
        """Simula ejecución para desarrollo/demo."""
        await asyncio.sleep(2)  # Simular tiempo de ejecución
        
        # Simular generación de reporte
        os.makedirs(report_path, exist_ok=True)
        with open(f"{report_path}/summary.md", "w") as f:
            f.write(f"# Reporte de Acción: {action_id}\n\n")
            f.write(f"**Target:** {target}\n")
            f.write(f"**Status:** Success\n")
            f.write(f"**Execution ID:** {execution_id}\n")
            f.write("\n## Resultados Simulados\n")
            f.write("Esta es una ejecución simulada en el entorno de desarrollo.\n")
        
        return {
            "execution_id": execution_id,
            "status": "completed",
            "exit_code": 0,
            "stdout": f"[MOCK] Executing {script_path} on {target}...\n[MOCK] Done.",
            "stderr": "",
            "report_path": report_path,
            "artifacts": ["summary.md"]
        }

    async def _run_ssh(self, execution_id: str, action_id: str, script_path: str, target: str, report_path: str, host: str = None, user: str = None, remote_output_dir: str = None) -> Dict[str, Any]:
        """Ejecuta vía SSH en Kali-2025 o nodo personalizado."""
        try:
            # Construir comando SSH
            # ssh -o BatchMode=yes user@host "script 'target'"
            
            current_host = host if host else self.host
            current_user = user if user else self.user
            
            # Si target es vacío, usar 'auto'
            target_arg = target if target else "auto"
            
            
            # Copiar script al remoto
            remote_script_path = f"/tmp/{execution_id}.sh"
            
            # Use sshpass for kali-2025 due to SSH key issues
            use_sshpass = (current_host == "kali-2025" and current_user == "kali")
            
            if use_sshpass:
                scp_cmd = [
                    "sshpass", "-p", "leoslo23",
                    "scp",
                    "-o", "StrictHostKeyChecking=no",
                    script_path,
                    f"{current_user}@{current_host}:{remote_script_path}"
                ]
            else:
                scp_cmd = [
                    "scp",
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=no",
                    script_path,
                    f"{current_user}@{current_host}:{remote_script_path}"
                ]
                
                if self.key_path:
                    scp_cmd.insert(1, "-i")
                    scp_cmd.insert(2, self.key_path)
                
            logger.info(f"Copying script via SCP to {current_host}")
            
            scp_proc = await asyncio.create_subprocess_exec(
                *scp_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, scp_stderr = await scp_proc.communicate()
            
            if scp_proc.returncode != 0:
                raise Exception(f"Failed to copy script: {scp_stderr.decode()}")


            # Dar permisos de ejecución
            if use_sshpass:
                chmod_cmd = [
                    "sshpass", "-p", "leoslo23",
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    f"{current_user}@{current_host}",
                    f"chmod +x {remote_script_path}"
                ]
            else:
                chmod_cmd = [
                    "ssh",
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=no",
                    f"{current_user}@{current_host}",
                    f"chmod +x {remote_script_path}"
                ]
                
                if self.key_path:
                    chmod_cmd.insert(1, "-i")
                    chmod_cmd.insert(2, self.key_path)
                
            chmod_proc = await asyncio.create_subprocess_exec(
                *chmod_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await chmod_proc.communicate()

            # Ejecutar script remoto
            if use_sshpass:
                cmd = [
                    "sshpass", "-p", "leoslo23",
                    "ssh",
                    "-o", "StrictHostKeyChecking=no",
                    f"{current_user}@{current_host}",
                    f"{remote_script_path} '{target_arg}'"
                ]
            else:
                cmd = [
                    "ssh",
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=no", # Para evitar prompts en primera conexión
                    f"{current_user}@{current_host}",
                    f"{remote_script_path} '{target_arg}'"
                ]
                
                if self.key_path:
                    cmd.insert(1, "-i")
                    cmd.insert(2, self.key_path)
                
            logger.info(f"Executing SSH: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
        
            stdout_decoded = stdout.decode().strip()
            stderr_decoded = stderr.decode().strip()
            
            status = "completed" if process.returncode == 0 else "failed"
            
            # Crear directorio de reporte
            os.makedirs(report_path, exist_ok=True)
            
            # Generar metadata.json
            import json
            metadata = {
                "execution_id": execution_id,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "exit_code": process.returncode,
                "action_name": action_id
            }
            with open(f"{report_path}/metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
                
            # Generar report_ai.md con análisis de IA
            await self._generate_ai_report(
                report_path=report_path,
                execution_id=execution_id,
                action_id=action_id,
                target=target,
                status=status,
                stdout=stdout_decoded,
                stderr=stderr_decoded
            )
            
            return {
                "execution_id": execution_id,
                "status": status,
                "exit_code": process.returncode,
                "stdout": stdout_decoded,
                "stderr": stderr_decoded,
                "report_path": report_path
            }
            
        except Exception as e:
            logger.error(f"Error executing SSH: {e}")
            return {
                "execution_id": execution_id,
                "status": "error",
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "report_path": report_path
            }

# Singleton instance
kali_runner = KaliRunner()
