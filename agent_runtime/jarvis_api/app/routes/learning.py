"""
CLE API Routes
Endpoints for accessing learning reports and proposals
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pathlib import Path
import json
import logging

from app.cle.config import REPORTS_DIR, PROPOSALS_DIR
from app.cle.models import ImprovementProposal, ProposalStatus

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/reports")
async def list_learning_reports():
    """List all learning reports"""
    try:
        reports_dir = Path(REPORTS_DIR)
        reports = []
        
        # Find all report files
        for report_file in reports_dir.glob("JARVIS_CLE_REPORT_*.md"):
            # Try to load metadata
            meta_file = report_file.with_suffix(".md.meta.json")
            
            if meta_file.exists():
                with open(meta_file, "r") as f:
                    metadata = json.load(f)
                    reports.append(metadata)
            else:
                # Fallback: parse filename
                report_id = report_file.stem.replace("JARVIS_CLE_REPORT_", "")
                reports.append({
                    "id": report_id,
                    "report_path": str(report_file),
                    "status": "completed"
                })
        
        # Sort by ID (newest first)
        reports.sort(key=lambda x: x["id"], reverse=True)
        
        return {"reports": reports}
        
    except Exception as e:
        logger.error(f"[CLE API] Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_learning_report(report_id: str):
    """Get a specific learning report"""
    try:
        reports_dir = Path(REPORTS_DIR)
        report_file = reports_dir / f"JARVIS_CLE_REPORT_{report_id}.md"
        
        if not report_file.exists():
            raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
        
        # Read report content
        with open(report_file, "r") as f:
            content = f.read()
        
        # Try to load metadata
        metadata = {}
        meta_file = report_file.parent / f"JARVIS_CLE_REPORT_{report_id}.md.meta.json"
        if meta_file.exists():
            with open(meta_file, "r") as f:
                metadata = json.load(f)
        
        return {
            "id": report_id,
            "content": content,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CLE API] Error getting report {report_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals")
async def list_proposals(status: str = None):
    """
    List all improvement proposals
    
    Args:
        status: Optional status filter (pending_review, approved, rejected, implemented)
    """
    try:
        proposals_dir = Path(PROPOSALS_DIR)
        proposals = []
        
        for proposal_file in proposals_dir.glob("CLE_PROP_*.json"):
            with open(proposal_file, "r") as f:
                data = json.load(f)
                
                # Filter by status if specified
                if status and data.get("status") != status:
                    continue
                
                proposals.append(data)
        
        # Sort by score (highest first)
        proposals.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return {"proposals": proposals}
        
    except Exception as e:
        logger.error(f"[CLE API] Error listing proposals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get a specific proposal"""
    try:
        proposals_dir = Path(PROPOSALS_DIR)
        proposal_file = proposals_dir / f"{proposal_id}.json"
        
        if not proposal_file.exists():
            raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
        
        with open(proposal_file, "r") as f:
            proposal_data = json.load(f)
        
        return proposal_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CLE API] Error getting proposal {proposal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/proposals/{proposal_id}/review")
async def review_proposal(proposal_id: str, action: str, notes: str = ""):
    """
    Review a proposal (approve/reject)
    
    Args:
        action: "approve" or "reject" (query param)
        notes: Optional review notes (query param)
    """
    try:
        if action not in ["approve", "reject"]:
            raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
        
        proposals_dir = Path(PROPOSALS_DIR)
        proposal_file = proposals_dir / f"{proposal_id}.json"
        
        if not proposal_file.exists():
            raise HTTPException(status_code=404, detail=f"Proposal not found: {proposal_id}")
        
        # Load proposal
        with open(proposal_file, "r") as f:
            proposal_data = json.load(f)
        
        # Update status
        from datetime import datetime
        proposal_data["status"] = "approved" if action == "approve" else "rejected"
        proposal_data["reviewed_at"] = str(datetime.now())
        proposal_data["review_notes"] = notes
        
        # Save updated proposal
        with open(proposal_file, "w") as f:
            json.dump(proposal_data, f, indent=2)
        
        logger.info(f"[CLE API] Proposal {proposal_id} {action}d")
        
        return {
            "success": True,
            "proposal_id": proposal_id,
            "new_status": proposal_data["status"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CLE API] Error reviewing proposal {proposal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats")
async def get_knowledge_stats():
    """Get statistics about CLE knowledge base"""
    try:
        from app.cle.qdrant_manager import CLEQdrantManager
        
        qdrant = CLEQdrantManager()
        counts = qdrant.get_total_knowledge_count()
        
        return {
            "total_items": sum(counts.values()),
            "by_source": counts
        }
        
    except Exception as e:
        logger.error(f"[CLE API] Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
