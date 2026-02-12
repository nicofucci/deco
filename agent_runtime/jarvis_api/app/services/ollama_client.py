from typing import Optional, List, Dict, Any
import requests
import json

class JarvisOllamaClient:
    """Cliente Ollama para Jarvis con soporte de herramientas y memoria."""
    
    def __init__(self, base_url: str = None, default_model: str = "llama3.1:8b-instruct-q4_K_M"):
        import os
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.default_model = default_model
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = None, # Will use self.default_model if None
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Chat con contexto y herramientas opcionales."""
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream
        }
        
        if tools:
            payload["tools"] = tools
            
        if options:
            payload["options"] = options
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=180
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    def generate_embedding(self, text: str, model: str = "jarvis-core") -> List[float]:
        """Genera embedding para RAG."""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
        except Exception as e:
            print(f"[Ollama] Error generando embedding: {e}")
            return []
    
    def check_health(self) -> bool:
        """Verifica si Ollama está disponible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
