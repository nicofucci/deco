"""
Standard Workflows Definitions
Defines the core workflows for Jarvis 3.0
"""

from typing import Dict, Any, List
from .base import BaseWorkflow, register_workflow
from app.agents.dispatcher import dispatcher, DispatchResult
from app.agents.protocol import ResponseStatus

class NetworkAuditWorkflow(BaseWorkflow):
    name = "network_audit"
    description = "Complete network audit: Scan -> Vuln Analysis -> Report"
    agents_involved = ["A-SCAN", "A-VULN", "A-REPORT"]
    
    async def execute(self, dispatcher, params: Dict[str, Any]) -> DispatchResult:
        target = params.get("target")
        if not target:
            raise ValueError("Target required for network audit")
            
        results = []
        
        # 1. Scan
        scan_resp = await dispatcher.dispatch_to_agent(
            "A-SCAN", 
            "scan_target", 
            {"target": target, "profile": params.get("profile", "standard")}
        )
        results.append(scan_resp)
        
        if scan_resp.status != ResponseStatus.SUCCESS:
            return DispatchResult(
                workflow_id=self.name,
                success=False,
                responses=results,
                summary=f"Audit failed at scan stage: {scan_resp.summary}"
            )
            
        # 2. Vuln Analysis
        vuln_resp = await dispatcher.dispatch_to_agent(
            "A-VULN",
            "analyze_scan",
            {"scan_results": scan_resp.details}
        )
        results.append(vuln_resp)
        
        # 3. Report
        report_resp = await dispatcher.dispatch_to_agent(
            "A-REPORT",
            "generate_report",
            {
                "type": "audit",
                "data": {
                    "scan": scan_resp.details,
                    "vulns": vuln_resp.details
                },
                "title": f"Network Audit Report: {target}"
            }
        )
        results.append(report_resp)
        
        return DispatchResult(
            workflow_id=self.name,
            success=True,
            responses=results,
            summary=f"Network audit completed for {target}. Found {len(vuln_resp.details.get('vulnerabilities', []))} vulnerabilities.",
            artifacts=report_resp.artifacts
        )

class PentestWorkflow(BaseWorkflow):
    name = "pentest_attack"
    description = "Authorized Pentest: Scan -> Exploit -> Report"
    agents_involved = ["A-SCAN", "A-PENTEST", "A-REPORT"]
    
    async def execute(self, dispatcher, params: Dict[str, Any]) -> DispatchResult:
        target = params.get("target")
        
        # 1. Scan
        scan_resp = await dispatcher.dispatch_to_agent("A-SCAN", "quick_scan", {"target": target})
        
        # 2. Exploit (Simulated)
        exploit_resp = await dispatcher.dispatch_to_agent(
            "A-PENTEST", 
            "exploit_target", 
            {
                "target": target, 
                "exploit_module": "exploit/multi/http/tomcat_mgr_upload",
                "force_auth_dev": True # For demo purposes
            }
        )
        
        # 3. Report
        report_resp = await dispatcher.dispatch_to_agent(
            "A-REPORT",
            "generate_report",
            {
                "type": "pentest",
                "data": {"exploit_result": exploit_resp.details},
                "title": f"Pentest Report: {target}"
            }
        )
        
        return DispatchResult(
            workflow_id=self.name,
            success=exploit_resp.status == ResponseStatus.SUCCESS,
            responses=[scan_resp, exploit_resp, report_resp],
            summary=f"Pentest execution finished. Exploit status: {exploit_resp.status}",
            artifacts=report_resp.artifacts
        )

class RemediationWorkflow(BaseWorkflow):
    name = "remediation_plan"
    description = "Generate remediation plan from vulnerabilities"
    agents_involved = ["A-VULN", "A-DEFENSE", "A-REPORT"]
    
    async def execute(self, dispatcher, params: Dict[str, Any]) -> DispatchResult:
        # 1. Get Vulns (Mock or from params)
        vulns = params.get("vulnerabilities", [{"id": "CVE-2023-1234", "severity": "HIGH"}])
        
        # 2. Create Plan
        plan_resp = await dispatcher.dispatch_to_agent(
            "A-DEFENSE",
            "create_remediation_plan",
            {"vulnerabilities": vulns}
        )
        
        # 3. Report
        report_resp = await dispatcher.dispatch_to_agent(
            "A-REPORT",
            "generate_report",
            {
                "type": "remediation",
                "data": plan_resp.details,
                "title": "Remediation Plan"
            }
        )
        
        return DispatchResult(
            workflow_id=self.name,
            success=True,
            responses=[plan_resp, report_resp],
            summary="Remediation plan generated successfully",
            artifacts=report_resp.artifacts
        )

# Register all
register_workflow(NetworkAuditWorkflow())
register_workflow(PentestWorkflow())
register_workflow(RemediationWorkflow())
