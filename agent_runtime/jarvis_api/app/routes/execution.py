from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.services.kali_runner import kali_runner
from app.services.actions.network_discovery import network_discovery_service
from app.routes.catalog import MOCK_ACTIONS, MOCK_SERVICES # Importing mock data for now

router = APIRouter()

from app.routes.nodes import NODES_DB
from app.routes.tenants import TENANTS_DB

# Base de datos en memoria para persistencia de ejecuciones
EXECUTIONS_DB: List[Dict[str, Any]] = []

class ExecutionRequest(BaseModel):
    target: str
    params: Optional[Dict[str, Any]] = {}
    node_id: Optional[str] = None
    tenant_id: Optional[str] = "tenant_default"
    profile: Optional[str] = None
    allow_public: Optional[bool] = False

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_execution_history(action_id: Optional[str] = None):
    """Obtiene el historial de ejecuciones, opcionalmente filtrado por acción."""
    if action_id:
        return [e for e in EXECUTIONS_DB if e["action_id"] == action_id]
    return EXECUTIONS_DB

@router.get("/{execution_id}", response_model=Dict[str, Any])
async def get_execution_details(execution_id: str):
    """Obtiene los detalles de una ejecución específica."""
    execution = next((e for e in EXECUTIONS_DB if e["execution_id"] == execution_id), None)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@router.post("/actions/{action_id}/run")
async def run_action(action_id: str, request: ExecutionRequest):
    """Ejecuta una acción específica."""
    action = next((a for a in MOCK_ACTIONS if a.id == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    # Resolver nodo de ejecución
    node_config = None
    if request.node_id:
        node = next((n for n in NODES_DB if n.id == request.node_id), None)
        if not node:
             raise HTTPException(status_code=404, detail="Selected Node not found")
        # Convertir a dict para pasar al runner
        node_config = node.dict()
    
    # Resolver Tenant
    tenant_slug = "global"
    if request.tenant_id:
        tenant = next((t for t in TENANTS_DB if t.id == request.tenant_id), None)
        if tenant:
            tenant_slug = tenant.slug

    # Ejecutar act_80 con lógica especializada
    if action.id == "act_80":
        profile = request.profile or (request.params or {}).get("profile") or "standard"
        allow_public = bool(request.allow_public or (request.params or {}).get("allow_public", False))

        result = await network_discovery_service.run(
            target=request.target,
            profile=profile,
            tenant_slug=tenant_slug,
            node_config=node_config,
            allow_public=allow_public
        )

        execution_record = {
            "execution_id": result["execution_id"],
            "action_id": action_id,
            "action_name": action.name,
            "target": request.target,
            "timestamp": datetime.now().isoformat(),
            "status": result.get("status"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "report_path": result.get("report_path", ""),
            "report_id": result.get("report_id"),
            "profile": profile
        }
        EXECUTIONS_DB.append(execution_record)
        return result

    # Ejecutar (async) genérico
    result = await kali_runner.run_action(
        action_id=action.id,
        script_path=action.script_path_kali,
        target=request.target,
        params=request.params,
        node_config=node_config,
        tenant_slug=tenant_slug
    )
    
    # Persistir ejecución
    execution_record = {
        "execution_id": result["execution_id"],
        "action_id": action_id,
        "action_name": action.name,
        "target": request.target,
        "timestamp": datetime.now().isoformat(),
        "status": result["status"],
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "report_path": result.get("report_path", "")
    }
    EXECUTIONS_DB.append(execution_record)
    
    return result

@router.post("/services/{service_id}/run")
async def run_service(service_id: str, request: ExecutionRequest):
    """Ejecuta el pipeline de un servicio."""
    service = next((s for s in MOCK_SERVICES if s.id == service_id), None)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # TODO: Implementar lógica de pipeline secuencial
    # Por ahora, ejecutamos la primera acción como demo
    first_action_link = service.pipeline[0] if service.pipeline else None
    if not first_action_link:
         raise HTTPException(status_code=400, detail="Service has no actions in pipeline")
         
    action = next((a for a in MOCK_ACTIONS if a.id == first_action_link.action_id), None)
    
    result = await kali_runner.run_action(
        action_id=action.id,
        script_path=action.script_path_kali,
        target=request.target,
        params=request.params
    )
    
    # Persistir ejecución (parcial)
    execution_record = {
        "execution_id": result["execution_id"],
        "action_id": action.id,
        "service_id": service_id,
        "action_name": f"{service.name} - {action.name}",
        "target": request.target,
        "timestamp": datetime.now().isoformat(),
        "status": result["status"],
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "report_path": result.get("report_path", "")
    }
    EXECUTIONS_DB.append(execution_record)
    
    return {
        "service_execution_id": result["execution_id"], # Placeholder
        "status": "started",
        "pipeline_step": 1,
        "initial_result": result
    }
