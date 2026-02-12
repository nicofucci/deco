from sqlalchemy.orm import Session
from app.risk.risk_model import RiskScore
from app.risk.risk_predictor import RiskPredictor
from app.models.alerts import SystemAlert
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskService:
    def __init__(self, db: Session):
        self.db = db
        self.predictor = RiskPredictor()

    def get_risk_score(self, id: str = None, client_id: str = None, asset_id: str = None, agent_key: str = None):
        query = self.db.query(RiskScore)
        if id:
            query = query.filter(RiskScore.id == id)
        if client_id:
            query = query.filter(RiskScore.client_id == client_id)
        if asset_id:
            query = query.filter(RiskScore.asset_id == asset_id)
        if agent_key:
            query = query.filter(RiskScore.agent_key == agent_key)
            
        return query.first()

    def calculate_and_save_risk(self, entity_type: str, entity_id: str):
        """
        Calculates risk for an entity and saves it.
        entity_type: 'client', 'asset', 'agent', 'global'
        """
        # 1. Gather Data (Alerts, etc.)
        score = self._calculate_base_score(entity_type, entity_id)
        
        # 2. Get History (Mocked for now, or retrieve past scores)
        # In a real system, we would query a history table. 
        # Here we just use the current score and some noise/logic to simulate history for prediction
        # or fetch the previous score to build a tiny history.
        
        current_risk_entry = self.get_risk_score(**{f"{entity_type}_id" if entity_type != 'agent' and entity_type != 'global' else "agent_key" if entity_type == 'agent' else "id": entity_id if entity_type != 'global' else None})
        
        history = []
        if current_risk_entry:
            # Simple simulation: assume previous score was history
            history = [current_risk_entry.score_actual]
        
        history.append(score)
        
        # 3. Predict
        trend = self.predictor.calculate_trend(history)
        risk_24h = self.predictor.predict_future_risk(history, 1) # 1 step = 24h roughly in this abstract model
        risk_72h = self.predictor.predict_future_risk(history, 3)
        risk_7d = self.predictor.predict_future_risk(history, 7)
        
        category = self.predictor.calculate_risk_category(score)
        
        # 4. Save/Update
        if not current_risk_entry:
            if entity_type == 'global':
                 current_risk_entry = RiskScore(id="global", score_actual=score)
                 self.db.add(current_risk_entry)
            else:
                kwargs = {}
                if entity_type == 'client': kwargs['client_id'] = entity_id
                elif entity_type == 'asset': kwargs['asset_id'] = entity_id
                elif entity_type == 'agent': kwargs['agent_key'] = entity_id
                current_risk_entry = RiskScore(**kwargs, score_actual=score)
                self.db.add(current_risk_entry)
        
        current_risk_entry.score_actual = score
        current_risk_entry.trend = trend
        current_risk_entry.risk_24h = risk_24h
        current_risk_entry.risk_72h = risk_72h
        current_risk_entry.risk_7d = risk_7d
        current_risk_entry.category = category
        current_risk_entry.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(current_risk_entry)
        return current_risk_entry

    def _calculate_base_score(self, entity_type: str, entity_id: str) -> float:
        """
        Calculates a base risk score (0-100) based on active alerts.
        """
        base_score = 0.0
        
        # Fetch active alerts
        query = self.db.query(SystemAlert).filter(SystemAlert.status.in_(["new", "acknowledged"]))
        
        if entity_type == 'client':
            query = query.filter(SystemAlert.client_id == entity_id)
        elif entity_type == 'asset':
            query = query.filter(SystemAlert.asset_id == entity_id)
        elif entity_type == 'agent':
            query = query.filter(SystemAlert.agent_key == entity_id)
        # Global includes ALL alerts
            
        alerts = query.all()
        
        for alert in alerts:
            if alert.severity == 'critical':
                base_score += 40
            elif alert.severity == 'high':
                base_score += 20
            elif alert.severity == 'medium':
                base_score += 10
            elif alert.severity == 'low':
                base_score += 2
                
        # Cap at 100
        return min(100.0, base_score)

    def get_all_risks(self, limit: int = 100):
        return self.db.query(RiskScore).limit(limit).all()
