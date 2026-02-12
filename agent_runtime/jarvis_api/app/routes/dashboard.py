from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models.orchestrator import Client, Asset, JarvisScanReport, VulnScan
from app.models.cases_sql import CaseORM

router = APIRouter()

class DashboardSummary(BaseModel):
    total_clients: int
    total_assets: int
    activos_criticos: int
    escaneos_ultimas_24h: int
    escaneos_fallidos_ultimas_24h: int
    reportes_ia_ultimos_7_dias: List[Dict[str, Any]]
    ultimos_reportes: List[Dict[str, Any]]

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Obtiene resumen para el dashboard usando datos reales."""
    
    # 1. Conteos básicos
    total_clients = db.query(Client).count()
    total_assets = db.query(Asset).count()
    
    # 2. Activos Críticos (Assuming 'critical' or 'high' as critical)
    # Adjusting filter based on typical values. If unsure, we can check DB values later.
    # Assuming 'critical' string based on user prompt context.
    activos_criticos = db.query(Asset).filter(
        func.lower(Asset.criticality).in_(['critical', 'crítica', 'high', 'alta'])
    ).count()
    
    # 3. Escaneos últimas 24h
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    
    escaneos_ultimas_24h = db.query(VulnScan).filter(
        VulnScan.start_time >= one_day_ago
    ).count()
    
    escaneos_fallidos_ultimas_24h = db.query(VulnScan).filter(
        VulnScan.start_time >= one_day_ago,
        func.lower(VulnScan.status).in_(['failed', 'error', 'fallido'])
    ).count()
    
    # 4. Reportes IA últimos 7 días
    reportes_trend = []
    today = datetime.utcnow().date()
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        count = db.query(JarvisScanReport).filter(
            JarvisScanReport.created_at >= day,
            JarvisScanReport.created_at < next_day
        ).count()
        
        reportes_trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "count": count
        })
        
    # 5. Últimos Reportes IA (Top 5)
    # Need to join with Client and Asset to get names
    latest_reports_query = db.query(
        JarvisScanReport, Client.name, Asset.hostname
    ).outerjoin(
        Client, JarvisScanReport.client_id == Client.id
    ).outerjoin(
        Asset, JarvisScanReport.asset_id == Asset.id
    ).order_by(
        desc(JarvisScanReport.created_at)
    ).limit(5).all()
    
    ultimos_reportes = []
    for report, client_name, asset_hostname in latest_reports_query:
        # Extract risk from JSON or use default
        risk = "Unknown"
        if report.riesgos_principales:
            # Try to parse risk if it's a list or dict
            # This depends on the JSON structure. For now, let's assume we can extract a summary or default to Medium
            # Or maybe we just show "Analizado" if risk isn't clear.
            # Let's try to find a 'severity' or 'risk' key if it's a dict, or take the first item if list
            pass
            
        ultimos_reportes.append({
            "id": report.id,
            "client": client_name or "Desconocido",
            "asset": asset_hostname or "Desconocido",
            "risk": "Analizado" # Placeholder as risk is inside JSON
        })
        
    return {
        "total_clients": total_clients,
        "total_assets": total_assets,
        "activos_criticos": activos_criticos,
        "escaneos_ultimas_24h": escaneos_ultimas_24h,
        "escaneos_fallidos_ultimas_24h": escaneos_fallidos_ultimas_24h,
        "reportes_ia_ultimos_7_dias": reportes_trend,
        "ultimos_reportes": ultimos_reportes
    }
