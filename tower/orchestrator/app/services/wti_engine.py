
import requests
import feedparser
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.domain import GlobalThreat

logger = logging.getLogger(__name__)

class WTIEngine:
    """
    Web Threat Intelligence Engine (v1)
    Fetches and normalizes threat data from OSINT sources.
    """
    
    SOURCES = {
        "cisa_kev": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        # "nvd_feed": "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.zip", # Simplify for v1
        "exploit_db": "https://www.exploit-db.com/rss.xml",
        "github_advisories": "https://api.github.com/advisories" # Requires token usually, leaving as placeholder
    }

    def __init__(self, db: Session):
        self.db = db

    def fetch_threat_intel(self):
        """
        Main entry point. Iterates sources and saves new threats to DB.
        """
        logger.info("Starting WTI Fetch Cycle...")
        new_events = []
        
        # 1. CISA KEV (JSON)
        try:
            new_events.extend(self._fetch_cisa_kev())
        except Exception as e:
            logger.error(f"Error fetching CISA KEV: {e}")

        # 2. Exploit-DB (RSS)
        try:
            new_events.extend(self._fetch_exploit_db())
        except Exception as e:
            logger.error(f"Error fetching Exploit-DB: {e}")
            
        # 3. Simulate Zero-Day (Test Hook)
        # In a real scenario, this comes from a paid feed or Twitter scraper
        
        count = 0
        for event in new_events:
            if self._save_threat(event):
                count += 1
                
        logger.info(f"WTI Cycle Complete. New threats indexed: {count}")
        return count

    def _fetch_cisa_kev(self):
        """
        Parses CISA Known Exploited Vulnerabilities catalog.
        """
        events = []
        resp = requests.get(self.SOURCES["cisa_kev"], timeout=10)
        if resp.status_code != 200:
            return []
            
        data = resp.json()
        for vul in data.get("vulnerabilities", [])[:50]: # Limit to 50 recent for performance
            events.append({
                "source": "cisa",
                "cve": vul.get("cveID"),
                "title": vul.get("vulnerabilityName"),
                "description": vul.get("shortDescription"),
                "published_at": vul.get("dateAdded"), # String YYYY-MM-DD
                "tags": ["exploit", "kev", "active-exploitation"],
                "exploit_status": "confirmed"
            })
        return events

    def _fetch_exploit_db(self):
        """
        Parses Exploit-DB RSS feed.
        """
        events = []
        # feedparser is needed, might not be installed. 
        # Fallback to simple requests if simple structure, or skip if dep missing.
        # Assuming we can use feedparser or simple regex if needed.
        # For this environment, let's skip complex RSS parsing requiring libs not in standard env unless present.
        # We'll simulate this part if feedparser isn't available.
        try:
            feed = feedparser.parse(self.SOURCES["exploit_db"])
            for entry in feed.entries[:20]:
                events.append({
                    "source": "exploit-db",
                    "cve": "N/A", # ExploitDB often lacks CVE in title
                    "title": entry.title,
                    "description": entry.summary,
                    "published_at": entry.published,
                    "tags": ["exploit", "poc"],
                    "exploit_status": "poc"
                })
        except NameError:
             logger.warning("feedparser not installed, skipping RSS")
        return events

    def _save_threat(self, event):
        """
        Idempotent save. Checks if CVE/Source combo exists.
        """
        # Dedup logic: check if CVE exists from that source
        if event["cve"] != "N/A":
            exists = self.db.query(GlobalThreat).filter(
                GlobalThreat.cve == event["cve"],
                GlobalThreat.source == event["source"]
            ).first()
            if exists:
                return False
        
        # Parse date
        pub_date = datetime.now(timezone.utc) # Default
        if event.get("published_at"):
            try:
                # Basic parsing, can be improved with dateutil
                # CISA format: YYYY-MM-DD
                pub_date = datetime.strptime(event["published_at"], "%Y-%m-%d")
            except:
                pass

        threat = GlobalThreat(
            source=event["source"],
            cve=event["cve"],
            title=event["title"],
            description=event["description"],
            published_at=pub_date,
            tags=event["tags"],
            exploit_status=event["exploit_status"],
            risk_score_base=10.0 if "exploit" in event["tags"] else 5.0
        )
        self.db.add(threat)
        self.db.commit()
        return True

    def inject_simulated_threat(self, threat_data):
        """
        Helper for E2E testing to inject a custom threat.
        """
        return self._save_threat(threat_data)
