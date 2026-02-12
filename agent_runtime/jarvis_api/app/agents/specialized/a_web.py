from typing import List, Dict, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus
from app.services.web_search import web_search_service

class WebAgent(BaseAgent):
    """
    Agent responsible for web searches and information retrieval.
    """
    agent_id = "web-agent"
    code = "A-WEB"
    name = "Web Search Agent"
    version = "1.0.0"
    description = "Performs web searches to retrieve up-to-date information."

    @property
    def responsibilities(self) -> List[str]:
        return [
            "Search the web for information",
            "Retrieve documentation and technical details",
            "Find exploits and vulnerabilities online"
        ]

    @property
    def tools(self) -> List[str]:
        return ["duckduckgo-search"]

    @property
    def permissions(self) -> List[str]:
        return ["internet-access"]

    async def execute(self, message: AgentMessage) -> AgentResponse:
        """
        Execute web search actions.
        """
        intent = message.intent
        params = message.params
        
        if intent == "search":
            query = params.get("query")
            if not query:
                return AgentResponse(
                    request_id=message.request_id,
                    agent_code=self.code,
                    status=ResponseStatus.FAILED,
                    summary="Query parameter is required for search."
                )
            
            results = web_search_service.search(query)
            
            summary = f"Found {len(results)} results for '{query}'"
            details = {"results": results}
            
            # Create a nice summary for the LLM
            formatted_results = "\n".join([f"- [{r['title']}]({r['href']}): {r['body']}" for r in results])
            
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.SUCCESS,
                summary=summary,
                details=details,
                artifacts=[formatted_results] # Pass results as artifact/text
            )
            
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Unknown intent: {intent}"
            )
