"""
Jarvis Prime - Main Orchestrator
The central intelligence that coordinates all agents
"""

import logging
from typing import Dict, Optional, Any, List
from app.services.ollama_client import JarvisOllamaClient
from app.agents.dispatcher import dispatcher, DispatchResult
from app.agents.protocol import AgentResponse
from app.jarvis_prime.prompts import build_system_prompt
from app.tools.web_search import web_search

logger = logging.getLogger(__name__)


class JarvisPrime:
    """
    Jarvis Prime - The Master Orchestrator
    
    Responsibilities:
    - Understand user requests in natural language
    - Decide which agents to call and in what order
    - Coordinate multi-agent workflows
    - Synthesize results into human-readable responses
    - Maintain conversation context
    """
    
    def __init__(self):
        self.llm = JarvisOllamaClient()
        self.dispatcher = dispatcher
        self.conversation_memory: Dict[str, list] = {}
        self.logger = logging.getLogger("jarvis.prime")
    
    async def process_user_request(
        self,
        user_input: str,
        user_id: str = "default",
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None,
        use_web_search: bool = False,
    ) -> Dict:
        """
        Main entry point for user requests
        """
        self.logger.info(f"[Jarvis Prime] Processing: {user_input[:50]}...")

        context = context or {}
        conversation_history = history if history is not None else self.conversation_memory.get(user_id, [])

        # Initialize memory slot if needed
        if history is None and user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []

        intent_analysis = await self._analyze_intent(user_input, conversation_history)

        if intent_analysis.get("workflow"):
            result = await self.dispatcher.execute_workflow(
                intent_analysis["workflow"], intent_analysis.get("params", {})
            )
        elif intent_analysis.get("agents"):
            result = await self._execute_agent_chain(
                intent_analysis["agents"], intent_analysis.get("params", {}), context
            )
        else:
            result = await self._general_conversation(
                user_input=user_input,
                history=conversation_history,
                use_web_search=use_web_search or context.get("use_web_search", False),
            )

        response = await self.synthesize_response(result, user_input)

        updated_history = conversation_history + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response["message"]},
        ]
        self.conversation_memory[user_id] = updated_history[-20:]
        return response
    
    async def _analyze_intent(
        self,
        user_input: str,
        conversation_history: list
    ) -> Dict:
        """
        Analyze user intent using LLM
        
        Returns:
            {
                "intent_type": "workflow" | "agents" | "conversation",
                "workflow": "network_audit" (if applicable),
                "agents": [(code, intent, params)] (if applicable),
                "params": {...}
            }
        """
        prompt = f"""
Analiza esta petición del usuario y determina qué agentes de Jarvis necesita:

PETICIÓN: {user_input}

AGENTES DISPONIBLES:
- A-INFRA: Infraestructura y servicios (health check, restart)
- A-SCAN: Escaneo de red y reconocimiento
- A-VULN: Análisis de vulnerabilidades
- A-REPORT: Generación de informes
- A-WEB: Búsqueda en internet y documentación
- A-RAG: Base de conocimientos y análisis de documentos (store, query)

WORKFLOWS DISPONIBLES:
- network_audit: Auditoría completa de red (A-SCAN → A-VULN → A-REPORT)

Responde en JSON:
{{
  "intent_type": "workflow|agents|conversation",
  "workflow": "nombre_workflow" (si aplica),
  "agents": ["A-CODE1", "A-CODE2"] (si aplica),
  "params": {{"target": "...", ...}}
}}

RESPONDE SOLO CON JSON.
"""
        
        try:
            response = self.llm.chat(messages=[
                {"role": "system", "content": "Eres el analizador de intenciones de Jarvis. Responde solo con JSON válido."},
                {"role": "user", "content": prompt}
            ])
            
            import json
            content = response["message"]["content"].strip()
            
            # Remove markdown if present
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            analysis = json.loads(content)
            self.logger.info(f"[Intent] {analysis}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"[Intent] Error: {e}")
            # Fallback to conversation
            return {"intent_type": "conversation"}
    
    async def _execute_agent_chain(
        self,
        agent_codes: list,
        params: Dict,
        context: Dict
    ) -> DispatchResult:
        """Execute a chain of agents"""
        agents_to_call = []
        
        for code in agent_codes:
            # Map agent code to intent and params
            # TODO: Make this smarter
            intent = params.get("action", "execute")
            agents_to_call.append((code, intent, params))
        
        return await self.dispatcher.dispatch_to_multiple(agents_to_call, context)
    
    async def _general_conversation(
        self,
        user_input: str,
        history: list,
        use_web_search: bool = False,
    ) -> Dict:
        """Handle general conversation without agents and optionally enrich with web search."""
        try:
            search_results = []
            if use_web_search or self._should_use_web_search(user_input):
                search_results = web_search(user_input, max_results=5)

            context_block = ""
            if search_results:
                lines = []
                for item in search_results[:5]:
                    title = item.get("title") or "sin título"
                    link = item.get("link") or ""
                    snippet = item.get("snippet") or ""
                    lines.append(f"- {title} {f'({link})' if link else ''}: {snippet}")
                context_block = "Contexto de búsqueda web:\n" + "\n".join(lines)

            system_prompt = build_system_prompt(enable_web_search=bool(search_results) or use_web_search)
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history[-10:])  # keep short context

            user_payload = user_input
            if context_block:
                user_payload = f"{user_input}\n\n{context_block}"

            messages.append({"role": "user", "content": user_payload})

            response = self.llm.chat(messages=messages)

            return {
                "type": "conversation",
                "message": response["message"]["content"],
                "used_web_search": bool(search_results),
            }
        except Exception as e:
            return {
                "type": "conversation",
                "message": f"Lo siento, tuve un error: {e}",
                "used_web_search": False,
            }

    def _should_use_web_search(self, user_input: str) -> bool:
        triggers = ["noticia", "última", "ultimo", "buscar", "busca", "trend", "tendencia", "google", "web"]
        lowered = user_input.lower()
        return any(keyword in lowered for keyword in triggers)
    
    async def synthesize_response(
        self,
        result: Any,
        original_request: str
    ) -> Dict:
        """
        Synthesize agent results into human-readable response
        
        Takes technical results from agents and converts them into
        a friendly, informative response for the user
        """
        if isinstance(result, dict) and result.get("type") == "conversation":
            return {
                "message": result["message"],
                "agents_used": [],
                "artifacts": [],
                "success": True
            }
        
        if isinstance(result, DispatchResult):
            # Build summary from all agent responses
            summary_parts = []
            
            for response in result.responses:
                if response.summary:
                    summary_parts.append(f"**{response.agent_code}:** {response.summary}")
            
            combined_summary = "\n\n".join(summary_parts)
            
            # Ask LLM to make it more natural
            try:
                synthesis_prompt = f"""
El usuario pidió: "{original_request}"

Los agentes ejecutaron lo siguiente:
{combined_summary}

Genera una respuesta amigable y profesional resumiendo los resultados.
Sé conciso pero informativo.
"""
                
                llm_response = self.llm.chat(messages=[
                    {"role": "system", "content": "Eres Jarvis. Resume los resultados de forma clara y amigable. IMPORTANTE: Responde SIEMPRE en ESPAÑOL."},
                    {"role": "user", "content": synthesis_prompt}
                ])
                
                message = llm_response["message"]["content"]
            except:
                message = combined_summary
            
            return {
                "message": message,
                "agents_used": result.agents_used,
                "artifacts": result.artifacts,
                "success": result.success,
                "details": result.details
            }
        
        return {
            "message": "Procesamiento completado",
            "success": True
        }


# Global Jarvis Prime instance
jarvis_prime = JarvisPrime()
