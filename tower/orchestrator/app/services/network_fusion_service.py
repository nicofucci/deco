import logging
import uuid
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.domain import NetworkAsset, NetworkObservation
from app.schemas.contracts import NetworkObservationSchema

logger = logging.getLogger("orchestrator")

# === DEVICE CLASSIFIER LOGIC (Embedded) ===
class FusionClassifier:
    def classify(self, observations: List[Dict]) -> Dict:
        result = {
            "device_type": "unknown",
            "os_guess": "unknown",
            "confidence_tags": set(),
            "display_name": "",
            "vendor": "",
            "score_accum": 0
        }
        
        mdns_names = []
        ssdp_server = ""
        
        # 1. Accumulate Evidence & Base Score
        for obs in observations:
            src = obs.get("source", "")
            
            # Weights
            if "mdns" in src: result["score_accum"] += 30
            elif "ssdp" in src: result["score_accum"] += 25
            elif "banner" in src: result["score_accum"] += 20
            elif "oui" in src: result["score_accum"] += 10
            elif "arp" in src or "ping" in src: result["score_accum"] += 10
            
            # Extract Metadata
            if "vendor" in obs and obs.get("vendor") and obs.get("vendor") != "Unknown": 
                result["vendor"] = obs["vendor"]
            
            if "names" in obs: mdns_names.extend(obs["names"])
            if "hostname" in obs and obs["hostname"]: mdns_names.append(obs["hostname"])
            
            if "server" in obs: ssdp_server = obs["server"]
            
            # Headers from banner
            if "headers" in obs:
                 h = obs["headers"]
                 if isinstance(h, dict) and h.get("server"):
                     result["confidence_tags"].add(f"http:{h.get('server')}")

        # 2. Heuristics
        
        # mDNS
        for n in mdns_names:
            n_lower = n.lower()
            if not result["display_name"]: result["display_name"] = n # Pick first
            
            if "_airplay" in n_lower or "_raop" in n_lower:
                result["device_type"] = "media_player"
                result["os_guess"] = "tvos_or_ios"
                result["confidence_tags"].add("apple_airplay")
            elif "_googlecast" in n_lower:
                result["device_type"] = "media_player"
                result["os_guess"] = "android_tv"
                result["confidence_tags"].add("chromecast")
            elif "_printer" in n_lower or "_ipp" in n_lower:
                result["device_type"] = "printer"
        
        # SSDP
        if ssdp_server:
            s_lower = ssdp_server.lower()
            if "sonos" in s_lower:
                result["device_type"] = "speaker"
                result["confidence_tags"].add("sonos")
            elif "linux" in s_lower and "upnp" in s_lower:
                 result["confidence_tags"].add("upnp_linux")

        # Vendor Fallbacks
        v_lower = (result["vendor"] or "").lower()
        if result["device_type"] == "unknown" and v_lower:
            if "apple" in v_lower:
                result["confidence_tags"].add("apple_device")
            elif "synology" in v_lower or "qnap" in v_lower:
                result["device_type"] = "nas"
            elif "hikvision" in v_lower:
                result["device_type"] = "camera"
            elif any(x in v_lower for x in ["epson", "hp", "brother", "canon"]):
                result["device_type"] = "printer"
                
        # Confidence Cap
        result["confidence_score"] = min(100, result["score_accum"])
        
        return result

classifier = FusionClassifier()

def fuse_observations(client_id: str, observations: List[NetworkObservationSchema], db: Session):
    # Group by potential asset key (prefer MAC, fallback IP)
    
    # 1. Persist Raw & Grouping
    grouped_obs = {} # Key (mac or ip) -> List[dicts]
    
    for obs in observations:
        raw_dict = obs.dict()
        
        # Persist
        db_obs = NetworkObservation(
            id=str(uuid.uuid4()),
            client_id=client_id,
            sensor_id="default", 
            ip=obs.ip,
            mac=obs.mac,
            hostname=obs.hostname,
            source=obs.source,
            confidence_delta=obs.confidence_delta,
            raw_data=raw_dict,
            processed=True,
            timestamp=datetime.utcnow()
        )
        db.add(db_obs)
        
        # Grouping Key
        key = obs.mac if obs.mac else obs.ip
        if key:
            if key not in grouped_obs: grouped_obs[key] = []
            grouped_obs[key].append(raw_dict)
            
    # 2. Process Groups (Assets)
    for key, obs_list in grouped_obs.items():
        # Find Asset
        target_asset = None
        # Try MAC first
        sample_mac = next((o.get("mac") for o in obs_list if o.get("mac")), None)
        sample_ip = next((o.get("ip") for o in obs_list if o.get("ip")), None)
        
        if sample_mac:
            target_asset = db.query(NetworkAsset).filter(
                NetworkAsset.client_id == client_id,
                NetworkAsset.mac == sample_mac
            ).first()
        
        if not target_asset and sample_ip:
             target_asset = db.query(NetworkAsset).filter(
                NetworkAsset.client_id == client_id,
                NetworkAsset.ip == sample_ip
            ).first()
            
        # Run Classifier
        classification = classifier.classify(obs_list)
        
        # Determine Origin
        origin_type = "lan"
        tags = list(classification["confidence_tags"])
        
        if sample_ip:
             if sample_ip.startswith("172."):
                 parts = sample_ip.split(".")
                 if len(parts) == 4 and 16 <= int(parts[1]) <= 31:
                     origin_type = "local_interface"
                     tags.append("docker")
             elif sample_ip.startswith("127."): origin_type = "loopback"
             elif sample_ip.startswith("169.254"): origin_type = "link_local"
             elif not (sample_ip.startswith("10.") or sample_ip.startswith("192.")): origin_type = "wan"

        if not target_asset:
            target_asset = NetworkAsset(
                id=str(uuid.uuid4()),
                client_id=client_id,
                ip=sample_ip or "0.0.0.0",
                mac=sample_mac,
                hostname=classification["display_name"] or "",
                first_seen=datetime.utcnow(),
                status="new",
                origin_type=origin_type,
                confidence_score=classification["confidence_score"],
                mac_vendor=classification["vendor"],
                device_type=classification["device_type"],
                os_guess=classification["os_guess"],
                tags=tags,
                times_seen=1
            )
            db.add(target_asset)
        else:
            # Update fields
            target_asset.last_seen = datetime.utcnow()
            target_asset.times_seen += 1
            
            if classification["display_name"]:
                target_asset.hostname = classification["display_name"]
            
            if sample_mac and not target_asset.mac:
                target_asset.mac = sample_mac
                
            if classification["vendor"]:
                 target_asset.mac_vendor = classification["vendor"]
                 
            # Max Confidence
            target_asset.confidence_score = max(target_asset.confidence_score or 0, classification["confidence_score"])
            
            if classification["device_type"] != "unknown":
                 target_asset.device_type = classification["device_type"]
                 
            if classification["os_guess"] != "unknown":
                 target_asset.os_guess = classification["os_guess"]
                 
            # Merge Tags
            existing_tags = set(target_asset.tags) if target_asset.tags else set()
            existing_tags.update(tags)
            target_asset.tags = list(existing_tags)
            
            if target_asset.origin_type == "unknown":
                target_asset.origin_type = origin_type

    try:
        db.commit()
    except Exception as e:
        logger.error(f"Fusion Commit Error: {e}")
        db.rollback()
