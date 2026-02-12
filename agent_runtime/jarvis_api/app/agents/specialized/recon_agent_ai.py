"""
Intelligent Reconnaissance Agent
Autonomous network discovery with adaptive decision-making.
"""

import logging
from typing import Dict, Any
from app.agents.base_agent import BaseAgent, Tool
from app.services.kali_runner import kali_runner

logger = logging.getLogger(__name__)


class ReconAgentAI(BaseAgent):
    """
    Autonomous Reconnaissance Agent with LLM-powered decision making.
    
    Capabilities:
    - Adaptive network scanning
    - Service fingerprinting
    - Technology stack detection
    - Asset inventory compilation
    """
    
    def __init__(self, agent_id: str = "recon-ai-001"):
        super().__init__(agent_id)
        self.discovered_hosts = []
        self.discovered_services = []
    
    def get_system_prompt(self) -> str:
        return """You are an expert reconnaissance specialist for cybersecurity operations.

Your role is to:
- Systematically discover network assets
- Identify running services and their versions
- Detect technologies and platforms
- Build comprehensive asset inventories
- Adapt your scanning strategy based on findings

You have access to various scanning tools. Choose the right tool for each situation:
- **nmap_quick**: Fast port scan (top 100 ports)
- **nmap_detailed**: Comprehensive scan with service detection
- **dns_enum**: DNS enumeration and subdomain discovery

Be thorough but efficient. Start with broad discovery, then drill down into interesting findings.
Prioritize stealth and avoid disrupting target systems.

Always provide clear reasoning for your decisions."""
    
    def _register_tools(self):
        """Register reconnaissance tools."""
        
        # Tool 1: Quick Nmap Scan
        async def nmap_quick(target: str) -> Dict[str, Any]:
            """Quick port scan of top 100 ports."""
            result = await kali_runner.run_action(
                action_id="nmap_quick",
                script_path="/opt/deco/agent_runtime/scripts/actions/01_network_scan.sh",
                target=target,
                params={"scan_type": "quick"}
            )
            return {
                "target": target,
                "scan_type": "quick",
                "output": result.get("stdout", ""),
                "status": result.get("status", "unknown")
            }
        
        self.register_tool(Tool(
            name="nmap_quick",
            description="Fast port scan of top 100 ports. Use for initial discovery.",
            function=nmap_quick,
            parameters={"target": "IP address or hostname"}
        ))
        
        # Tool 2: Detailed Nmap Scan
        async def nmap_detailed(target: str) -> Dict[str, Any]:
            """Comprehensive scan with service version detection."""
            result = await kali_runner.run_action(
                action_id="nmap_detailed",
                script_path="/opt/deco/agent_runtime/scripts/actions/01_network_scan.sh",
                target=target,
                params={"scan_type": "detailed"}
            )
            return {
                "target": target,
                "scan_type": "detailed",
                "output": result.get("stdout", ""),
                "status": result.get("status", "unknown")
            }
        
        self.register_tool(Tool(
            name="nmap_detailed",
            description="Comprehensive port and service version scan. Use when you need detailed information.",
            function=nmap_detailed,
            parameters={"target": "IP address or hostname"}
        ))
        
        # Tool 3: DNS Enumeration (mock for now)
        async def dns_enum(domain: str) -> Dict[str, Any]:
            """DNS enumeration and subdomain discovery."""
            # This would call actual DNS tools - mocked for now
            return {
                "domain": domain,
                "subdomains_found": ["www", "mail", "ftp"],
                "records": {
                    "A": ["192.168.1.1"],
                    "MX": ["mail.example.com"]
                }
            }
        
        self.register_tool(Tool(
            name="dns_enum",
            description="Enumerate DNS records and discover subdomains. Use for domain reconnaissance.",
            function=dns_enum,
            parameters={"domain": "Domain name"}
        ))
    
    async def run_reconnaissance(self, target: str, scan_type: str = "adaptive") -> Dict[str, Any]:
        """
        Execute reconnaissance mission with autonomous decision-making.
        
        Args:
            target: IP, hostname, or network range
            scan_type: "adaptive" (default), "quick", or "comprehensive"
        
        Returns:
            Complete reconnaissance results
        """
        objective = f"Perform {scan_type} reconnaissance on {target}. Discover all accessible services and build an asset inventory."
        
        context = {
            "target": target,
            "scan_type": scan_type,
            "constraints": {
                "stealth": True,
                "max_time_minutes": 30
            }
        }
        
        results = await self.run(objective, context)
        
        # Post-process results
        results["agent_type"] = "reconnaissance"
        results["discovered_hosts"] = self.discovered_hosts
        results["discovered_services"] = self.discovered_services
        
        return results
