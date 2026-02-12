"""
Discovery Module for CLE
Orchestrates web crawling, GitHub exploration, and YouTube processing
"""

from app.cle.discovery.web_crawler import WebCrawler
from app.cle.discovery.github_explorer import GitHubExplorer, get_github_token_from_env
from app.cle.discovery.youtube_processor import YouTubeProcessor, get_youtube_api_key_from_env

__all__ = [
    "WebCrawler",
    "GitHubExplorer",
    "YouTubeProcessor",
    "get_github_token_from_env",
    "get_youtube_api_key_from_env",
]
