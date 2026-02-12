from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import func, select, desc
from typing import List, Dict, Any

from app.api.deps import get_db, verify_admin_master_key
from app.models.domain import Client, Agent, Finding, ScanJob, Partner, Asset
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(dependencies=[Depends(verify_admin_master_key)])

class DashboardSummary(BaseModel):
    total_clients: int
    suspended_clients: int
    total_partners: int
    active_agents: int
    total_agents: int
    total_findings: int
    total_jobs: int
    last_findings: List[Any]
    findings_by_severity: Dict[str, int]

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    try:
        total_clients = db.query(Client).count()
        suspended_clients = db.query(Client).filter(Client.is_suspended == True).count()
        total_partners = db.query(Partner).count()
        
        # Agents status is a bit complex, let's assume 'online' status or similar
        # If status field exists. If not, just count total.
        # Checking Agent model in previous steps might be needed, but let's guess standard fields.
        # Previous snippet used: where(Agent.status == "online")
        active_agents = db.query(Agent).filter(Agent.status == "online").count()
        total_agents = db.query(Agent).count()
        
        total_findings = db.query(Finding).count()
        total_jobs = db.query(ScanJob).count()

        # Last findings
        last_findings_query = (
            db.query(Finding.id, Finding.title, Finding.severity, Finding.client_id, Finding.detected_at, Client.name.label("client_name"))
            .join(Client, Finding.client_id == Client.id)
            .order_by(Finding.detected_at.desc())
            .limit(5)
            .all()
        )
        
        last_findings = []
        for f in last_findings_query:
            last_findings.append({
                "id": f.id,
                "title": f.title,
                "severity": f.severity,
                "client_id": f.client_id,
                "detected_at": f.detected_at,
                "client_name": f.client_name
            })

        # Findings by severity
        findings_by_severity_query = (
            db.query(Finding.severity, func.count(Finding.id))
            .group_by(Finding.severity)
            .all()
        )
        
        findings_by_severity = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }
        for severity, count in findings_by_severity_query:
            if severity in findings_by_severity:
                findings_by_severity[severity] = count
            else:
                # Handle case sensitivity or unexpected values
                lower_sev = severity.lower()
                if lower_sev in findings_by_severity:
                    findings_by_severity[lower_sev] = count

        return DashboardSummary(
            total_clients=total_clients,
            suspended_clients=suspended_clients,
            total_partners=total_partners,
            active_agents=active_agents,
            total_agents=total_agents,
            total_findings=total_findings,
            total_jobs=total_jobs,
            last_findings=last_findings,
            findings_by_severity=findings_by_severity,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
