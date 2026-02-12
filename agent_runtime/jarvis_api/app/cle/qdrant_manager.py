"""
CLE Qdrant Manager
Handles creation and management of CLE knowledge collections
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
import uuid
import logging

from app.cle.config import CLE_COLLECTIONS
from app.cle.models import KnowledgeArticle, KnowledgeGitHub, KnowledgeYouTube, SourceType

logger = logging.getLogger(__name__)


class CLEQdrantManager:
    """Manages Qdrant collections for CLE knowledge base"""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.vector_size = 4096  # Llama 3.1 embeddings
    
    def setup_collections(self):
        """Create all CLE collections if they don't exist"""
        for collection_name, config in CLE_COLLECTIONS.items():
            try:
                self._ensure_collection(collection_name, config["vector_size"])
                logger.info(f"[CLE] Collection '{collection_name}' ready")
            except Exception as e:
                logger.error(f"[CLE] Error setting up collection '{collection_name}': {e}")
    
    def _ensure_collection(self, collection_name: str, vector_size: int):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"[CLE Qdrant] Created collection: {collection_name}")
            else:
                logger.debug(f"[CLE Qdrant] Collection exists: {collection_name}")
                
        except Exception as e:
            logger.error(f"[CLE Qdrant] Error ensuring collection '{collection_name}': {e}")
            raise
    
    def store_article(self, article: KnowledgeArticle):
        """Store a web article in Qdrant"""
        if not article.embedding:
            raise ValueError("Article must have embedding vector")
        
        point = PointStruct(
            id=article.id,
            vector=article.embedding,
            payload={
                "source_type": article.source_type.value,
                "source_url": str(article.source_url),
                "title": article.title,
                "content": article.content[:2000],  # Truncate for payload
                "summary": article.summary,
                "concepts": article.concepts,
                "use_cases_jarvis": article.use_cases_jarvis,
                "tags": article.tags,
                "relevance_score": article.relevance_score,
                "discovered_at": article.discovered_at.isoformat(),
            }
        )
        
        self.client.upsert(
            collection_name="cle_articles",
            points=[point]
        )
        logger.info(f"[CLE] Stored article: {article.title}")
    
    def store_github_repo(self, repo: KnowledgeGitHub):
        """Store a GitHub repo in Qdrant"""
        if not repo.embedding:
            raise ValueError("Repo must have embedding vector")
        
        point = PointStruct(
            id=repo.id,
            vector=repo.embedding,
            payload={
                "source_type": repo.source_type.value,
                "repo_url": str(repo.repo_url),
                "repo_name": repo.repo_name,
                "description": repo.description,
                "stars": repo.stars,
                "language": repo.language,
                "topics": repo.topics,
                "readme_content": repo.readme_content[:2000],
                "summary": repo.summary,
                "concepts": repo.concepts,
                "use_cases_jarvis": repo.use_cases_jarvis,
                "tags": repo.tags,
                "relevance_score": repo.relevance_score,
                "discovered_at": repo.discovered_at.isoformat(),
            }
        )
        
        self.client.upsert(
            collection_name="cle_github",
            points=[point]
        )
        logger.info(f"[CLE] Stored GitHub repo: {repo.repo_name}")
    
    def store_youtube_video(self, video: KnowledgeYouTube):
        """Store a YouTube video transcript in Qdrant"""
        if not video.embedding:
            raise ValueError("Video must have embedding vector")
        
        point = PointStruct(
            id=video.id,
            vector=video.embedding,
            payload={
                "source_type": video.source_type.value,
                "video_url": str(video.video_url),
                "video_id": video.video_id,
                "title": video.title,
                "channel": video.channel,
                "duration": video.duration,
                "transcript": video.transcript[:2000],
                "summary": video.summary,
                "concepts": video.concepts,
                "use_cases_jarvis": video.use_cases_jarvis,
                "tags": video.tags,
                "relevance_score": video.relevance_score,
                "discovered_at": video.discovered_at.isoformat(),
            }
        )
        
        self.client.upsert(
            collection_name="cle_youtube",
            points=[point]
        )
        logger.info(f"[CLE] Stored YouTube video: {video.title}")
    
    def search_knowledge(
        self,
        query_vector: List[float],
        collection_name: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search CLE knowledge base"""
        # If no collection specified, search all
        collections_to_search = [collection_name] if collection_name else list(CLE_COLLECTIONS.keys())
        
        all_results = []
        for coll in collections_to_search:
            try:
                results = self.client.search(
                    collection_name=coll,
                    query_vector=query_vector,
                    limit=limit
                )
                all_results.extend([
                    {
                        "collection": coll,
                        "score": r.score,
                        "payload": r.payload
                    }
                    for r in results
                ])
            except Exception as e:
                logger.error(f"[CLE] Error searching collection '{coll}': {e}")
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:limit]
    
    def get_total_knowledge_count(self) -> Dict[str, int]:
        """Get count of items in each collection"""
        counts = {}
        for collection_name in CLE_COLLECTIONS.keys():
            try:
                info = self.client.get_collection(collection_name)
                counts[collection_name] = info.points_count
            except Exception as e:
                logger.error(f"[CLE] Error getting count for '{collection_name}': {e}")
                counts[collection_name] = 0
        
        return counts
