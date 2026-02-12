"""
CLE Reporting - Phase 5
Generate learning cycle reports in Markdown
"""

import logging
from typing import List, Dict
from pathlib import Path
from datetime import datetime

from app.cle.models import ImprovementProposal, LearningReportMetadata, DiscoveryResult
from app.cle.config import REPORTS_DIR
from app.routes.catalog import MOCK_ACTIONS  # Import for action count in reports

logger = logging.getLogger(__name__)


class ReportBuilder:
    """Builds learning cycle reports in Markdown format"""
    
    def __init__(self):
        self.reports_dir = Path(REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        cycle_start: datetime,
        cycle_end: datetime,
        discovery_results: List[DiscoveryResult],
        knowledge_items: Dict[str, List],  # {"articles": [...], "repos": [...], "videos": [...]}
        proposals: List[ImprovementProposal]
    ) -> str:
        """
        Generate a complete learning cycle report
        
        Returns:
            Path to generated report file
        """
        report_id = cycle_end.strftime("%Y%m%d_%H%M")
        
        # Build report content
        content = self._build_report_content(
            cycle_start,
            cycle_end,
            discovery_results,
            knowledge_items,
            proposals
        )
        
        # Save report
        filename = f"JARVIS_CLE_REPORT_{report_id}.md"
        filepath = self.reports_dir / filename
        
        with open(filepath, "w") as f:
            f.write(content)
        
        logger.info(f"[Report Builder] Generated report: {filepath}")
        
        # Save metadata
        self._save_metadata(report_id, cycle_start, cycle_end, knowledge_items, proposals, str(filepath))
        
        return str(filepath)
    
    def _build_report_content(
        self,
        cycle_start: datetime,
        cycle_end: datetime,
        discovery_results: List[DiscoveryResult],
        knowledge_items: Dict[str, List],
        proposals: List[ImprovementProposal]
    ) -> str:
        """Build Markdown report content"""
        
        # Count items
        articles = knowledge_items.get("articles", [])
        repos = knowledge_items.get("github_repos", [])
        videos = knowledge_items.get("youtube_videos", [])
        
        # Group proposals by priority
        high_priority = [p for p in proposals if p.impact.value == "high"]
        medium_priority = [p for p in proposals if p.impact.value == "medium"]
        low_priority = [p for p in proposals if p.impact.value == "low"]
        
        # Build content
        content = f"""# JARVIS CLE Report - {cycle_end.strftime("%Y-%m-%d %H:%M")}

**Cycle Period:** {cycle_start.strftime("%Y-%m-%d %H:%M")} → {cycle_end.strftime("%Y-%m-%d %H:%M")}

---

## 1. Executive Summary

Durante este ciclo de aprendizaje, JARVIS ha explorado **{len(articles)} artículos web**, **{len(repos)} repositorios GitHub** y **{len(videos)} vídeos educativos** en busca de conocimiento de ciberseguridad, hacking ético y pentesting.

**Hallazgos Clave:**
- {len(articles) + len(repos) + len(videos)} fuentes procesadas en total
- {len(proposals)} propuestas de mejora generadas
- {len(high_priority)} propuestas de alto impacto identificadas

**Estado de Propuestas:**
- **Alta prioridad:** {len(high_priority)} propuestas
- **Media prioridad:** {len(medium_priority)} propuestas
- **Baja prioridad:** {len(low_priority)} propuestas

---

## 2. Knowledge Acquired

### Web Articles ({len(articles)})

"""
        
        if articles:
            content += "| Title | Source | Key Concepts |\n"
            content += "|-------|--------|-------------|\n"
            for article in articles[:10]:  # Top 10
                concepts_str = ", ".join(article.concepts[:3])
                content += f"| {article.title[:50]}... | {self._extract_domain(article.source_url)} | {concepts_str} |\n"
        else:
            content += "*No web articles processed this cycle.*\n"
        
        content += f"\n### GitHub Repositories ({len(repos)})\n\n"
        
        if repos:
            content += "| Repo | Stars | Purpose | Potential Use in Jarvis |\n"
            content += "|------|-------|---------|------------------------|\n"
            for repo in repos[:10]:
                # Handle use_cases_jarvis which might be strings or dicts
                if repo.use_cases_jarvis:
                    use_cases_list = []
                    for uc in repo.use_cases_jarvis[:2]:
                        if isinstance(uc, str):
                            use_cases_list.append(uc)
                        elif isinstance(uc, dict):
                            use_cases_list.append(str(uc))
                    use_cases = ", ".join(use_cases_list) if use_cases_list else "TBD"
                else:
                    use_cases = "TBD"
                content += f"| [{repo.repo_name}]({repo.repo_url}) | {repo.stars} ⭐ | {repo.description[:40]}... | {use_cases} |\n"
        else:
            content += "*No GitHub repositories processed this cycle.*\n"
        
        content += f"\n### YouTube Content ({len(videos)})\n\n"
        
        if videos:
            content += "| Video | Channel | Main Insights |\n"
            content += "|-------|---------|---------------|\n"
            for video in videos[:10]:
                content += f"| [{video.title[:40]}...]({video.video_url}) | {video.channel} | {video.summary[:60]}... |\n"
        else:
            content += "*No YouTube videos processed this cycle.*\n"
        
        content += f"""

---

## 3. Improvement Proposals

### High Priority ({len(high_priority)})

"""
        
        if high_priority:
            for i, proposal in enumerate(high_priority, 1):
                content += f"""
#### {i}. [{proposal.id}] {proposal.title}
- **Type:** {proposal.type.value}
- **Impact:** {proposal.impact.value.upper()} | **Effort:** {proposal.effort.value} | **Score:** {proposal.score}
- **Description:** {proposal.description}
- **Learned from:** {proposal.learned_from}

"""
        else:
            content += "*No high-priority proposals this cycle.*\n"
        
        content += f"\n### Medium Priority ({len(medium_priority)})\n\n"
        
        if medium_priority:
            for proposal in medium_priority[:5]:  # Top 5
                content += f"- **[{proposal.id}]** {proposal.title} (Score: {proposal.score})\n"
        else:
            content += "*No medium-priority proposals this cycle.*\n"
        
        content += f"\n### Low Priority ({len(low_priority)})\n\n"
        
        if low_priority:
            for proposal in low_priority[:3]:  # Top 3
                content += f"- **[{proposal.id}]** {proposal.title} (Score: {proposal.score})\n"
        else:
            content += "*No low-priority proposals this cycle.*\n"
        
        content += f"""

---

## 4. JARVIS Self-Assessment

**Strengths:**
- Comprehensive action catalog with {len(MOCK_ACTIONS)} technical actions
- Multi-service architecture supporting business-level operations
- Robust reporting and intelligence gathering capabilities

**Gaps Identified:**
"""
        
        for proposal in high_priority[:3]:
            content += f"- {proposal.title}\n"
        
        content += f"""

**Trending Topics:**
- {self._extract_trending_topics(articles, repos, videos)}

---

## 5. Next Learning Cycle

**Focus Areas:**
- Deep dive into high-priority gaps
- Explore emerging techniques in identified gaps
- Expand knowledge in trending security topics

**Questions to Explore:**
- How can we implement the high-priority improvements safely?
- What are the dependencies for proposed changes?
- Which proposals can be combined for maximum impact?

---

**Report Generated:** {datetime.now().isoformat()}  
**CLE Version:** 1.0
"""
        
        return content
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(str(url)).netloc
        except:
            return "unknown"
    
    def _extract_trending_topics(self, articles, repos, videos) -> str:
        """Extract trending topics from knowledge items"""
        all_tags = []
        
        for item in articles + repos + videos:
            all_tags.extend(item.tags)
        
        # Count frequency
        from collections import Counter
        tag_counts = Counter(all_tags)
        top_tags = tag_counts.most_common(5)
        
        if top_tags:
            return ", ".join([tag for tag, count in top_tags])
        else:
            return "Insufficient data to determine trends"
    
    def _save_metadata(
        self,
        report_id: str,
        cycle_start: datetime,
        cycle_end: datetime,
        knowledge_items: Dict,
        proposals: List[ImprovementProposal],
        report_path: str
    ):
        """Save report metadata"""
        try:
            import json
            
            metadata = LearningReportMetadata(
                id=report_id,
                cycle_start=cycle_start,
                cycle_end=cycle_end,
                sources_explored={
                    "web": len(knowledge_items.get("articles", [])),
                    "github": len(knowledge_items.get("github_repos", [])),
                    "youtube": len(knowledge_items.get("youtube_videos", []))
                },
                concepts_learned=sum(
                    len(item.concepts) for item in 
                    knowledge_items.get("articles", []) + 
                    knowledge_items.get("github_repos", []) + 
                    knowledge_items.get("youtube_videos", [])
                ),
                proposals_generated=len(proposals),
                proposals_breakdown={
                    "high": len([p for p in proposals if p.impact.value == "high"]),
                    "medium": len([p for p in proposals if p.impact.value == "medium"]),
                    "low": len([p for p in proposals if p.impact.value == "low"])
                },
                status="completed",
                report_path=report_path
            )
            
            metadata_path = Path(report_path + ".meta.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata.dict(), f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"[Report Builder] Error saving metadata: {e}")
