"""
Web Crawler for CLE
Discovers and extracts cybersecurity content from allowed domains
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime
import hashlib

from app.cle.config import ALLOWED_DOMAINS, BLOCKED_KEYWORDS
from app.cle.models import KnowledgeArticle, SourceType

logger = logging.getLogger(__name__)


class WebCrawler:
    """Crawls cybersecurity websites for learning content"""
    
    def __init__(self, user_agent: str = "JarvisCLE/1.0 (Educational Bot)"):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml",
        })
        self.crawl_delay = 2  # Polite crawling: 2 seconds between requests
        
    def is_allowed_domain(self, url: str) -> bool:
        """Check if URL domain is in whitelist"""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix for comparison
            domain = domain.replace("www.", "")
            
            return any(allowed in domain for allowed in ALLOWED_DOMAINS)
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return False
    
    def contains_blocked_keywords(self, text: str) -> bool:
        """Check if content contains blocked keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in BLOCKED_KEYWORDS)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page HTML with error handling"""
        if not self.is_allowed_domain(url):
            logger.warning(f"Domain not allowed: {url}")
            return None
        
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Polite crawling delay
            time.sleep(self.crawl_delay)
            
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_main_content(self, html: str, url: str) -> Optional[Dict[str, str]]:
        """Extract title and main content from HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove script, style, and nav elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Untitled"
            
            # Try to find main content
            main_content = None
            
            # Common content containers
            for selector in ['article', 'main', '.content', '#content', '.post', '.article']:
                if isinstance(selector, str) and selector.startswith('.'):
                    # Class selector
                    main_content = soup.find(class_=selector[1:])
                elif isinstance(selector, str) and selector.startswith('#'):
                    # ID selector
                    main_content = soup.find(id=selector[1:])
                else:
                    # Tag selector
                    main_content = soup.find(selector)
                
                if main_content:
                    break
            
            # Fallback to body
            if not main_content:
                main_content = soup.find('body')
            
            if not main_content:
                return None
            
            # Extract text
            text = main_content.get_text(separator='\n', strip=True)
            
            # Clean up multiple newlines
            text = '\n'.join(line for line in text.split('\n') if line.strip())
            
            return {
                "title": title_text,
                "content": text,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def crawl_url(self, url: str) -> Optional[KnowledgeArticle]:
        """
        Crawl a single URL and create KnowledgeArticle
        
        Returns:
            KnowledgeArticle if successful, None otherwise
        """
        # Fetch page
        html = self.fetch_page(url)
        if not html:
            return None
        
        # Extract content
        extracted = self.extract_main_content(html, url)
        if not extracted:
            logger.warning(f"Could not extract content from {url}")
            return None
        
        # Check for blocked keywords
        if self.contains_blocked_keywords(extracted["content"]):
            logger.warning(f"Content contains blocked keywords: {url}")
            return None
        
        # Generate ID
        article_id = hashlib.md5(url.encode()).hexdigest()
        
        # Create KnowledgeArticle (without embedding for now)
        article = KnowledgeArticle(
            id=article_id,
            source_type=SourceType.WEB,
            source_url=url,
            title=extracted["title"],
            content=extracted["content"],
            summary="",  # Will be filled by summarization service
            concepts=[],
            use_cases_jarvis=[],
            tags=self._extract_tags(url),
            relevance_score=0.5,  # Default, can be adjusted
            discovered_at=datetime.now()
        )
        
        logger.info(f"Successfully crawled: {extracted['title']}")
        return article
    
    def _extract_tags(self, url: str) -> List[str]:
        """Extract tags from URL domain"""
        domain = urlparse(url).netloc.lower()
        tags = []
        
        # Map domains to tags
        if "owasp" in domain:
            tags.append("owasp")
        if "nist" in domain or "nvd" in domain:
            tags.extend(["nist", "cve"])
        if "kali" in domain:
            tags.append("kali")
        if "portswigger" in domain:
            tags.extend(["burp", "web-security"])
        if "tryhackme" in domain or "hackthebox" in domain:
            tags.extend(["training", "lab"])
        
        return tags
    
    def search_and_crawl(
        self,
        search_queries: List[str],
        max_results_per_query: int = 5
    ) -> List[KnowledgeArticle]:
        """
        Search for articles and crawl them
        
        Note: This is a placeholder. In production, you'd integrate with
        Google Custom Search API or similar.
        
        For now, we'll accept a list of direct URLs.
        """
        articles = []
        
        # Placeholder: In real implementation, use search API
        # For now, just accept direct URLs in search_queries
        for url in search_queries:
            if not url.startswith("http"):
                logger.warning(f"Invalid URL: {url}")
                continue
            
            article = self.crawl_url(url)
            if article:
                articles.append(article)
                
                if len(articles) >= max_results_per_query:
                    break
        
        return articles
