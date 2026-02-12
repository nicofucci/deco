import random

class ThreatIntelService:
    def get_ip_reputation(self, ip_address: str):
        """
        Simulates fetching IP reputation from an external provider (e.g., VirusTotal, AbuseIPDB).
        """
        # Mock logic based on IP octets to be deterministic but varied
        last_octet = int(ip_address.split('.')[-1])
        
        if last_octet % 10 == 0:
            risk_score = 90
            verdict = "malicious"
            tags = ["botnet", "brute-force"]
        elif last_octet % 5 == 0:
            risk_score = 60
            verdict = "suspicious"
            tags = ["scanner"]
        else:
            risk_score = 5
            verdict = "clean"
            tags = []

        return {
            "ip": ip_address,
            "risk_score": risk_score, # 0-100
            "verdict": verdict,
            "tags": tags,
            "provider": "DecoIntel Global DB",
            "last_seen": "2025-12-01T12:00:00Z"
        }

threat_intel_service = ThreatIntelService()
