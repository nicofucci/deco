"""
GitHub Explorer for CLE
Discovers security tools and best practices from GitHub
"""

from github import Github, GithubException
from typing import List, Optional
import logging
from datetime import datetime
import hashlib
import os

from app.cle.config import GITHUB_TOPICS
from app.cle.models import KnowledgeGitHub, SourceType

logger = logging.getLogger(__name__)


class GitHubExplorer:
    """Explores GitHub for security-related repositories"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize GitHub client
        
        Args:
            access_token: GitHub Personal Access Token (optional, but recommended
                         for higher rate limits: 5000 req/hour vs 60 req/hour)
        """
        if access_token:
            self.github = Github(access_token)
            logger.info("[GitHub] Authenticated with access token")
        else:
            self.github = Github()
            logger.warning("[GitHub] Running unauthenticated (60 req/hour limit)")
    
    def search_repositories(
        self,
        topics: List[str] = None,
        min_stars: int = 100,
        max_results: int = 10
    ) -> List[KnowledgeGitHub]:
        """
        Search for repositories by topics
        
        Args:
            topics: List of topics to search (default: from config)
            min_stars: Minimum star count filter
            max_results: Maximum number of repos to return
        
        Returns:
            List of KnowledgeGitHub items
        """
        if topics is None:
            topics = GITHUB_TOPICS
        
        repos = []
        
        for topic in topics[:3]:  # Limit to 3 topics per call to avoid rate limits
            try:
                logger.info(f"[GitHub] Searching topic: {topic}")
                
                # Build search query
                query = f"topic:{topic} stars:>={min_stars}"
                
                # Search repositories
                search_results = self.github.search_repositories(
                    query=query,
                    sort="stars",
                    order="desc"
                )
                
                # Process results
                for repo in search_results[:max_results]:
                    try:
                        knowledge_repo = self._process_repository(repo)
                        if knowledge_repo:
                            repos.append(knowledge_repo)
                            logger.info(f"[GitHub] Found: {repo.full_name} ({repo.stargazers_count} ⭐)")
                    except Exception as e:
                        logger.error(f"[GitHub] Error processing {repo.full_name}: {e}")
                        continue
                
            except GithubException as e:
                logger.error(f"[GitHub] Search error for topic '{topic}': {e}")
                continue
        
        return repos
    
    def _process_repository(self, repo) -> Optional[KnowledgeGitHub]:
        """Process a GitHub repository into KnowledgeGitHub"""
        try:
            # Get README content
            readme_content = self._get_readme(repo)
            if not readme_content:
                logger.debug(f"[GitHub] No README for {repo.full_name}, skipping")
                return None
            
            # Generate ID
            repo_id = hashlib.md5(repo.html_url.encode()).hexdigest()
            
            # Extract topics
            topics = list(repo.get_topics()) if hasattr(repo, 'get_topics') else []
            
            # Create KnowledgeGitHub
            knowledge_repo = KnowledgeGitHub(
                id=repo_id,
                source_type=SourceType.GITHUB,
                repo_url=repo.html_url,
                repo_name=repo.full_name,
                description=repo.description or "No description",
                stars=repo.stargazers_count,
                language=repo.language,
                topics=topics,
                readme_content=readme_content,
                summary="",  # Will be filled by summarization service
                concepts=[],
                use_cases_jarvis=[],
                tags=self._extract_tags(repo),
                relevance_score=self._calculate_relevance(repo),
                discovered_at=datetime.now()
            )
            
            return knowledge_repo
            
        except Exception as e:
            logger.error(f"[GitHub] Error processing repository: {e}")
            return None
    
    def _get_readme(self, repo) -> Optional[str]:
        """Get README content from repository"""
        try:
            readme = repo.get_readme()
            content = readme.decoded_content.decode('utf-8')
            return content
        except GithubException:
            # No README file
            return None
        except Exception as e:
            logger.error(f"[GitHub] Error fetching README: {e}")
            return None
    
    def _extract_tags(self, repo) -> List[str]:
        """Extract tags from repository metadata"""
        tags = []
        
        # Language
        if repo.language:
            tags.append(repo.language.lower())
        
        # Topics
        if hasattr(repo, 'get_topics'):
            tags.extend(repo.get_topics()[:5])  # Max 5 topics
        
        return tags
    
    def _calculate_relevance(self, repo) -> float:
        """Calculate relevance score based on stars, activity, etc."""
        # Simple scoring based on stars
        stars = repo.stargazers_count
        
        if stars >= 10000:
            return 1.0
        elif stars >= 5000:
            return 0.9
        elif stars >= 1000:
            return 0.8
        elif stars >= 500:
            return 0.7
        elif stars >= 100:
            return 0.6
        else:
            return 0.5
    
    def get_rate_limit(self) -> dict:
        """Get current GitHub API rate limit status"""
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                "core_remaining": rate_limit.core.remaining,
                "core_limit": rate_limit.core.limit,
                "search_remaining": rate_limit.search.remaining,
                "search_limit": rate_limit.search.limit,
            }
        except Exception as e:
            logger.error(f"[GitHub] Error getting rate limit: {e}")
            return {}


def get_github_token_from_env() -> Optional[str]:
    """Get GitHub token from environment variable"""
    return os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_ACCESS_TOKEN")
