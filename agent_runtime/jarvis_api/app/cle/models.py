"""
CLE Data Models
Pydantic models for CLE knowledge items and proposals
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    """Type of knowledge source"""
    WEB = "web"
    GITHUB = "github"
    YOUTUBE = "youtube"


class ProposalType(str, Enum):
    """Type of improvement proposal"""
    NEW_ACTION = "new_action"
    IMPROVE_ACTION = "improve_action"
    NEW_SERVICE = "new_service"
    IMPROVE_SERVICE = "improve_service"
    SECURITY_UPDATE = "security_update"
    DOCUMENTATION = "documentation"


class ImpactLevel(str, Enum):
    """Impact level of a proposal"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EffortLevel(str, Enum):
    """Effort required for implementation"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProposalStatus(str, Enum):
    """Status of an improvement proposal"""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


# ============================================================================
# KNOWLEDGE ITEMS
# ============================================================================

class KnowledgeArticle(BaseModel):
    """Web article or documentation"""
    id: str
    source_type: Literal[SourceType.WEB] = SourceType.WEB
    source_url: HttpUrl
    title: str
    content: str
    summary: str
    concepts: List[str] = []
    use_cases_jarvis: List[str] = []
    tags: List[str] = []
    relevance_score: float = Field(ge=0.0, le=1.0)
    discovered_at: datetime = Field(default_factory=datetime.now)
    embedding: Optional[List[float]] = None


class KnowledgeGitHub(BaseModel):
    """GitHub repository"""
    id: str
    source_type: Literal[SourceType.GITHUB] = SourceType.GITHUB
    repo_url: HttpUrl
    repo_name: str
    description: str
    stars: int
    language: Optional[str] = None
    topics: List[str] = []
    readme_content: str
    summary: str
    concepts: List[str] = []
    use_cases_jarvis: List[str] = []
    tags: List[str] = []
    relevance_score: float = Field(ge=0.0, le=1.0)
    discovered_at: datetime = Field(default_factory=datetime.now)
    embedding: Optional[List[float]] = None


class KnowledgeYouTube(BaseModel):
    """YouTube video transcript"""
    id: str
    source_type: Literal[SourceType.YOUTUBE] = SourceType.YOUTUBE
    video_url: HttpUrl
    video_id: str
    title: str
    channel: str
    duration: int  # seconds
    transcript: str
    summary: str
    concepts: List[str] = []
    use_cases_jarvis: List[str] = []
    tags: List[str] = []
    relevance_score: float = Field(ge=0.0, le=1.0)
    discovered_at: datetime = Field(default_factory=datetime.now)
    embedding: Optional[List[float]] = None


# ============================================================================
# IMPROVEMENT PROPOSALS
# ============================================================================

class ImprovementProposal(BaseModel):
    """Improvement proposal for Jarvis"""
    id: str
    type: ProposalType
    title: str
    description: str
    target_file: Optional[str] = None  # File to modify (if applicable)
    code_diff: Optional[str] = None  # Proposed code changes
    new_file_content: Optional[str] = None  # For new files
    impact: ImpactLevel
    effort: EffortLevel
    score: float  # Calculated priority score
    learned_from: str  # Source URL/reference
    status: ProposalStatus = ProposalStatus.PENDING_REVIEW
    created_at: datetime = Field(default_factory=datetime.now)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    tags: List[str] = []


# ============================================================================
# LEARNING REPORTS
# ============================================================================

class LearningReportMetadata(BaseModel):
    """Metadata for a learning cycle report"""
    id: str  # Format: YYYYMMDD_HHMM
    cycle_start: datetime
    cycle_end: datetime
    sources_explored: dict  # {"web": 15, "github": 8, "youtube": 3}
    concepts_learned: int
    proposals_generated: int
    proposals_breakdown: dict  # {"high": 2, "medium": 5, "low": 3}
    status: Literal["running", "completed", "failed"]
    report_path: str  # Path to .md file


# ============================================================================
# DISCOVERY RESULTS
# ============================================================================

class DiscoveryResult(BaseModel):
    """Result from a discovery operation"""
    source_type: SourceType
    items_found: int
    items_processed: int
    items_failed: int
    duration_seconds: float
    errors: List[str] = []
