"""
CLE Ingestion Pipeline - Phase 3
Text processing, summarization, and RAG insertion
"""

import logging
import json
from typing import Dict, List, Optional
import asyncio

from app.cle.models import KnowledgeArticle, KnowledgeGitHub, KnowledgeYouTube
from app.cle.config import SUMMARIZATION_PROMPT
from app.services.ollama_client import JarvisOllamaClient
from app.cle.qdrant_manager import CLEQdrantManager

logger = logging.getLogger(__name__)


class ContentSummarizer:
    """Summarizes content using LLM"""
    
    def __init__(self, ollama_client: Optional[JarvisOllamaClient] = None):
        self.ollama = ollama_client or JarvisOllamaClient()
    
    async def summarize(self, content: str, source_type: str = "article") -> Dict:
        """
        Generate summary, concepts, and use cases for Jarvis
        
        Returns:
            Dict with 'summary', 'concepts', 'jarvis_use_cases'
        """
        try:
            # Truncate content if too long (max ~8000 chars for LLM context)
            truncated_content = content[:8000] if len(content) > 8000 else content
            
            # Build prompt
            prompt = SUMMARIZATION_PROMPT.format(content=truncated_content)
            
            logger.info(f"[Summarizer] Processing {source_type}...")
            
            # Call LLM
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.ollama.chat(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3.1:8b-instruct-q4_K_M"
                )
            )
            
            if "error" in response:
                raise Exception(f"LLM error: {response['error']}")
            
            llm_output = response.get("message", {}).get("content", "")
            
            # Try to parse JSON from LLM response
            if "```json" in llm_output:
                llm_output = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                llm_output = llm_output.split("```")[1].split("```")[0].strip()
            
            result = json.loads(llm_output)
            
            logger.info(f"[Summarizer] Generated summary with {len(result.get('concepts', []))} concepts")
            
            return {
                "summary": result.get("summary", "No summary generated"),
                "concepts": result.get("concepts", []),
                "jarvis_use_cases": result.get("jarvis_use_cases", [])
            }
            
        except Exception as e:
            logger.error(f"[Summarizer] Error: {e}")
            # Fallback to simple summary
            return {
                "summary": f"Content from {source_type} (summary generation failed)",
                "concepts": [],
                "jarvis_use_cases": []
            }


