import requests
import json
from datetime import datetime

class SIEMForwarder:
    def __init__(self):
        # In a real app, this would be loaded from DB per client
        self.configs = {} 

    def configure_webhook(self, client_id: str, webhook_url: str):
        self.configs[client_id] = webhook_url
        return True

    def get_config(self, client_id: str):
        return self.configs.get(client_id)

    def forward_event(self, client_id: str, event_type: str, payload: dict):
        url = self.configs.get(client_id)
        if not url:
            return {"status": "skipped", "reason": "no_config"}

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "client_id": client_id,
            "data": payload,
            "source": "Deco-Security-Tower"
        }

        try:
            # Mock sending
            # res = requests.post(url, json=event, timeout=2)
            print(f"[SIEM] Forwarding to {url}: {json.dumps(event)}")
            return {"status": "sent", "destination": url}
        except Exception as e:
            return {"status": "error", "error": str(e)}

siem_service = SIEMForwarder()
