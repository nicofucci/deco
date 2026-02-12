"""
Intent Classifier Service
Uses LLM to detect user intent and extract parameters
"""

import logging
from typing import Dict, Optional, List
from app.services.ollama_client import JarvisOllamaClient

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Classifies user intent using LLM"""
    
    def __init__(self):
        self.ollama = JarvisOllamaClient()
        
    INTENT_PROMPT = """
Clasifica la intención del usuario en UNA de estas categorías:
[general_chat, execute_scan, vulnerability_analysis, osint, exploit, report, show_risk, list_alerts, run_benchmark, list_actions, approve_action, execute_action]

Mensaje: "{message}"

Responde SOLO con la categoría. Nada más.

Ejemplos:
"Hola" -> general_chat
"Escanear 192.168.1.1" -> execute_scan
"Ver riesgo" -> show_risk
"Listar alertas" -> list_alerts
"Aprobar acción 123" -> approve_action
"""

    PARAMS_PROMPT = """
Extrae los parámetros técnicos de esta solicitud de {intent}.

MENSAJE:
{message}

Responde en formato JSON con estos campos:
{{
  "target": "IP, dominio o rango (obligatorio para scans)",
  "ports": "lista de puertos específicos o 'all' (opcional)",
  "scan_type": "quick|full|stealth (opcional, default: quick)",
  "depth": "superficial|normal|deep (opcional, default: normal)",
  "action_id": "ID de la acción para aprobar/ejecutar (si aplica)",
  "entity": "client|asset|global (para riesgo/alertas)",
  "limit": "número de items (opcional)"
}}

Si no se menciona un campo opcional, omítelo del JSON.
RESPONDE SOLO CON EL JSON, sin markdown, sin explicaciones.
"""

    async def classify_intent(self, message: str) -> str:
        """
        Classifies user intent using deterministic rules (No LLM).
        
        Returns:
            Intent category name
        """
        text = (message or "").strip().lower()
        
        # 1. Slash Commands
        if text.startswith("/salud"): return "system.health"
        if text.startswith("/riesgo_global"): return "risk.global"
        if text.startswith("/alertas_criticas"): return "alerts.critical"
        if text.startswith("/acciones_pendientes"): return "actions.pending"
        if text.startswith("/benchmarks_ia"): return "benchmarks.run_all"
        
        # 2. Keyword Rules
        
        # System Health
        if any(kw in text for kw in ["salud del sistema", "salud sistema", "estado del sistema", "estado de la torre", "health", "system health"]):
            return "system.health"
            
        # Risk Global
        if any(kw in text for kw in ["riesgo global", "riesgo del sistema", "risk center", "riesgos generales", "ver riesgo", "show risk"]):
            return "risk.global"
            
        # Critical Alerts
        if any(kw in text for kw in ["alertas criticas", "alertas críticas", "alertas importantes", "critical alerts", "listar alertas", "list alerts"]):
            return "alerts.critical"
            
        # Pending Actions
        if any(kw in text for kw in ["acciones pendientes", "acciones en espera", "pending actions", "listar acciones", "list actions"]):
            return "actions.pending"
            
        # Benchmarks
        if any(kw in text for kw in ["benchmarks", "pruebas de rendimiento", "test de agentes", "benchmark de ia", "run benchmark"]):
            return "benchmarks.run_all"
            
        # Action Approval/Execution (Regex for ID extraction would be better, but simple keyword for now)
        if "aprobar" in text or "approve" in text:
            return "approve_action"
        if "ejecutar" in text or "execute" in text:
            if "scan" in text or "escanear" in text:
                return "execute_scan"
            return "execute_action"
            
        # Scan
        if "escanear" in text or "scan" in text:
            return "execute_scan"

        # Default
        return "general_chat"
    
    async def extract_parameters(self, message: str, intent: str) -> Dict:
        """
        Extracts parameters for a given intent
        
        Returns:
            Dictionary of parameters
        """
        try:
            prompt = self.PARAMS_PROMPT.format(intent=intent, message=message)
            
            response = self.ollama.chat(messages=[
                {"role": "system", "content": "Eres un extractor de parámetros. Responde solo con JSON válido."},
                {"role": "user", "content": prompt}
            ])
            
            import json
            params_str = response["message"]["content"].strip()
            
            # Remove markdown code blocks if present
            if "```" in params_str:
                params_str = params_str.split("```")[1]
                if params_str.startswith("json"):
                    params_str = params_str[4:]
            
            params = json.loads(params_str)
            
            logger.info(f"[Intent] Extracted params: {params}")
            return params
            
        except Exception as e:
            logger.error(f"[Intent] Error extracting params: {e}")
            return {}
    
    async def analyze_message(self, message: str) -> Dict:
        """
        Complete analysis: intent + parameters
        
        Returns:
            {
                "intent": "execute_scan",
                "params": {...},
                "confidence": "high|medium|low"
            }
        """
        intent = await self.classify_intent(message)
        
        params = {}
        if intent != "general_chat":
            params = await self.extract_parameters(message, intent)
        
        # Simple confidence based on parameter extraction
        confidence = "high" if params else "medium" if intent != "general_chat" else "low"
        
        return {
            "intent": intent,
            "params": params,
            "confidence": confidence
        }