class EmbeddingGenerator:
    """Generates embeddings for knowledge items"""
    
    def __init__(self, ollama_client: Optional[JarvisOllamaClient] = None):
        self.ollama = ollama_client or JarvisOllamaClient()
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text"""
        try:
            # Truncate text for embedding
            truncated_text = text[:2000] if len(text) > 2000 else text
            
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.ollama.generate_embedding(truncated_text)
            )
            
            if not embedding:
                raise Exception("Empty embedding returned")
            
            return embedding
            
        except Exception as e:
            logger.error(f"[Embedding] Error generating embedding: {e}")
            return None


class IngestionPipeline:
    """Complete ingestion pipeline for CLE knowledge"""
    
    def __init__(
        self,
        ollama_client: Optional[JarvisOllamaClient] = None,
        qdrant_manager: Optional[CLEQdrantManager] = None
    ):
        self.summarizer = ContentSummarizer(ollama_client)
        self.embedding_generator = EmbeddingGenerator(ollama_client)
        self.qdrant = qdrant_manager or CLEQdrantManager()
    
    async def process_article(self, article: KnowledgeArticle) -> bool:
        """
        Process a web article: summarize, embed, store
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"[Ingestion] Processing article: {article.title}")
            
            # Step 1: Summarize
            summary_data = await self.summarizer.summarize(article.content, "article")
            article.summary = summary_data["summary"]
            article.concepts = summary_data["concepts"]
            article.use_cases_jarvis = summary_data["jarvis_use_cases"]
            
            # Step 2: Generate embedding
            # Combine title + summary for embedding
            text_for_embedding = f"{article.title}\n\n{article.summary}\n\n{' '.join(article.concepts)}"
            embedding = await self.embedding_generator.generate_embedding(text_for_embedding)
            
            if not embedding:
                logger.error(f"[Ingestion] Failed to generate embedding for article: {article.title}")
                return False
            
            article.embedding = embedding
            
            # Step 3: Store in Qdrant
            self.qdrant.store_article(article)
            
            logger.info(f"[Ingestion] Successfully processed article: {article.title}")
            return True
            
        except Exception as e:
            logger.error(f"[Ingestion] Error processing article: {e}")
            return False
    
    async def process_github_repo(self, repo: KnowledgeGitHub) -> bool:
        """Process a GitHub repository: summarize, embed, store"""
        try:
            logger.info(f"[Ingestion] Processing repo: {repo.repo_name}")
            
            # Summarize
            summary_data = await self.summarizer.summarize(repo.readme_content, "github")
            repo.summary = summary_data["summary"]
            repo.concepts = summary_data["concepts"]
            repo.use_cases_jarvis = summary_data["jarvis_use_cases"]
            
            # Generate embedding
            text_for_embedding = f"{repo.repo_name}\n{repo.description}\n\n{repo.summary}\n\n{' '.join(repo.concepts)}"
            embedding = await self.embedding_generator.generate_embedding(text_for_embedding)
            
            if not embedding:
                logger.error(f"[Ingestion] Failed to generate embedding for repo: {repo.repo_name}")
                return False
            
            repo.embedding = embedding
            
            # Store
            self.qdrant.store_github_repo(repo)
            
            logger.info(f"[Ingestion] Successfully processed repo: {repo.repo_name}")
            return True
            
        except Exception as e:
            logger.error(f"[Ingestion] Error processing repo: {e}")
            return False
    
    async def process_youtube_video(self, video: KnowledgeYouTube) -> bool:
        """Process a YouTube video: summarize, embed, store"""
        try:
            logger.info(f"[Ingestion] Processing video: {video.title}")
            
            # Summarize
            summary_data = await self.summarizer.summarize(video.transcript, "youtube")
            video.summary = summary_data["summary"]
            video.concepts = summary_data["concepts"]
            video.use_cases_jarvis = summary_data["jarvis_use_cases"]
            
            # Generate embedding
            text_for_embedding = f"{video.title}\n{video.channel}\n\n{video.summary}\n\n{' '.join(video.concepts)}"
            embedding = await self.embedding_generator.generate_embedding(text_for_embedding)
            
            if not embedding:
                logger.error(f"[Ingestion] Failed to generate embedding for video: {video.title}")
                return False
            
            video.embedding = embedding
            
            # Store
            self.qdrant.store_youtube_video(video)
            
            logger.info(f"[Ingestion] Successfully processed video: {video.title}")
            return True
            
        except Exception as e:
            logger.error(f"[Ingestion] Error processing video: {e}")
            return False
    
    async def process_batch(
        self,
        articles: List[KnowledgeArticle] = None,
        repos: List[KnowledgeGitHub] = None,
        videos: List[KnowledgeYouTube] = None
    ) -> Dict[str, int]:
        """
        Process a batch of knowledge items
        
        Returns:
            Dict with counts of successful/failed items
        """
        results = {
            "articles_success": 0,
            "articles_failed": 0,
            "repos_success": 0,
            "repos_failed": 0,
            "videos_success": 0,
            "videos_failed": 0,
        }
        
        # Process articles
        if articles:
            for article in articles:
                success = await self.process_article(article)
                if success:
                    results["articles_success"] += 1
                else:
                    results["articles_failed"] += 1
        
        # Process repos
        if repos:
            for repo in repos:
                success = await self.process_github_repo(repo)
                if success:
                    results["repos_success"] += 1
                else:
                    results["repos_failed"] += 1
        
        # Process videos
        if videos:
            for video in videos:
                success = await self.process_youtube_video(video)
                if success:
                    results["videos_success"] += 1
                else:
                    results["videos_failed"] += 1
        
        return results
