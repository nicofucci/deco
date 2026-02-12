"""
Jarvis Core Engine 2.0
Motor central mejorado con estado persistente y pipeline de acciones
"""

from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
from enum import Enum

class ActionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JarvisCoreEngine:
    """Motor central de Jarvis 2.0 con estado persistente."""
    
    def __init__(self, redis_client, ollama_client, qdrant_memory):
        self.redis = redis_client
        self.ollama = ollama_client
        self.memory = qdrant_memory
        self.session_id = str(uuid.uuid4())
        
    def get_state(self) -> Dict[str, Any]:
        """Obtiene estado actual del motor."""
        state_key = f"jarvis:state:{self.session_id}"
        state = self.redis.redis.get(state_key)
        
        if state:
            return json.loads(state)
        
        # Estado inicial
        return {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "actions_executed": 0,
            "mode": "defensive",
            "active_agents": [],
            "last_interaction": None
        }
    
    def update_state(self, updates: Dict[str, Any]):
        """Actualiza estado persistente."""
        state = self.get_state()
        state.update(updates)
        state["updated_at"] = datetime.now().isoformat()
        
        state_key = f"jarvis:state:{self.session_id}"
        self.redis.redis.setex(
            state_key,
            3600 * 24,  # 24 horas
            json.dumps(state)
        )
    
    def execute_action(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        security_check: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecuta acción con pipeline de seguridad.
        
        Pipeline:
        1. Validación de seguridad
        2. Logging pre-ejecución
        3. Ejecución
        4. Logging post-ejecución
        5. Actualización de estado
        """
        action_id = str(uuid.uuid4())
        
        # 1. Validación de seguridad
        if security_check and not self._validate_action(action_type, parameters):
            self.redis.publish_log(
                "error",
                f"Acción {action_type} bloqueada por seguridad",
                {"action_id": action_id}
            )
            return {
                "status": "blocked",
                "action_id": action_id,
                "reason": "Acción no permitida en modo defensivo"
            }
        
        # 2. Log pre-ejecución
        self.redis.publish_log(
            "info",
            f"Iniciando acción: {action_type}",
            {"action_id": action_id, "params": parameters}
        )
        
        # 3. Ejecución
        try:
            result = self._execute_action_internal(action_type, parameters)
            status = ActionStatus.COMPLETED
            
        except Exception as e:
            result = {"error": str(e)}
            status = ActionStatus.FAILED
            self.redis.publish_log(
                "error",
                f"Error en acción {action_type}: {str(e)}",
                {"action_id": action_id}
            )
        
        # 4. Log post-ejecución
        self.redis.publish_log(
            "info",
            f"Acción completada: {action_type} - {status.value}",
            {"action_id": action_id}
        )
        
        # 5. Actualizar estado
        state = self.get_state()
        state["actions_executed"] += 1
        state["last_interaction"] = datetime.now().isoformat()
        self.update_state(state)
        
        return {
            "status": status.value,
            "action_id": action_id,
            "result": result
        }
    
    def _validate_action(self, action_type: str, parameters: Dict) -> bool:
        """Valida acción según reglas de seguridad."""
        # Modo defensivo: solo acciones seguras
        safe_actions = [
            "chat",
            "rag_query",
            "recon_scan",  # Solo en laboratorio
            "analyze_vulnerabilities",
            "generate_report"
        ]
        
        if action_type not in safe_actions:
            return False
        
        # Validación de targets
        if "target" in parameters:
            target = parameters["target"]
            # Solo IPs locales/laboratorio
            if not (target.startswith("192.168.") or 
                   target.startswith("10.") or
                   target == "localhost"):
                return False
        
        return True
    
    def _execute_action_internal(self, action_type: str, params: Dict) -> Any:
        """Ejecuta acción internamente (delegado a agentes)."""
        # Aquí se integraría con los agentes existentes
        # Por ahora retorna estructura básica
        return {
            "action": action_type,
            "executed_at": datetime.now().isoformat(),
            "parameters": params
        }
    
    def handle_error(self, error: Exception, context: Dict) -> Dict[str, Any]:
        """Manejo de errores con autocuración."""
        self.redis.publish_log(
            "error",
            f"Error manejado: {str(error)}",
            context
        )
        
        # Intentar recuperación automática
        recovery_action = self._determine_recovery_action(error, context)
        
        if recovery_action:
            self.redis.publish_log(
                "info",
                f"Intentando recuperación: {recovery_action}",
                context
            )
        
        return {
            "error": str(error),
            "context": context,
            "recovery_attempted": bool(recovery_action)
        }
    
    def _determine_recovery_action(self, error: Exception, context: Dict) -> Optional[str]:
        """Determina acción de recuperación según tipo de error."""
        error_type = type(error).__name__
        
        recovery_map = {
            "ConnectionError": "retry_connection",
            "TimeoutError": "increase_timeout",
            "MemoryError": "clear_cache"
        }
        
        return recovery_map.get(error_type)
