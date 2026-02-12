import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class RagService:
    def __init__(self):
        self.persist_directory = "/opt/deco/agent_runtime/data/chroma_db"
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(name="jarvis_knowledge")
        
        # Load embedding model
        logger.info("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Embedding model loaded.")

    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Adds a document to the knowledge base.
        """
        doc_id = str(uuid.uuid4())
        
        # Simple chunking (can be improved)
        chunks = self._chunk_text(content)
        
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        embeddings = self.model.encode(chunks).tolist()
        metadatas = [metadata or {} for _ in range(len(chunks))]
        documents = chunks
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        logger.info(f"Added document {doc_id} with {len(chunks)} chunks.")
        return doc_id

    def query(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """
        Queries the knowledge base.
        """
        query_embedding = self.model.encode([query_text]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
                
        return formatted_results

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        Splits text into chunks.
        """
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Global instance
rag_service = RagService()
