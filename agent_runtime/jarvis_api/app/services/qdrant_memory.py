from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
import uuid
from datetime import datetime

class JarvisQdrantMemory:
    """Memoria vectorial de Jarvis con colecciones separadas."""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.vector_size = 4096  # llama3.1:8b-instruct-q4_K_M
    
    def ensure_collection(self, collection_name: str):
        """Crea colección si no existe."""
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == collection_name for c in collections):
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"[Qdrant] Colección '{collection_name}' creada")
        except Exception as e:
            print(f"[Qdrant] Error creando colección: {e}")
    
    def store_chat_memory(
        self,
        user_message: str,
        assistant_message: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None
    ):
        """Almacena memoria conversacional."""
        self.ensure_collection("jarvis_chat_memory")
        
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "user": user_message,
                "assistant": assistant_message,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
        )
        
        self.client.upsert(
            collection_name="jarvis_chat_memory",
            points=[point]
        )
    
    def store_knowledge(
        self,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """Almacena fragmento de conocimiento (RAG)."""
        self.ensure_collection("jarvis_knowledge_base")
        
        point_id = str(uuid.uuid4())
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "text": text,
                "source": metadata.get("source", "unknown"),
                "page": metadata.get("page"),
                "section": metadata.get("section"),
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        )
        
        self.client.upsert(
            collection_name="jarvis_knowledge_base",
            points=[point]
        )
        
        return point_id
    
    def search_knowledge(
        self,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict]:
        """Busca en base de conocimiento."""
        self.ensure_collection("jarvis_knowledge_base")
        
        results = self.client.search(
            collection_name="jarvis_knowledge_base",
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold
        )
        
        return [
            {
                "text": hit.payload.get("text"),
                "source": hit.payload.get("source"),
                "page": hit.payload.get("page"),
                "section": hit.payload.get("section"),
                "score": hit.score
            }
            for hit in results
        ]
