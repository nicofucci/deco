import requests
import logging
from config import ORCHESTRATOR_URL, API_KEY_HEADER
from modules.secure_storage import SecureStorage

logger = logging.getLogger(__name__)

class HTTPClient:
    def __init__(self):
        self.storage = SecureStorage()
        # Prefer stored URL, fallback to default
        self.base_url = self.storage.get("orchestrator_url") or ORCHESTRATOR_URL
        self.session = requests.Session()

    def _get_headers(self):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "DecoAgent/1.0.0"
        }
        
        # Add Client API Key if available (for initial registration)
        api_key = self.storage.get("client_api_key")
        if api_key:
            headers[API_KEY_HEADER] = api_key
            
        # Add Agent Token if available (for subsequent requests)
        token = self.storage.get("agent_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        return headers

    def post(self, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"POST {endpoint} failed: {e}")
            return None

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GET {endpoint} failed: {e}")
            return None
