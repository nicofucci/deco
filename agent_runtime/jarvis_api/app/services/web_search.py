from duckduckgo_search import DDGS
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Performs a web search using DuckDuckGo.
        """
        try:
            logger.info(f"Searching web for: {query}")
            results = list(self.ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title"),
                    "href": r.get("href"),
                    "body": r.get("body")
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []

# Global instance
web_search_service = WebSearchService()
