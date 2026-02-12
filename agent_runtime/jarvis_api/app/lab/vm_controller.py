"""
VM Lab Controller para Jarvis 3.0
Control de VMs del laboratorio desde API
"""

import subprocess
from typing import List, Dict, Optional
import json

class LabVMController:
    """Controlador de VMs del laboratorio distribuido."""
    
    # Mapa de VMs del laboratorio
    VMS = {
        "kali": "Kali-2025",
        "parrot": "ParrotOS",
        "winserver": "WinServer2019",
        "win10": "Win10Vuln",
        "ubuntu": "UbuntuLegacy"
    }
    
    def __init__(self):
        self.vbox_manage = "VBoxManage"
    
    def list_vms(self) -> List[Dict]:
        """Lista todas las VMs con su estado."""
        result = subprocess.run(
            [self.vbox_manage, 'list', 'vms'],
            capture_output=True,
            text=True
        )
        
        vms = []
        for vm_id, vm_name in self.VMS.items():
            status = self.get_vm_status(vm_id)
            vms.append({
                "id": vm_id,
                "name": vm_name,
                "status": status
            })
        
        return vms
    
    def start_vm(self, vm_id: str, headless: bool = True) -> Dict:
        """
        Inicia una VM.
        
        Args:
            vm_id: ID de la VM (kali, parrot, etc.)
            headless: Si True, inicia sin GUI
        """
        vm_name = self.VMS.get(vm_id)
        if not vm_name:
            return {"error": f"VM desconocida: {vm_id}"}
        
        # Verificar si ya está corriendo
        status = self.get_vm_status(vm_id)
        if status == "running":
            return {"status": "already_running", "vm": vm_id}
        
        try:
            cmd = [self.vbox_manage, 'startvm', vm_name]
            if headless:
                cmd.extend(['--type', 'headless'])
            
            subprocess.run(cmd, check=True)
            
            return {
                "status": "started",
                "vm": vm_id,
                "name": vm_name,
                "headless": headless
            }
        except subprocess.CalledProcessError as e:
            return {"error": str(e)}
    
    def stop_vm(self, vm_id: str, force: bool = False) -> Dict:
        """
        Detiene una VM.
        
        Args:
            vm_id: ID de la VM
            force: Si True, usa poweroff en lugar de acpi shutdown
        """
        vm_name = self.VMS.get(vm_id)
        if not vm_name:
            return {"error": f"VM desconocida: {vm_id}"}
        
        try:
            action = 'poweroff' if force else 'acpipowerbutton'
            subprocess.run(
                [self.vbox_manage, 'controlvm', vm_name, action],
                check=True
            )
            
            return {
                "status": "stopped",
                "vm": vm_id,
                "method": action
            }
        except subprocess.CalledProcessError as e:
            return {"error": str(e)}
    
    def snapshot_vm(self, vm_id: str, snapshot_name: str, description: str = "") -> Dict:
        """Crea snapshot de una VM."""
        vm_name = self.VMS.get(vm_id)
        if not vm_name:
            return {"error": f"VM desconocida: {vm_id}"}
        
        try:
            cmd = [
                self.vbox_manage, 'snapshot', vm_name,
                'take', snapshot_name
            ]
            if description:
                cmd.extend(['--description', description])
            
            subprocess.run(cmd, check=True)
            
            return {
                "status": "snapshot_created",
                "vm": vm_id,
                "snapshot": snapshot_name
            }
        except subprocess.CalledProcessError as e:
            return {"error": str(e)}
    
    def restore_vm(self, vm_id: str, snapshot_name: str) -> Dict:
        """Restaura una VM a un snapshot."""
        vm_name = self.VMS.get(vm_id)
        if not vm_name:
            return {"error": f"VM desconocida: {vm_id}"}
        
        try:
            # Detener VM si está corriendo
            status = self.get_vm_status(vm_id)
            if status == "running":
                self.stop_vm(vm_id, force=True)
            
            # Restaurar snapshot
            subprocess.run(
                [self.vbox_manage, 'snapshot', vm_name, 'restore', snapshot_name],
                check=True
            )
            
            return {
                "status": "restored",
                "vm": vm_id,
                "snapshot": snapshot_name
            }
        except subprocess.CalledProcessError as e:
            return {"error": str(e)}
    
    def list_snapshots(self, vm_id: str) -> List[str]:
        """Lista snapshots de una VM."""
        vm_name = self.VMS.get(vm_id)
        if not vm_name:
            return []
        
        try:
            result = subprocess.run(
                [self.vbox_manage, 'snapshot', vm_name, 'list'],
                capture_output=True,
                text=True
            )
            
            # Parse output para extraer nombres de snapshots
            snapshots = []
            for line in result.stdout.split('\n'):
                if line.strip().startswith('Name:'):
                    name = line.split(':', 1)[1].strip()
                    snapshots.append(name)
            
            return snapshots
        except:
            return []
    
    def get_vm_status(self, vm_id: str) -> str:
        """
        Obtiene estado actual de una VM.
        
        Returns:
            Estado: running, poweroff, saved, etc.
        """
        vm_name = self.VMS.get(vm_id)
        if not vm_name:
            return "unknown"
        
        try:
            result = subprocess.run(
                [self.vbox_manage, 'showvminfo', vm_name, '--machinereadable'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if line.startswith('VMState='):
                    return line.split('=')[1].strip('"')
            
            return "unknown"
        except:
            return "error"
    
    def get_vm_info(self, vm_id: str) -> Optional[Dict]:
        """Obtiene información detallada de una VM."""
        vm_name = self.VMS.get(vm_id)
        if not vm_name:
            return None
        
        try:
            result = subprocess.run(
                [self.vbox_manage, 'showvminfo', vm_name, '--machinereadable'],
                capture_output=True,
                text=True
            )
            
            info = {}
            for line in result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    info[key] = value.strip('"')
            
            return {
                "id": vm_id,
                "name": vm_name,
                "state": info.get("VMState", "unknown"),
                "memory": info.get("memory", "0"),
                "cpus": info.get("cpus", "0"),
                "description": info.get("description", "")
            }
        except:
            return None
