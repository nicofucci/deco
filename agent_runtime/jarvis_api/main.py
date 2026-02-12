from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.models.catalog import Action
from typing import List, Dict, Optional, Any
import asyncio
import redis.asyncio as aioredis
from pathlib import Path
import shutil
from datetime import datetime
from app.logging_config import setup_logging

setup_logging()

# Importar servicios
from app.services.ollama_client import JarvisOllamaClient
from app.services.qdrant_memory import JarvisQdrantMemory
from app.services.redis_bus import JarvisRedisBus
from app.services.rag_pipeline import JarvisRAGPipeline

# Importar Auth
from app.dependencies import auth_system, rbac_manager, get_current_user, require_permission, redis_bus

# Importar Agentes Avanzados
from app.agents.advanced.recon_advanced import ReconAgentAdvanced
from app.agents.advanced.vuln_scanner import VulnScannerAgent
from app.agents.advanced.risk_scorer import RiskScorer, VulnerabilityRanker

# Importar Routers
from app.routes import catalog, execution, reports, nodes, tenants, intelligence, chat, memory, agents, learning, cases, dashboard, agents_tests, ai_benchmarks, ai_performance, playbooks, webhooks, alerts, health

app = FastAPI(
    title="Jarvis API v3.0",
    version="3.0.0",
    description="Backend para Deco-Gravity Agent System"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Routers
app.include_router(catalog.router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(execution.router, prefix="/api/execution", tags=["Execution"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(nodes.router, prefix="/api/nodes", tags=["Nodes"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["Tenants"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["Intelligence"])
app.include_router(agents.router, prefix="/api/agents", tags=["AI Agents"])
app.include_router(learning.router, prefix="/api/learning", tags=["CLE Learning"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(cases.router, prefix="/cases", tags=["Cases"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(agents_tests.router, prefix="/ai/tests", tags=["AI Agents Tests"])
app.include_router(ai_benchmarks.router, prefix="/ai/tests", tags=["AI Agents Benchmarks"])
app.include_router(ai_performance.router, prefix="/ai/performance", tags=["AI Performance"])
app.include_router(playbooks.router, prefix="/api/playbooks", tags=["Playbooks"])
app.include_router(webhooks.router, prefix="/api/hooks", tags=["Webhooks"])
app.include_router(alerts.router, prefix="/ai/alerts", tags=["Alerts"])
app.include_router(health.router, prefix="/ai", tags=["Health"])

# Inicializar servicios
ollama_client = JarvisOllamaClient()
qdrant_memory = JarvisQdrantMemory()
rag_pipeline = JarvisRAGPipeline(ollama_client, qdrant_memory)

# Inicializar Agentes Avanzados
recon_agent = ReconAgentAdvanced()
vuln_scanner = VulnScannerAgent(ollama_client)
risk_scorer = RiskScorer()
vuln_ranker = VulnerabilityRanker(risk_scorer)

# ========== MODELOS PYDANTIC ==========

class ChatRequest(BaseModel):
    message: str
    context: Optional[List[Dict[str, str]]] = []

class RAGQueryRequest(BaseModel):
    question: str
    top_k: int = 5

class ActionRequest(BaseModel):
    target: str
    options: Dict[str, Any] = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class ReconRequest(BaseModel):
    target: str
    ports: Optional[str] = "1-1000"
    aggressive: Optional[bool] = False
    os_detection: Optional[bool] = False

# ========== RUTAS AUTH ==========

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login con usuario y contraseña."""
    # TODO: Validar contra base de datos de usuarios
    # Por ahora, demo con credenciales hardcoded
    
    demo_users = {
        "admin": {"password_hash": auth_system.hash_password("admin123"), "role": "admin"},
        "analyst": {"password_hash": auth_system.hash_password("analyst123"), "role": "analyst"},
        "viewer": {"password_hash": auth_system.hash_password("viewer123"), "role": "viewer"}
    }
    
    user = demo_users.get(request.username)
    if not user or not auth_system.verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Crear tokens
    access_token = auth_system.create_access_token({
        "sub": request.username,
        "role": user["role"]
    })
    
    refresh_token = auth_system.create_refresh_token({
        "sub": request.username
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user["role"]
    }

@app.post("/api/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refrescar access token con refresh token."""
    payload = auth_system.verify_token(refresh_token, "refresh")
    
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    
    new_access_token = auth_system.create_access_token({
        "sub": payload["sub"],
        "role": payload.get("role", "viewer")
    })
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/logout")
async def logout(user: Dict = Depends(get_current_user)):
    """Logout y revocación de refresh tokens."""
    username = user.get("sub")
    auth_system.revoke_refresh_token(username)
    
    return {"message": "Logout exitoso"}

# ========== RUTAS API ==========

@app.get("/")
def read_root():
    return {"status": "online", "system": "Jarvis 3.0", "mode": "Deco-Gravity"}

@app.get("/api/health")
async def health_check():
    """Health check del sistema."""
    return {
        "status": "operational",
        "version": "3.0.0",
        "services": {
            "ollama": ollama_client.check_health(),
            "redis": redis_bus.ping(),
            "qdrant": "connected"
        }
    }

async def run_action_background(action: Action, target: str, user: Dict):
    """Función helper para ejecución en background."""
    try:
        from app.services.kali_runner import kali_runner
        
        redis_bus.publish_log("info", f"Background execution started: {action.name} on {target} requested by {user.get('sub')}")
        
        result = await kali_runner.run_action(
            action_id=action.id,
            script_path=action.script_path_kali,
            target=target,
            params={}
        )
        
        # Generar Reporte con IA
        redis_bus.publish_log("info", "Generating AI Report for execution result...")
        
        report_prompt = [
            {"role": "system", "content": "Eres Jarvis, una IA avanzada de ciberseguridad. Analiza la salida de la herramienta y genera un resumen ejecutivo y un reporte técnico profesional en ESPAÑOL. Sé directo, usa formato Markdown y mantén un tono técnico pero claro."},
            {"role": "user", "content": f"Herramienta: {action.name}\nObjetivo: {target}\n\nSalida:\n{result.get('stdout', '')}"}
        ]
        
        report_response = ollama_client.chat(messages=report_prompt)
        ai_report = report_response.get("message", {}).get("content", "Error generating report.")
        
        # Guardar reporte en memoria (o base de datos futura)
        embedding = ollama_client.generate_embedding(ai_report)
        if embedding:
            qdrant_memory.store_chat_memory(
                user_message=f"System Report: {action.name} on {target}",
                assistant_message=ai_report,
                embedding=embedding
            )
            
        # Guardar reporte en disco para persistencia
        report_path = result.get("report_path")
        if report_path:
            try:
                os.makedirs(report_path, exist_ok=True)
                with open(f"{report_path}/report_ai.md", "w") as f:
                    f.write(ai_report)
                
                with open(f"{report_path}/metadata.json", "w") as f:
                    json.dump(metadata, f)
                
                print(f"DEBUG: Report saved successfully to {report_path}")
                redis_bus.publish_log("info", f"Report saved to {report_path}")
                    
            except Exception as e:
                print(f"Error saving report to disk: {e}")
                redis_bus.publish_log("error", f"Error saving report: {e}")
        else:
            print("DEBUG: report_path is None or empty")
            redis_bus.publish_log("error", "Report path missing, cannot save report.")
            
        # Notificar finalización (vía Redis Log por ahora)
        redis_bus.publish_log("success", f"✅ Reporte generado para {action.name} sobre {target}. Ver en historial.")
        
    except Exception as e:
        print(f"BACKGROUND ERROR: {e}")
        redis_bus.publish_log("error", f"Error en background task: {str(e)}")

@app.post("/api/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    user: Dict = Depends(require_permission("write"))
):
    """Ingesta documento en base de conocimiento."""
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        result = rag_pipeline.ingest_document(temp_path)
        Path(temp_path).unlink(missing_ok=True)
        
        redis_bus.publish_log("info", f"Documento ingestado por {user.get('sub')}: {file.filename}")
        
        return result
    
    except Exception as e:
        redis_bus.publish_log("error", f"Error ingesta: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/query")
async def rag_query(
    request: RAGQueryRequest,
    user: Dict = Depends(get_current_user)
):
    """Consulta base de conocimiento con RAG."""
    try:
        result = rag_pipeline.query_knowledge(
            question=request.question,
            top_k=request.top_k
        )
        
        redis_bus.publish_log("info", f"RAG query por {user.get('sub')}")
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== RUTAS AGENTES AVANZADOS ==========

@app.post("/api/agents/recon")
async def run_recon(
    request: ReconRequest,
    user: Dict = Depends(require_permission("execute_agents"))
):
    """Ejecuta reconocimiento avanzado."""
    try:
        redis_bus.publish_log("warning", f"Recon iniciado por {user.get('sub')}: {request.target}")
        redis_bus.publish_agent_state("recon-advanced", "working", {"target": request.target})
        
        results = await recon_agent.run_full_discovery(
            target=request.target,
            options={
                "ports": request.ports,
                "aggressive": request.aggressive,
                "os_detection": request.os_detection
            }
        )
        
        redis_bus.publish_agent_state("recon-advanced", "idle", {})
        redis_bus.publish_log("info", f"Recon completado: {len(results.get('phases', {}))} fases")
        
        return results
    
    except Exception as e:
        redis_bus.publish_agent_state("recon-advanced", "error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/vulnscan")
async def run_vuln_scan(
    request: ActionRequest,
    user: Dict = Depends(require_permission("execute_agents"))
):
    """Ejecuta escaneo de vulnerabilidades."""
    try:
        redis_bus.publish_log("warning", f"VulnScan iniciado por {user.get('sub')}")
        redis_bus.publish_agent_state("vuln-scanner", "working", {"target": request.target})
        
        # Primero recon para obtener servicios
        recon_results = await recon_agent.run_full_discovery(request.target)
        services = recon_results.get("phases", {}).get("services", {})
        
        # Escanear vulnerabilidades
        vulnerabilities = await vuln_scanner.scan_target(request.target, services)
        
        # Calcular riesgos y rankear
        ranked_vulns = vuln_ranker.rank_vulnerabilities(vulnerabilities)
        grouped = vuln_ranker.group_by_risk_level(vulnerabilities)
        
        redis_bus.publish_agent_state("vuln-scanner", "idle", {})
        redis_bus.publish_log("info", f"VulnScan completado: {len(vulnerabilities)} vulns encontradas")
        
        return {
            "target": request.target,
            "total_vulnerabilities": len(vulnerabilities),
            "ranked": ranked_vulns[:10],  # Top 10
            "by_risk_level": {
                level: len(vulns) for level, vulns in grouped.items()
            }
        }
    
    except Exception as e:
        redis_bus.publish_agent_state("vuln-scanner", "error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/status")
async def get_agents_status(user: Dict = Depends(get_current_user)):
    """Obtiene estado de todos los agentes."""
    return {
        "agents": {
            "recon": "idle",
            "vuln_scanner": "idle",
            "intel": "idle"
        },
        "user": user.get("sub"),
        "role": user.get("role")
    }

# ========== LEGACY ROUTES (sin auth para compatibilidad) ==========

@app.post("/api/actions/recon")
async def action_recon_legacy(request: ActionRequest):
    """Legacy: Reconocimiento (sin auth)."""
    redis_bus.publish_log("warning", f"Recon legacy: {request.target}")
    return {"status": "scheduled", "agent": "recon-agent", "mode": "legacy"}

@app.post("/api/actions/vulnmap")
async def action_vulnmap_legacy(request: ActionRequest):
    """Legacy: VulnMap (sin auth)."""
    redis_bus.publish_log("warning", f"VulnMap legacy: {request.target}")
    return {"status": "scheduled", "agent": "vulnmapper-agent", "mode": "legacy"}

# ========== WEBSOCKETS ==========

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """Stream de logs en tiempo real."""
    await websocket.accept()
    
    redis_client = aioredis.from_url("redis://localhost:6379")
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("deco.logs")
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.1)
    
    except WebSocketDisconnect:
        await pubsub.unsubscribe("deco.logs")
        await redis_client.close()

@app.websocket("/ws/agents")
async def websocket_agents(websocket: WebSocket):
    """Stream de estados de agentes."""
    await websocket.accept()
    
    redis_client = aioredis.from_url("redis://localhost:6379")
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("deco.agents.state")
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.1)
    
    except WebSocketDisconnect:
        await pubsub.unsubscribe("deco.agents.state")
        await redis_client.close()

# Import Watchers
from app.watchers.ai_performance_watcher import start_ai_performance_watcher
from app.watchers.pentest_watcher import start_pentest_watcher
from app.watchers.system_health_watcher import start_system_health_watcher
from app.watchers.llm_latency_watcher import start_llm_latency_watcher
from app.watchers.worker_monitor_watcher import start_worker_monitor_watcher
from app.watchers.qdrant_monitor_watcher import start_qdrant_monitor_watcher
from app.watchers.redis_monitor_watcher import start_redis_monitor_watcher
from app.watchers.orchestrator_monitor_watcher import start_orchestrator_monitor_watcher
from app.watchers.risk_global_watcher import start_risk_global_watcher
from app.watchers.continuous_audit_watcher import start_continuous_audit_watcher
from app.watchers.client_risk_watcher import start_client_risk_watcher
from app.watchers.asset_risk_watcher import start_asset_risk_watcher
from app.watchers.auto_remediation_watcher import start_auto_remediation_watcher

# Import Risk Controller
from app.risk import risk_controller

# Include Risk Router
app.include_router(risk_controller.router, prefix="/ai/risk", tags=["Risk Center"])

# Import Actions Router
from app.routes import actions
app.include_router(actions.router, prefix="/ai/actions", tags=["Hybrid Actions"])

# Import Jarvis Console Router
from app.routes import jarvis_console, jarvis_sessions
app.include_router(jarvis_console.router, prefix="/ai/jarvis", tags=["Jarvis Console"])
app.include_router(jarvis_sessions.router, prefix="/ai/jarvis", tags=["Jarvis Sessions"])

from app.database import init_db

@app.on_event("startup")
async def startup_event():
    """Initialize background watchers and database."""
    init_db()
    # Start watchers as background tasks
    asyncio.create_task(start_ai_performance_watcher())
    asyncio.create_task(start_pentest_watcher())
    asyncio.create_task(start_system_health_watcher())
    asyncio.create_task(start_llm_latency_watcher())
    asyncio.create_task(start_worker_monitor_watcher())
    asyncio.create_task(start_qdrant_monitor_watcher())
    asyncio.create_task(start_redis_monitor_watcher())
    asyncio.create_task(start_orchestrator_monitor_watcher())
    
    # Risk Watchers
    asyncio.create_task(start_risk_global_watcher())
    asyncio.create_task(start_continuous_audit_watcher())
    asyncio.create_task(start_client_risk_watcher())
    asyncio.create_task(start_asset_risk_watcher())
    
    # Auto-Remediation Watcher
    asyncio.create_task(start_auto_remediation_watcher())

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 18001))
    uvicorn.run(app, host="0.0.0.0", port=port)
