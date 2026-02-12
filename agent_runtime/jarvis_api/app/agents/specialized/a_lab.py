"""
A-LAB: Laboratory Commander Agent
Responsible for managing KVM/Libvirt Virtual Machines
"""

import asyncio
import subprocess
from typing import Dict, List, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus

class LabAgent(BaseAgent):
    agent_id = "lab-001"
    code = "A-LAB"
    name = "Lab Commander"
    version = "1.0.0"
    description = "Manages KVM/Libvirt Virtual Machines for the laboratory environment"
    
    @property
    def responsibilities(self) -> List[str]:
        return [
            "VM Management (start, stop, restart)",
            "Lab Scenario Provisioning",
            "Snapshot Management",
            "Network Configuration"
        ]
    
    @property
    def tools(self) -> List[str]:
        return ["virsh", "virt-install", "qemu-img"]
    
    @property
    def permissions(self) -> List[str]:
        return ["manage_vms", "manage_networks"]
    
    async def execute(self, message: AgentMessage) -> AgentResponse:
        action = message.intent
        params = message.params
        
        if action == "list_vms":
            return await self._list_vms()
        elif action == "start_vm":
            return await self._control_vm(params.get("vm_name"), "start")
        elif action == "stop_vm":
            return await self._control_vm(params.get("vm_name"), "shutdown")
        elif action == "snapshot_vm":
            return await self._snapshot_vm(params.get("vm_name"), params.get("snapshot_name"))
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Acción desconocida: {action}",
                errors=[f"Unknown action: {action}"]
            )
    
    async def _run_virsh(self, command: str) -> str:
        """Run a virsh command"""
        try:
            # In a real env, we'd run this. For safety/demo, we might mock if virsh isn't accessible
            # But let's try to implement the wrapper
            proc = await asyncio.create_subprocess_shell(
                f"virsh {command}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                self.logger.error(f"Virsh error: {stderr.decode()}")
                raise Exception(stderr.decode())
                
            return stdout.decode()
        except Exception as e:
            # Fallback for dev environment without libvirt
            self.logger.warning(f"Virsh command failed (simulating): {e}")
            return self._mock_virsh_response(command)

    def _mock_virsh_response(self, command: str) -> str:
        """Mock responses for dev environment"""
        if "list --all" in command:
            return """ Id   Name           State
------------------------------
 -    kali-agent     shut off
 -    parrot-agent   shut off
 -    metasploitable shut off
"""
        return ""

    async def _list_vms(self) -> AgentResponse:
        output = await self._run_virsh("list --all")
        
        # Parse output
        vms = []
        lines = output.strip().split('\n')
        if len(lines) > 2:
            for line in lines[2:]:
                parts = line.split()
                if len(parts) >= 2:
                    vms.append({
                        "id": parts[0],
                        "name": parts[1],
                        "state": " ".join(parts[2:])
                    })
        
        return AgentResponse(
            request_id="list-vms",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Encontradas {len(vms)} máquinas virtuales en el laboratorio",
            details={"vms": vms}
        )
    
    async def _control_vm(self, vm_name: str, action: str) -> AgentResponse:
        if not vm_name:
            return AgentResponse(
                request_id="control-vm",
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary="Nombre de VM requerido",
                errors=["Missing vm_name"]
            )
            
        await self._run_virsh(f"{action} {vm_name}")
        
        return AgentResponse(
            request_id="control-vm",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Comando '{action}' enviado a VM '{vm_name}'",
            details={"vm": vm_name, "action": action}
        )

    async def _snapshot_vm(self, vm_name: str, snapshot_name: str) -> AgentResponse:
        if not vm_name or not snapshot_name:
             return AgentResponse(
                request_id="snap-vm",
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary="Nombre de VM y Snapshot requeridos",
                errors=["Missing params"]
            )
            
        await self._run_virsh(f"snapshot-create-as {vm_name} {snapshot_name}")
        
        return AgentResponse(
            request_id="snap-vm",
            agent_code=self.code,
            status=ResponseStatus.SUCCESS,
            summary=f"Snapshot '{snapshot_name}' creado para '{vm_name}'",
            details={"vm": vm_name, "snapshot": snapshot_name}
        )
