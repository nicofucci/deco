"""
CLE Analysis Engine - Phase 4
Gap analysis and improvement proposal generation
"""

import logging
import json
from typing import List, Dict, Optional
from pathlib import Path
import asyncio
from datetime import datetime
import uuid

from app.cle.models import ImprovementProposal, ProposalType, ImpactLevel, EffortLevel, ProposalStatus
from app.cle.config import GAP_ANALYSIS_PROMPT, PROPOSAL_SCORING, PROPOSALS_DIR
from app.services.ollama_client import JarvisOllamaClient
from app.cle.qdrant_manager import CLEQdrantManager
from app.routes.catalog import MOCK_ACTIONS, MOCK_SERVICES

logger = logging.getLogger(__name__)


class GapAnalyzer:
    """Analyzes gaps between current Jarvis capabilities and learned best practices"""
    
    def __init__(
        self,
        ollama_client: Optional[JarvisOllamaClient] = None,
        qdrant_manager: Optional[CLEQdrantManager] = None
    ):
        self.ollama = ollama_client or JarvisOllamaClient()
        self.qdrant = qdrant_manager or CLEQdrantManager()
    
    async def analyze_gaps(self, recent_knowledge_summary: str) -> List[Dict]:
        """
        Analyze gaps and generate improvement recommendations
        
        Args:
            recent_knowledge_summary: Summary of recently learned knowledge
        
        Returns:
            List of gap/improvement dictionaries
        """
        try:
            # Get current Jarvis capabilities
            current_actions_summary = self._summarize_current_actions()
            
            # Build prompt
            prompt = GAP_ANALYSIS_PROMPT.format(
                current_actions=current_actions_summary,
                learned_techniques=recent_knowledge_summary
            )
            
            logger.info("[Gap Analyzer] Analyzing gaps...")
            
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
            
            # Parse JSON
            if "```json" in llm_output:
                llm_output = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                llm_output = llm_output.split("```")[1].split("```")[0].strip()
            
            gaps = json.loads(llm_output)
            
            logger.info(f"[Gap Analyzer] Found {len(gaps)} gaps/improvements")
            return gaps
            
        except Exception as e:
            logger.error(f"[Gap Analyzer] Error analyzing gaps: {e}")
            return []
    
    def _summarize_current_actions(self) -> str:
        """Summarize current Jarvis actions for LLM"""
        summary_lines = []
        for action in MOCK_ACTIONS[:10]:  # Sample first 10
            summary_lines.append(
                f"- {action.name} ({action.category.value}): {action.description}"
            )
        
        return "\n".join(summary_lines)


