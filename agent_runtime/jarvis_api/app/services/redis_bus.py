import redis
import json
from typing import Any, Dict
from datetime import datetime

class JarvisRedisBus:
    """Bus de eventos Redis para logs y estados en tiempo real."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        import os
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            self.redis = redis.from_url(redis_url, decode_responses=True)
        else:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    def publish_log(self, level: str, message: str, context: Dict[str, Any] = None):
        """Publica log para WebSocket."""
        event = {
            "type": "log",
            "level": level,
            "message": message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        self.redis.publish("deco.logs", json.dumps(event))
    
    def publish_agent_state(self, agent_id: str, state: str, details: Dict[str, Any] = None):
        """Publica estado de agente."""
        event = {
            "type": "agent_state",
            "agent_id": agent_id,
            "state": state,  # idle, working, completed, failed
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.redis.publish("deco.agents.state", json.dumps(event))
    
    def get_recent_logs(self, count: int = 50) -> list:
        """Obtiene logs recientes (desde lista)."""
        try:
            logs = self.redis.lrange("deco:logs:history", 0, count - 1)
            return [json.loads(log) for log in logs]
        except:
            return []
    
    def store_log(self, level: str, message: str, context: Dict[str, Any] = None):
        """Almacena log en historial (además de publicar)."""
        event = {
            "level": level,
            "message": message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        self.redis.lpush("deco:logs:history", json.dumps(event))
        self.redis.ltrim("deco:logs:history", 0, 499)  # Mantener últimos 500
    
    def ping(self) -> bool:
        """Verifica conexión a Redis."""
        try:
            return self.redis.ping()
        except:
            return False
