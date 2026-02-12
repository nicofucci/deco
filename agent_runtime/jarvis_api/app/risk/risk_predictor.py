import numpy as np
from typing import List, Dict

class RiskPredictor:
    """
    Handles predictive analysis for risk scores using statistical methods.
    """

    @staticmethod
    def calculate_trend(history: List[float]) -> str:
        """
        Determines trend based on recent history.
        """
        if not history or len(history) < 2:
            return "flat"
        
        # Simple linear regression slope
        x = np.arange(len(history))
        y = np.array(history)
        slope, _ = np.polyfit(x, y, 1)
        
        if slope > 0.5:
            return "up"
        elif slope < -0.5:
            return "down"
        return "flat"

    @staticmethod
    def predict_future_risk(history: List[float], horizon_steps: int) -> float:
        """
        Predicts risk score for a future horizon using Exponential Smoothing.
        """
        if not history:
            return 0.0
            
        if len(history) < 3:
            return history[-1] # Not enough data, return last known
            
        # Simple Exponential Smoothing
        alpha = 0.3
        forecast = history[0]
        for i in range(1, len(history)):
            forecast = alpha * history[i] + (1 - alpha) * forecast
            
        # Project linear trend for horizon
        trend_factor = 0
        trend = RiskPredictor.calculate_trend(history)
        if trend == "up":
            trend_factor = 0.5 * horizon_steps
        elif trend == "down":
            trend_factor = -0.2 * horizon_steps
            
        predicted = forecast + trend_factor
        return max(0.0, min(100.0, predicted))

    @staticmethod
    def calculate_risk_category(score: float) -> str:
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 30:
            return "medium"
        return "low"