class ProposalGenerator:
    """Generates improvement proposals based on gap analysis"""
    
    def __init__(self):
        self.proposals_dir = Path(PROPOSALS_DIR)
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_proposal(
        self,
        title: str,
        description: str,
        proposal_type: ProposalType,
        target_file: Optional[str] = None,
        code_diff: Optional[str] = None,
        impact: ImpactLevel = ImpactLevel.MEDIUM,
        effort: EffortLevel = EffortLevel.MEDIUM,
        learned_from: str = "CLE Knowledge Base",
        tags: List[str] = None
    ) -> ImprovementProposal:
        """
        Create an improvement proposal
        
        Returns:
            ImprovementProposal object
        """
        # Generate unique ID
        proposal_id = f"CLE_PROP_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        
        # Calculate priority score
        score = self._calculate_score(impact, effort)
        
        # Create proposal
        proposal = ImprovementProposal(
            id=proposal_id,
            type=proposal_type,
            title=title,
            description=description,
            target_file=target_file,
            code_diff=code_diff,
            impact=impact,
            effort=effort,
            score=score,
            learned_from=learned_from,
            status=ProposalStatus.PENDING_REVIEW,
            tags=tags or []
        )
        
        # Save to file
        self._save_proposal(proposal)
        
        logger.info(f"[Proposal Generator] Created proposal: {proposal_id}")
        return proposal
    
    def _calculate_score(self, impact: ImpactLevel, effort: EffortLevel) -> float:
        """Calculate priority score based on impact and effort"""
        impact_value = PROPOSAL_SCORING[f"impact_{impact.value}"]
        effort_value = PROPOSAL_SCORING[f"effort_{effort.value}"]
        
        # Score = Impact / Effort (higher is better)
        score = impact_value / effort_value
        return round(score * 10, 2)  # Scale to 0-10 range
    
    def _save_proposal(self, proposal: ImprovementProposal):
        """Save proposal to JSON file"""
        try:
            filepath = self.proposals_dir / f"{proposal.id}.json"
            
            with open(filepath, "w") as f:
                json.dump(proposal.dict(), f, indent=2, default=str)
            
            logger.info(f"[Proposal Generator] Saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"[Proposal Generator] Error saving proposal: {e}")
    
    def load_all_proposals(self) -> List[ImprovementProposal]:
        """Load all proposals from disk"""
        proposals = []
        
        try:
            for filepath in self.proposals_dir.glob("CLE_PROP_*.json"):
                with open(filepath, "r") as f:
                    data = json.load(f)
                    proposal = ImprovementProposal(**data)
                    proposals.append(proposal)
        except Exception as e:
            logger.error(f"[Proposal Generator] Error loading proposals: {e}")
        
        return proposals


class AnalysisEngine:
    """Complete analysis engine: gap analysis + proposal generation"""
    
    def __init__(
        self,
        ollama_client: Optional[JarvisOllamaClient] = None,
        qdrant_manager: Optional[CLEQdrantManager] = None
    ):
        self.gap_analyzer = GapAnalyzer(ollama_client, qdrant_manager)
        self.proposal_generator = ProposalGenerator()
    
    async def run_analysis(self, knowledge_summary: str) -> List[ImprovementProposal]:
        """
        Run complete analysis: identify gaps and generate proposals
        
        Args:
            knowledge_summary: Summary of recently learned knowledge
        
        Returns:
            List of generated proposals
        """
        logger.info("[Analysis Engine] Starting analysis...")
        
        # Step 1: Analyze gaps
        gaps = await self.gap_analyzer.analyze_gaps(knowledge_summary)
        
        # Step 2: Generate proposals
        proposals = []
        for gap in gaps:
            try:
                proposal = self._gap_to_proposal(gap)
                proposals.append(proposal)
            except Exception as e:
                logger.error(f"[Analysis Engine] Error converting gap to proposal: {e}")
        
        logger.info(f"[Analysis Engine] Generated {len(proposals)} proposals")
        return proposals
    
    def _gap_to_proposal(self, gap: Dict) -> ImprovementProposal:
        """Convert gap analysis item to improvement proposal"""
        # Parse gap data
        title = gap.get("capability", "Unnamed improvement")
        description = gap.get("why_it_matters", "No description")
        difficulty = gap.get("difficulty", "medium").lower()
        
        # Map to proposal types
        proposal_type = ProposalType.IMPROVE_ACTION  # Default
        if "new" in title.lower() or "add" in title.lower():
            proposal_type = ProposalType.NEW_ACTION
        
        # Map difficulty to effort
        effort_map = {
            "easy": EffortLevel.LOW,
            "low": EffortLevel.LOW,
            "medium": EffortLevel.MEDIUM,
            "hard": EffortLevel.HIGH,
            "high": EffortLevel.HIGH
        }
        effort = effort_map.get(difficulty, EffortLevel.MEDIUM)
        
        # Assume high impact if it's a gap identified by analysis
        impact = ImpactLevel.HIGH
        
        # Generate proposal
        proposal = self.proposal_generator.generate_proposal(
            title=title,
            description=description,
            proposal_type=proposal_type,
            impact=impact,
            effort=effort,
            learned_from="CLE Gap Analysis",
            tags=["gap-analysis", "auto-generated"]
        )
        
        return proposal
