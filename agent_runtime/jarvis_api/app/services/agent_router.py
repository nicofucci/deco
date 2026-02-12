"""
Agent Router Service
Maps intents to appropriate AI agents and orchestrates execution
"""

import logging
from typing import Dict, Optional
from app.agents.specialized.recon_agent_ai import ReconAgentAI

logger = logging.getLogger(__name__)

class AgentRouter:
    """Routes intents to appropriate AI agents"""
    
    def __init__(self):
        # Initialize agents (lazy loading could be added)
        self.recon_agent = None
        
    INTENT_TO_AGENT_MAP = {
        "execute_scan": "recon",
        "vulnerability_analysis": "vuln_scanner",
        "osint": "recon",
        "exploit": "exploit",  # Future
    }
    
    def get_agent_for_intent(self, intent: str) -> Optional[str]:
        """
        Returns agent name for given intent
        
        Args:
            intent: Classified intent
            
        Returns:
            Agent name or None
        """
        return self.INTENT_TO_AGENT_MAP.get(intent)
    
    async def execute_with_agent(
        self, 
        intent: str, 
        params: Dict,
        user: Dict
    ) -> Dict:
        """
        Executes action using appropriate agent
        
        Args:
            intent: User intent
            params: Extracted parameters
            user: User info
            
        Returns:
            Execution result
        """
        agent_name = self.get_agent_for_intent(intent)
        
        if not agent_name:
            return {
                "success": False,
                "error": f"No agent available for intent: {intent}"
            }
        
        logger.info(f"[Agent Router] Routing to {agent_name} with params: {params}")
        
        try:
            if agent_name == "recon":
                return await self._execute_recon(params, user)
            elif agent_name == "vuln_scanner":
                return await self._execute_vuln_scan(params, user)
            else:
                return {
                    "success": False,
                    "error": f"Agent '{agent_name}' not yet implemented"
                }
                
        except Exception as e:
            logger.error(f"[Agent Router] Error executing {agent_name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_recon(self, params: Dict, user: Dict) -> Dict:
        """Execute ReconAgentAI"""
        target = params.get("target", "")
        
        if not target:
            return {"success": False, "error": "No target specified"}
        
        # Initialize agent if needed
        if not self.recon_agent:
            self.recon_agent = ReconAgentAI()
        
        # Execute
        session_id = f"chat_{user['username']}_{target}"
        
        result = await self.recon_agent.run(target=target, session_id=session_id)
        
        return {
            "success": True,
            "agent": "ReconAgentAI",
            "session_id": session_id,
            "result": result,
            "message": f"Reconnaissance completed on {target}"
        }
    
    async def _execute_vuln_scan(self, params: Dict, user: Dict) -> Dict:
        """Execute Vulnerability Scanner (placeholder)"""
        return {
            "success": False,
            "error": "VulnScanner agent not yet implemented in chat mode"
        }
