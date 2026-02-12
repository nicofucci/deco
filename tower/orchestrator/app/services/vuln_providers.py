from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
import logging
import time
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class VulnProvider(ABC):
    @abstractmethod
    def fetch_cves_for_cpe(self, cpe: str) -> List[Dict[str, Any]]:
        """
        Fetches vulnerabilities for a given CPE.
        Returns a list of dicts with keys: cve, severity, score, desc, exploit.
        """
        pass

class NvdVulnProvider(VulnProvider):
    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NVD_API_KEY")
        self.last_call = 0
        
    def fetch_cves_for_cpe(self, cpe: str) -> List[Dict[str, Any]]:
        """
        Queries NVD for a specific CPE Name.
        """
        # Rate Limiting
        # NVD: 50 req/30s (w/ key), 5 req/30s (w/o key).
        # Safe bet: 0.6s delay key, 6s delay without.
        now = time.time()
        delay = 0.6 if self.api_key else 6.0
        elapsed = now - self.last_call
        if elapsed < delay:
            sleep_time = delay - elapsed
            logger.info(f"[NVD] Rate inhibiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
            
        self.last_call = time.time()
        
        headers = {}
        if self.api_key:
            headers["apiKey"] = self.api_key
            
        params = {
            "cpeName": cpe,
            "resultsPerPage": 50 # Limit to avoid timeout on broad CPEs like Windows 10
        }
        
        try:
            logger.info(f"[NVD] Fetching CVEs for {cpe}...")
            resp = requests.get(self.BASE_URL, params=params, headers=headers, timeout=10)
            
            logger.info(f"[NVD] Response: {resp.status_code} - len={len(resp.text)}")
            if len(resp.text) < 500:
                logger.info(f"[NVD] Body snippet: {resp.text}")

            if resp.status_code == 404:
                return []
            if resp.status_code != 200:
                logger.error(f"[NVD] API Error: {resp.status_code} - {resp.text}")
                return []
                
            data = resp.json()
            return self._normalize_nvd_response(data)
            
        except Exception as e:
            logger.error(f"[NVD] Request failed: {e}")
            return []

    def _normalize_nvd_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings = []
        vulnerabilities = data.get("vulnerabilities", [])
        
        for item in vulnerabilities:
            cve_item = item.get("cve", {})
            cve_id = cve_item.get("id")
            
            # Metrics (CVSS 3.1 > 3.0 > 2.0)
            metrics = cve_item.get("metrics", {})
            cvss_data = None
            
            if "cvssMetricV31" in metrics:
                cvss_data = metrics["cvssMetricV31"][0].get("cvssData")
            elif "cvssMetricV30" in metrics:
                cvss_data = metrics["cvssMetricV30"][0].get("cvssData")
            elif "cvssMetricV2" in metrics:
                cvss_data = metrics["cvssMetricV2"][0].get("cvssData")
                
            score = cvss_data.get("baseScore", 0.0) if cvss_data else 0.0
            severity = cvss_data.get("baseSeverity", "UNKNOWN") if cvss_data else "UNKNOWN"
            
            # Description
            descriptions = cve_item.get("descriptions", [])
            desc_text = "No description"
            for d in descriptions:
                if d.get("lang") == "en":
                    desc_text = d.get("value")
                    break
            
            # Weaknesses (CWE) - optional enrichment
            
            # Exploitability (Check existing exploit status - Simplified/Mock for now)
            # NVD doesn't provide "exploit available" flag directly, usually implies references.
            # We will default to False here, as the prompt said exploit DB is future.
            # However, prompt said "VulnCheck u otra... opcional".
            # Mapping high severity as "potentially exploitable" for demo purposes? 
            # No, keep it clean.
            exploit_available = False
            
            findings.append({
                "cve": cve_id,
                "severity": severity,
                "score": score,
                "desc": desc_text,
                "exploit": exploit_available,
                "cpe": "" # Unknown which CPE match exactly if query was broad, but here we query by specific CPE
            })
            
        return findings
