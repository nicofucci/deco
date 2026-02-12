from datetime import datetime, timezone
import json
import logging
import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from app.models.domain import (
    Client,
    NetworkAsset,
    NetworkVulnerability,
    AutofixPlaybook,
    AutofixExecution,
    ScanJob
)

logger = logging.getLogger("DecoOrchestrator.AutofixEngine")

class FixAction:
    def __init__(self, id: str, title: str, description: str, 
                 os_family: str, commands: List[str], risk: str, 
                 reboot: bool = False, manual_steps: List[str] = None):
        self.id = id
        self.title = title
        self.description = description
        self.os_family = os_family # windows, linux, generic
        self.commands = commands or []
        self.risk_level = risk # low, medium, high
        self.requires_reboot = reboot
        self.manual_steps = manual_steps or []
        
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "os_family": self.os_family,
            "commands": self.commands,
            "risk_level": self.risk_level,
            "requires_reboot": self.requires_reboot,
            "manual_steps": self.manual_steps
        }

class AutofixEngine:
    def __init__(self, db: Session):
        self.db = db
        
    def generate_playbooks_for_client(self, client_id: str) -> List[AutofixPlaybook]:
        """
        Scans client critical/high vulnerabilities and generates Draft Playbooks.
        """
        logger.info(f"Generating playbooks for client {client_id}")
        
        # 1. Fetch Vulns
        vulns = self.db.query(NetworkVulnerability).join(NetworkAsset).filter(
            NetworkVulnerability.client_id == client_id,
            NetworkVulnerability.severity.in_(["critical", "high"])
        ).all()
        
        generated = []
        
        for vuln in vulns:
            # Check if playbook already exists for this vuln
            exists = self.db.query(AutofixPlaybook).filter(
                AutofixPlaybook.vulnerability_id == vuln.id
            ).first()
            if exists:
                continue
                
            # 2. Rule Engine
            playbook_data = self._create_rule_based_playbook(vuln, vuln.asset)
            if not playbook_data:
                continue
                
            # 3. Create Draft
            new_pb = AutofixPlaybook(
                client_id=client_id,
                asset_id=vuln.asset_id,
                vulnerability_id=vuln.id,
                title=f"Fix for {vuln.cve}: {playbook_data['title_suffix']}",
                playbook_json=playbook_data["json"],
                risk_level=playbook_data["risk"],
                status="draft"
            )
            self.db.add(new_pb)
            generated.append(new_pb)
            
        self.db.commit()
        logger.info(f"Generated {len(generated)} new playbooks for client {client_id}")
        return generated

    def _create_rule_based_playbook(self, vuln: NetworkVulnerability, asset: NetworkAsset) -> Optional[Dict]:
        """
        Heuristic Rules v1.
        Returns dict with keys: title_suffix, json, risk OR None if no fix known.
        """
        os_guess = str(asset.os_guess).lower()
        
        # RULE 1: SMBv1 (WannaCry-like) on Windows
        # CVE-2017-0144 (EternalBlue) or generic "SMB" in title
        if "windows" in os_guess and ("CVE-2017-0144" in vuln.cve or "smb" in vuln.description_short.lower()):
            action = FixAction(
                id="disable_smbv1",
                title="Disable SMBv1 Protocol",
                description="Disables the legacy SMBv1 protocol to prevent EternalBlue exploits.",
                os_family="windows",
                commands=[
                    "Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force",
                    "sc.exe config lanmanworkstation depend= bowser/mrxsmb10/nsi",
                    "sc.exe config mrxsmb10 start= disabled"
                ],
                risk="medium",
                reboot=True
            )
            return {
                "title_suffix": "Disable SMBv1 (Windows PowerShell)",
                "json": {"actions": [action.to_dict()]},
                "risk": "medium"
            }
            
        # RULE 2: Open RDP/SSH on Public IP (Generic)
        # Assuming we check if it is exposed. For v1, let's just create a manual recommendation if high severity.
        # This is a fallback manual playbook.
        if vuln.severity in ["critical", "high"]:
            action = FixAction(
                id="manual_patch_critical",
                title="Manual Patching Required",
                description=f"Critical vulnerability {vuln.cve} requires manual intervention or vendor patch.",
                os_family="generic",
                commands=[],
                risk="low",
                manual_steps=[
                    "Identify the vendor update for this software.",
                    "Download and install the patch.",
                    "Verify headers/version after update."
                ]
            )
            return {
                "title_suffix": "Manual Intervention Required",
                "json": {"actions": [action.to_dict()]},
                "risk": "low"
            }
            
        return None

    def approve_playbook(self, playbook_id: str):
        pb = self.db.query(AutofixPlaybook).filter(AutofixPlaybook.id == playbook_id).first()
        if pb and pb.status == "draft":
            pb.status = "approved"
            self.db.commit()
            return True
        return False
        
    def execute_playbook(self, playbook_id: str, agent_id: str = None) -> AutofixExecution:
        pb = self.db.query(AutofixPlaybook).filter(AutofixPlaybook.id == playbook_id).first()
        if not pb:
            raise ValueError("Playbook not found")
            
        if pb.status != "approved":
            raise ValueError("Playbook must be APPROVED before execution")
            
        # Find Agent if not provided
        target_agent_id = agent_id or pb.asset.agent_id
        if not target_agent_id:
             # Find generic agent for client?
             # For Autofix it MUST be the agent that can see the asset.
             # If asset.agent_id is null, we can't safely execute commands on the asset unless it's a remote scan fix.
             # Since our commands (PowerShell) run ON the asset, we assume the agent IS on the asset (Endpoint Agent)
             # OR the agent can reach it.
             # V1 assumption: Endpoint Agent installed -> asset.agent_id is set.
             raise ValueError("No Agent associated with this asset/playbook.")

        # Create Execution Record
        execution = AutofixExecution(
            playbook_id=pb.id,
            agent_id=target_agent_id,
            execution_mode="semi_auto",
            status="pending"
        )
        self.db.add(execution)
        self.db.commit()
        
        # Create Job for Agent
        # The params passed to the agent will be the playbook JSON Actions
        job = ScanJob(
            client_id=pb.client_id,
            agent_id=target_agent_id,
            type="autofix_playbook_execute",
            target=pb.asset.ip, # Or hostname? IP is safer.
            status="pending",
            params={
                "execution_id": execution.id,
                "playbook": pb.playbook_json
            },
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(job)
        self.db.commit()
        
        return execution
