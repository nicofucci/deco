from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from app.models.node import Node, NodeStatus, NodeType
import uuid
from datetime import datetime

router = APIRouter()

# Simulación de base de datos en memoria
NODES_DB: List[Node] = [
    Node(
        id="node_local_01",
        name="Kali Local (Default)",
        type=NodeType.SCANNER,
        host="kali-2025",
        protocol="ssh",
        status=NodeStatus.ONLINE,
        capabilities=["nmap", "metasploit", "nikto"]
    )
]

@router.get("/", response_model=List[Node])
async def list_nodes():
    """Lista todos los nodos registrados."""
    return NODES_DB

@router.post("/", response_model=Node)
async def register_node(node: Node):
    """Registra un nuevo nodo."""
    # Verificar duplicados por ID o Host
    if any(n.id == node.id for n in NODES_DB):
        raise HTTPException(status_code=400, detail="Node ID already exists")
    
    node.last_seen = datetime.now()
    NODES_DB.append(node)
    return node

@router.get("/{node_id}", response_model=Node)
async def get_node(node_id: str):
    node = next((n for n in NODES_DB if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.delete("/{node_id}")
async def delete_node(node_id: str):
    global NODES_DB
    NODES_DB = [n for n in NODES_DB if n.id != node_id]
    return {"status": "deleted"}

@router.post("/{node_id}/ping")
async def ping_node(node_id: str):
    """Verifica la conectividad con el nodo (Simulado)."""
    node = next((n for n in NODES_DB if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Aquí iría la lógica real de ping/ssh check
    import asyncio
    # Simular latencia
    await asyncio.sleep(0.5)
    
    node.status = NodeStatus.ONLINE
    node.last_seen = datetime.now()
    return {"status": "online", "latency_ms": 45}
