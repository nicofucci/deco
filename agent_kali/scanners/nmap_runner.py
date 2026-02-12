import subprocess
import os
import shutil
from typing import Dict, Any, Optional
from parsers.nmap_xml_parser import NmapXMLParser

class NmapRunner:
    def __init__(self, output_dir: str = "/tmp/deco_scans"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.parser = NmapXMLParser()

    def run_scan(self, target: str, scan_type: str = "discovery") -> Dict[str, Any]:
        """
        Ejecuta Nmap contra el target y devuelve el resultado parseado.
        """
        output_file = os.path.join(self.output_dir, f"scan_{target.replace('/', '_')}.xml")
        
        # Construir comando según tipo
        # Nota: En un entorno real, validar input para evitar inyección de comandos.
        # Aquí asumimos que 'target' viene validado del Orchestrator.
        
        cmd = ["nmap", "-oX", output_file]
        
        if scan_type == "discovery":
            # Escaneo rápido de top ports
            cmd.extend(["-F", "-T4", target])
        elif scan_type == "full":
            # Escaneo completo con versiones y OS
            cmd.extend(["-sV", "-O", "-T4", target])
        else:
            # Default
            cmd.extend(["-F", target])

        print(f"Executing: {' '.join(cmd)}")
        
        try:
            # Check if nmap is installed
            if not shutil.which("nmap"):
                return {"error": "Nmap binary not found"}

            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Leer y parsear
            with open(output_file, "r") as f:
                xml_content = f.read()
                
            return self.parser.parse(xml_content)

        except subprocess.CalledProcessError as e:
            print(f"Nmap execution failed: {e}")
            return {"error": f"Nmap execution failed: {e.stderr}"}
        except Exception as e:
            print(f"Error running scan: {e}")
            return {"error": str(e)}
