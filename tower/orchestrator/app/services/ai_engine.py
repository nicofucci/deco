import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from app.models.domain import Finding, Asset
from app.db.session import SessionLocal
from datetime import datetime

MODEL_PATH = "/app/ai_model.joblib"

class RiskPredictor:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print("[*] AI Model loaded successfully.")
            except Exception as e:
                print(f"[-] Error loading AI model: {e}")
        else:
            print("[*] No AI model found. Need training.")

    def train(self):
        """
        Trains the Isolation Forest model using findings from the database.
        """
        db: Session = SessionLocal()
        try:
            # Fetch data
            findings = db.query(Finding).all()
            if not findings:
                print("[-] No findings to train on.")
                return {"status": "error", "message": "No data"}

            # Preprocess
            data = []
            for f in findings:
                # Feature Engineering
                # We want to detect anomalies in severity/title combinations
                # For MVP, we map severity to int
                severity_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
                
                # Simple features: Severity + Hour of Day (simulated)
                # In real world, we would encode ports, services, etc.
                row = {
                    "severity_score": severity_map.get(f.severity.lower(), 1),
                    # "hour": f.detected_at.hour # If we had real timestamps varying enough
                }
                data.append(row)

            df = pd.DataFrame(data)
            
            if df.empty:
                return {"status": "error", "message": "Empty dataframe"}

            # Train Isolation Forest
            # contamination='auto' -> let model decide outlier proportion
            clf = IsolationForest(random_state=42, contamination=0.1)
            clf.fit(df)

            # Save
            joblib.dump(clf, MODEL_PATH)
            self.model = clf
            print(f"[+] AI Model trained on {len(df)} records.")
            return {"status": "success", "records": len(df)}

        except Exception as e:
            print(f"[-] Training error: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def predict(self, severity: str) -> dict:
        """
        Predicts if a finding is anomalous based on its severity.
        Returns risk_score (0-100) and anomaly (bool).
        """
        if not self.model:
            return {"risk_score": 0, "anomaly": False, "message": "Model not trained"}

        try:
            severity_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            score_val = severity_map.get(severity.lower(), 1)
            
            # Predict expects 2D array
            X = pd.DataFrame([{"severity_score": score_val}])
            
            # -1 for outliers, 1 for inliers
            pred = self.model.predict(X)[0]
            
            # Decision function: lower is more anomalous
            score = self.model.decision_function(X)[0]
            
            # Normalize score to 0-100 risk (approx)
            # decision_function returns negative for outliers. 
            # Let's invert it roughly for a "Risk Score"
            risk_score = 0
            if pred == -1:
                risk_score = 80 + abs(score * 100) # High risk
                risk_score = min(risk_score, 100)
            else:
                risk_score = max(0, 50 - (score * 100)) # Low risk

            return {
                "risk_score": int(risk_score),
                "anomaly": bool(pred == -1),
                "raw_score": float(score)
            }

        except Exception as e:
            print(f"[-] Prediction error: {e}")
            return {"risk_score": 0, "anomaly": False, "error": str(e)}

# Global instance
ai_engine = RiskPredictor()
