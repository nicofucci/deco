from typing import List, Dict, Any
from app.agents.base import BaseAgent
from app.agents.protocol import AgentMessage, AgentResponse, ResponseStatus
from app.services.rag_service import rag_service

class RagAgent(BaseAgent):
    """
    Agent responsible for Knowledge Base management and retrieval (RAG).
    """
    agent_id = "rag-agent"
    code = "A-RAG"
    name = "RAG & Knowledge Agent"
    version = "1.0.0"
    description = "Manages knowledge base, stores documents, and retrieves information."

    @property
    def responsibilities(self) -> List[str]:
        return [
            "Store information in the knowledge base",
            "Retrieve relevant context for queries",
            "Analyze documents and ingest them"
        ]

    @property
    def tools(self) -> List[str]:
        return ["chromadb", "sentence-transformers"]

    @property
    def permissions(self) -> List[str]:
        return ["read-files", "write-db"]

    async def execute(self, message: AgentMessage) -> AgentResponse:
        """
        Execute RAG actions.
        """
        intent = message.intent
        params = message.params
        
        if intent == "store":
            content = params.get("content")
            metadata = params.get("metadata", {})
            
            if not content:
                return AgentResponse(
                    request_id=message.request_id,
                    agent_code=self.code,
                    status=ResponseStatus.FAILED,
                    summary="Content is required for storage."
                )
            
            doc_id = rag_service.add_document(content, metadata)
            
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.SUCCESS,
                summary=f"Stored document with ID: {doc_id}",
                details={"doc_id": doc_id}
            )
            
        elif intent == "query":
            query = params.get("query")
            if not query:
                return AgentResponse(
                    request_id=message.request_id,
                    agent_code=self.code,
                    status=ResponseStatus.FAILED,
                    summary="Query parameter is required."
                )
            
            results = rag_service.query(query)
            
            summary = f"Found {len(results)} relevant fragments."
            
            # Format for LLM context
            context_str = "\n\n".join([f"--- Fragment (Dist: {r['distance']:.2f}) ---\n{r['content']}" for r in results])
            
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.SUCCESS,
                summary=summary,
                details={"results": results},
                artifacts=[context_str]
            )
            
        else:
            return AgentResponse(
                request_id=message.request_id,
                agent_code=self.code,
                status=ResponseStatus.FAILED,
                summary=f"Unknown intent: {intent}"
            )
