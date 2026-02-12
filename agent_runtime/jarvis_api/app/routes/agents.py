"""
API Routes for Intelligent AI Agents
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from app.agents.specialized.recon_agent_ai import ReconAgentAI

router = APIRouter()

# In-memory storage for agent sessions (would be Redis/DB in production)
AGENT_SESSIONS: Dict[str, Dict[str, Any]] = {}


class AgentRunRequest(BaseModel):
    target: str
    scan_type: Optional[str] = "adaptive"
    params: Optional[Dict[str, Any]] = {}


class AgentSession(BaseModel):
    session_id: str
    agent_type: str
    status: str  # "running", "completed", "failed"
    started_at: str
    completed_at: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_agents():
    """List all available intelligent agents."""
    return {
        "agents": [
            {
                "id": "recon-ai",
                "name": "Reconnaissance Agent",
                "description": "Autonomous network discovery with adaptive scanning",
                "capabilities": [
                    "Network topology mapping",
                    "Service fingerprinting",
                    "Technology detection",
                    "Asset inventory"
                ],
                "status": "available"
            },
            {
                "id": "vuln-ai",
                "name": "Vulnerability Assessment Agent",
                "description": "Intelligent vulnerability analysis and prioritization",
                "capabilities": [
                    "CVE matching",
                    "Risk scoring",
                    "Exploit assessment",
                    "Mitigation recommendations"
                ],
                "status": "coming_soon"
            },
            {
                "id": "report-ai",
                "name": "Report Generation Agent",
                "description": "Automated executive and technical report creation",
                "capabilities": [
                    "Executive summaries",
                    "Technical analysis",
                    "Compliance mapping",
                    "Visual dashboards"
                ],
                "status": "coming_soon"
            }
        ]
    }


async def run_recon_agent_background(session_id: str, target: str, scan_type: str, params: Dict[str, Any]):
    """Background task to run reconnaissance agent."""
    try:
        AGENT_SESSIONS[session_id]["status"] = "running"
        
        # Initialize and run agent
        agent = ReconAgentAI(agent_id=f"recon-{session_id[:8]}")
        results = await agent.run_reconnaissance(target=target, scan_type=scan_type)
        
        # Update session
        AGENT_SESSIONS[session_id]["status"] = "completed"
        AGENT_SESSIONS[session_id]["completed_at"] = datetime.now().isoformat()
        AGENT_SESSIONS[session_id]["results"] = results
        
    except Exception as e:
        AGENT_SESSIONS[session_id]["status"] = "failed"
        AGENT_SESSIONS[session_id]["completed_at"] = datetime.now().isoformat()
        AGENT_SESSIONS[session_id]["error"] = str(e)


@router.post("/recon/run")
async def run_recon_agent(request: AgentRunRequest, background_tasks: BackgroundTasks):
    """
    Execute the Reconnaissance Agent.
    
    The agent runs autonomously using LLM-powered decision making.
    """
    session_id = str(uuid.uuid4())
    
    # Create session record
    AGENT_SESSIONS[session_id] = {
        "session_id": session_id,
        "agent_type": "recon-ai",
        "target": request.target,
        "scan_type": request.scan_type,
        "status": "initializing",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "results": None
    }
    
    # Start agent in background
    background_tasks.add_task(
        run_recon_agent_background,
        session_id,
        request.target,
        request.scan_type,
        request.params
    )
    
    return {
        "session_id": session_id,
        "status": "started",
        "message": f"Reconnaissance agent started for target: {request.target}",
        "check_status_url": f"/api/agents/status/{session_id}"
    }


@router.get("/status/{session_id}")
async def get_agent_status(session_id: str):
    """Get the status of a running agent session."""
    if session_id not in AGENT_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = AGENT_SESSIONS[session_id]
    
    return {
        "session_id": session_id,
        "agent_type": session["agent_type"],
        "status": session["status"],
        "started_at": session["started_at"],
        "completed_at": session.get("completed_at"),
        "has_results": session.get("results") is not None,
        "error": session.get("error")
    }


@router.get("/results/{session_id}")
async def get_agent_results(session_id: str):
    """Get the full results of a completed agent session."""
    if session_id not in AGENT_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = AGENT_SESSIONS[session_id]
    
    if session["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Agent session is {session['status']}, results not available yet"
        )
    
    return {
        "session_id": session_id,
        "agent_type": session["agent_type"],
        "target": session["target"],
        "started_at": session["started_at"],
        "completed_at": session["completed_at"],
        "results": session.get("results", {})
    }


@router.post("/stop/{session_id}")
async def stop_agent(session_id: str):
    """Stop a running agent session."""
    if session_id not in AGENT_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = AGENT_SESSIONS[session_id]
    
    if session["status"] != "running":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot stop agent in status: {session['status']}"
        )
    
    # TODO: Implement actual agent interruption logic
    session["status"] = "stopped"
    session["completed_at"] = datetime.now().isoformat()
    
    return {
        "session_id": session_id,
        "status": "stopped",
        "message": "Agent execution interrupted"
    }


# ============================================================================
# MULTI-AGENT SYSTEM ENDPOINTS (Jarvis 3.0)
# ============================================================================

@router.get("/system/list")
async def list_all_agents_system():
    """List all agents in the multi-agent system"""
    from app.agents import registry
    
    return {
        "agents": registry.get_all_info(),
        "total": len(registry)
    }


@router.get("/system/health")
async def health_check_system():
    """Health check for all agents in the system"""
    from app.agents import dispatcher
    
    results = await dispatcher.ping_all_agents()
    
    return {
        "agents": {code: resp.dict() for code, resp in results.items()},
        "total_healthy": sum(1 for r in results.values() if r.status.value == "success")
    }


@router.post("/jarvis/ask")
async def ask_jarvis_prime(message: str, user_id: str = "default"):
    """
    Main endpoint for Jarvis Prime  
    Processes natural language requests and coordinates agents
    """
    from app.jarvis_prime import jarvis_prime
    
    response = await jarvis_prime.process_user_request(
        user_input=message,
        user_id=user_id
    )
    
    return response
