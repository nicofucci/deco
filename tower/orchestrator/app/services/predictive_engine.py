from sqlalchemy.orm import Session
from app.models.domain import Client, NetworkAsset, NetworkVulnerability, NetworkAssetHistory, PredictiveSignal
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("DecoOrchestrator.PredictiveEngine")
logger.setLevel(logging.INFO)

class PredictiveReport:
    def __init__(self, score: int, signals: List[Dict]):
        self.score = score
        self.signals = signals

class PredictiveEngine:
    def __init__(self, db: Session):
        self.db = db
        
    def analyze_client(self, client_id: str) -> PredictiveReport:
        logger.info(f"Analyzing client {client_id} for predictive risks...")
        
        # Cleanup old signals (optional, or we keep history. Let's clear for 'current state' check)
        # Actually usually signals are events. But risk score is current.
        # Let's delete old signals > 30 days? Or just generate new ones appearing now.
        # For this task, we will generate "current view" signals.
        # Strategy: Analyze -> Generate Signals -> Save to DB -> Calculate Score -> Update Client.
        
        # 1. Gather Data
        assets = self.db.query(NetworkAsset).filter(NetworkAsset.client_id == client_id).all()
        vulns = self.db.query(NetworkVulnerability).filter(NetworkVulnerability.client_id == client_id).all()
        
        now = datetime.now(timezone.utc)
        
        generated_signals = []
        
        # 2. Heuristics
        
        # H1: Surge of New Devices
        # Check assets created in last 24h
        new_assets = [a for a in assets if a.first_seen >= now - timedelta(hours=24)]
        if len(new_assets) >= 3:
            generated_signals.append({
                "type": "new_device_surge",
                "severity": "medium",
                "description": f"Se detectaron {len(new_assets)} dispositivos nuevos en las últimas 24h. Actividad inusual.",
                "score_delta": -10
            })
        elif len(new_assets) > 0:
             generated_signals.append({
                "type": "new_device_pattern",
                "severity": "low",
                "description": f"Aparición de {len(new_assets)} dispositivos recientes.",
                "score_delta": -2 * len(new_assets)
            })

        # H2: Vulnerability Trend
        # Check high/critical vulns found recently
        recent_vulns = [v for v in vulns if v.first_detected >= now - timedelta(hours=48) and v.severity in ["high", "critical"]]
        if len(recent_vulns) > 2:
             generated_signals.append({
                "type": "critical_vuln_spike",
                "severity": "high",
                "description": f"Aumento rápido de vulnerabilidades críticas ({len(recent_vulns)} en 48h). Posible campaña de escaneo activo.",
                "score_delta": -20
            })
            
        # H3: Instability (Gone/New flip-flop or just many "Gone")
        gone_assets = [a for a in assets if a.status == "gone"]
        if len(gone_assets) > len(assets) * 0.3 and len(assets) > 5:
            generated_signals.append({
                "type": "network_instability",
                "severity": "medium",
                "description": "Más del 30% de la red ha desaparecido. Posible fallo de segmento o sabotaje.",
                "score_delta": -15
            })
            
        # H4: Specific Critical Asset Risk
        for asset in assets:
            if asset.device_type in ["router", "server"] and asset.status == "at_risk":
                 generated_signals.append({
                    "type": "critical_asset_risk",
                    "severity": "high",
                    "description": f"Activo crítico ({asset.hostname or asset.ip}) marcado en riesgo.",
                    "score_delta": -10,
                    "asset_id": asset.id
                })

        # 3. Calculate Score
        base_score = 100
        total_penalty = sum([abs(s.get("score_delta", 0)) for s in generated_signals])
        final_score = max(0, base_score - total_penalty)
        
        # 4. Persist
        # Clear previous signals (simplification for V1 dashboard)
        # In a real system we might append, but for "Current Risk" report, we replace.
        self.db.query(PredictiveSignal).filter(PredictiveSignal.client_id == client_id).delete()
        
        saved_signals = []
        for s in generated_signals:
            sig = PredictiveSignal(
                client_id=client_id,
                asset_id=s.get("asset_id"),
                signal_type=s["type"],
                severity=s["severity"],
                description=s["description"],
                score_delta=s.get("score_delta", 0)
            )
            self.db.add(sig)
            # Create a clean dict for return
            saved_signals.append(s)
            
        # Update Client Score
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if client:
            client.predictive_risk_score = final_score
            
        self.db.commit()
        
        logger.info(f"Analysis complete. Score: {final_score}. Signals: {len(generated_signals)}")
        return PredictiveReport(final_score, saved_signals)
