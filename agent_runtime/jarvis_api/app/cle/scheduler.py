"""
CLE Scheduler - Phase 5
Automates learning cycles every 12 hours
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, List

from app.cle.discovery.web_crawler import WebCrawler
from app.cle.discovery.github_explorer import GitHubExplorer, get_github_token_from_env
from app.cle.discovery.youtube_processor import YouTubeProcessor, get_youtube_api_key_from_env
from app.cle.ingestion.pipeline import IngestionPipeline
from app.cle.analysis.engine import AnalysisEngine
from app.cle.reporting.builder import ReportBuilder
from app.cle.config import MAX_WEB_ARTICLES_PER_CYCLE, MAX_GITHUB_REPOS_PER_CYCLE

logger = logging.getLogger(__name__)


class LearningCycleOrchestrator:
    """Orchestrates a complete learning cycle"""
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        youtube_api_key: Optional[str] = None
    ):
        # Get tokens from environment if not provided
        if not github_token:
            github_token = get_github_token_from_env()
        if not youtube_api_key:
            youtube_api_key = get_youtube_api_key_from_env()
        
        # Initialize components
        self.web_crawler = WebCrawler()
        self.github_explorer = GitHubExplorer(access_token=github_token)
        self.youtube_processor = YouTubeProcessor(api_key=youtube_api_key)
        self.ingestion_pipeline = IngestionPipeline()
        self.analysis_engine = AnalysisEngine()
        self.report_builder = ReportBuilder()
        
        logger.info("[CLE Orchestrator] Initialized")
    
    async def run_learning_cycle(
        self,
        web_urls: Optional[List[str]] = None,
        github_topics: Optional[List[str]] = None,
        youtube_urls: Optional[List[str]] = None
    ) -> str:
        """
        Run a complete learning cycle
        
        Args:
            web_urls: URLs to crawl (optional)
            github_topics: Topics to search on GitHub (optional)
            youtube_urls: YouTube videos to process (optional)
        
        Returns:
            Path to generated report
        """
        cycle_start = datetime.now()
        logger.info(f"[CLE] === STARTING LEARNING CYCLE at {cycle_start} ===")
        
        try:
            # Phase 1: Discovery
            logger.info("[CLE] Phase 1/5: Discovery")
            discovery_results = await self._run_discovery(web_urls, github_topics, youtube_urls)
            
            # Phase 2: Ingestion
            logger.info("[CLE] Phase 2/5: Ingestion")
            ingestion_results = await self._run_ingestion(discovery_results)
            
            # Phase 3: Analysis
            logger.info("[CLE] Phase 3/5: Analysis")
            proposals = await self._run_analysis(ingestion_results)
            
            # Phase 4: Reporting
            logger.info("[CLE] Phase 4/5: Reporting")
            cycle_end = datetime.now()
            report_path = self._generate_report(
                cycle_start,
                cycle_end,
                discovery_results,
                ingestion_results,
                proposals
            )
            
            logger.info(f"[CLE] === CYCLE COMPLETE === Duration: {(cycle_end - cycle_start).total_seconds()}s")
            logger.info(f"[CLE] Report generated: {report_path}")
            
            return report_path
            
        except Exception as e:
            logger.error(f"[CLE] Learning cycle failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _run_discovery(
        self,
        web_urls: Optional[List[str]],
        github_topics: Optional[List[str]],
        youtube_urls: Optional[List[str]]
    ) -> dict:
        """Run discovery phase"""
        results = {
            "articles": [],
            "github_repos": [],
            "youtube_videos": [],
            "discovery_results": []
        }
        
        # Web crawling
        if web_urls:
            logger.info(f"[Discovery] Crawling {len(web_urls)} URLs")
            for url in web_urls[:MAX_WEB_ARTICLES_PER_CYCLE]:
                try:
                    article = self.web_crawler.crawl_url(url)
                    if article:
                        results["articles"].append(article)
                except Exception as e:
                    logger.error(f"[Discovery] Error crawling {url}: {e}")
        
        # GitHub exploration
        logger.info("[Discovery] Exploring GitHub repositories")
        try:
            repos = self.github_explorer.search_repositories(
                topics=github_topics,
                max_results=MAX_GITHUB_REPOS_PER_CYCLE
            )
            results["github_repos"] = repos
        except Exception as e:
            logger.error(f"[Discovery] GitHub error: {e}")
        
        # YouTube processing
        if youtube_urls:
            logger.info(f"[Discovery] Processing {len(youtube_urls)} YouTube videos")
            for url in youtube_urls:
                try:
                    video = self.youtube_processor.process_video(url)
                    if video:
                        results["youtube_videos"].append(video)
                except Exception as e:
                    logger.error(f"[Discovery] Error processing {url}: {e}")
        
        total = len(results["articles"]) + len(results["github_repos"]) + len(results["youtube_videos"])
        logger.info(f"[Discovery] Discovered {total} items total")
        
        return results
    
    async def _run_ingestion(self, discovery_results: dict) -> dict:
        """Run ingestion phase"""
        ingestion_results = await self.ingestion_pipeline.process_batch(
            articles=discovery_results["articles"],
            repos=discovery_results["github_repos"],
            videos=discovery_results["youtube_videos"]
        )
        
        logger.info(f"[Ingestion] Processed: {ingestion_results}")
        
        # Return original items (now with summaries and embeddings)
        return discovery_results
    
    async def _run_analysis(self, ingestion_results: dict) -> list:
        """Run analysis phase"""
        # Build knowledge summary for analysis
        knowledge_summary = self._build_knowledge_summary(ingestion_results)
        
        # Run gap analysis and generate proposals
        proposals = await self.analysis_engine.run_analysis(knowledge_summary)
        
        logger.info(f"[Analysis] Generated {len(proposals)} proposals")
        
        return proposals
    
    def _generate_report(
        self,
        cycle_start: datetime,
        cycle_end: datetime,
        discovery_results: dict,
        knowledge_items: dict,
        proposals: list
    ) -> str:
        """Generate final report"""
        report_path = self.report_builder.generate_report(
            cycle_start=cycle_start,
            cycle_end=cycle_end,
            discovery_results=[],  # Discovery results would be populated if we tracked them
            knowledge_items=knowledge_items,
            proposals=proposals
        )
        
        return report_path
    
    def _build_knowledge_summary(self, knowledge_items: dict) -> str:
        """Build a text summary of learned knowledge for analysis"""
        summary_lines = []
        
        # Summarize articles
        for article in knowledge_items.get("articles", [])[:5]:
            summary_lines.append(f"- **{article.title}**: {article.summary}")
            if article.concepts:
                summary_lines.append(f"  Concepts: {', '.join(article.concepts[:5])}")
        
        # Summarize repos
        for repo in knowledge_items.get("github_repos", [])[:5]:
            summary_lines.append(f"- **{repo.repo_name}**: {repo.summary}")
            if repo.use_cases_jarvis:
                # Handle both strings and dicts in use_cases
                use_cases_strs = []
                for uc in repo.use_cases_jarvis[:3]:
                    if isinstance(uc, str):
                        use_cases_strs.append(uc)
                    elif isinstance(uc, dict):
                        use_cases_strs.append(str(uc))
                if use_cases_strs:
                    summary_lines.append(f"  Use cases: {', '.join(use_cases_strs)}")
        
        # Summarize videos
        for video in knowledge_items.get("youtube_videos", [])[:5]:
            summary_lines.append(f"- **{video.title}** ({video.channel}): {video.summary}")
        
        return "\n".join(summary_lines)


# Standalone function for scheduled execution
async def run_scheduled_learning_cycle():
    """Run a learning cycle with default sources (for scheduling)"""
    logger.info("[CLE Scheduler] Starting scheduled learning cycle")
    
    orchestrator = LearningCycleOrchestrator()
    
    # Default sources (customize as needed)
    web_urls = [
        "https://owasp.org/www-project-top-ten/",
        "https://www.kali.org/docs/",
        "https://portswigger.net/web-security",
    ]
    
    github_topics = ["penetration-testing", "security-tools"]
    youtube_urls = []  # Optional: add educational video URLs
    
    try:
        report_path = await orchestrator.run_learning_cycle(
            web_urls=web_urls,
            github_topics=github_topics,
            youtube_urls=youtube_urls
        )
        logger.info(f"[CLE Scheduler] Cycle completed successfully: {report_path}")
        return report_path
    except Exception as e:
        logger.error(f"[CLE Scheduler] Cycle failed: {e}")
        raise
