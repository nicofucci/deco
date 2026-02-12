"""
Ingestion Module for CLE
"""

from app.cle.ingestion.pipeline import ContentSummarizer, EmbeddingGenerator, IngestionPipeline

__all__ = ["ContentSummarizer", "EmbeddingGenerator", "IngestionPipeline"]
