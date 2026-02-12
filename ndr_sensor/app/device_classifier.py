import logging

logger = logging.getLogger("ndr_sensor")

class DeviceClassifier:
    def classify(self, observations: list, fused_ip: str) -> dict:
        """
        Input: list of observations (fused by IP/MAC context beforehand or raw list related to this IP)
        Output: dict with device_type, os_guess, tags, confidence, display_name
        """
        
        result = {
            "device_type": "unknown",
            "os_guess": "unknown",
            "model": "unknown",
            "display_name": "",
            "confidence": 0,
            "tags": set(),
            "sources": set()
        }
        
        # Aggregate data
        mdns_names = []
        ssdp_server = ""
        mac_vendor = ""
        http_server = ""
        
        for obs in observations:
            src = obs.get("source", "")
            result["sources"].add(src)
            
            # Parse specific evidence
            if src == "mdns":
                # Assuming raw_data or evidence field has details
                if "names" in obs: mdns_names.extend(obs["names"])
                if "hostname" in obs: 
                     result["display_name"] = obs["hostname"]
                     mdns_names.append(obs["hostname"])
            
            if src == "ssdp":
                if "server" in obs: ssdp_server = obs["server"]
                
            if src == "oui":
                if "vendor" in obs: mac_vendor = obs["vendor"]
                
            if src == "banner_http":
                # check headers
                pass

        # === RULES ENGINE ===
        
        # 1. mDNS Rules
        for n in mdns_names:
            n_lower = n.lower()
            if "_airplay" in n_lower or "_raop" in n_lower:
                result["device_type"] = "media_player"
                result["os_guess"] = "tvos_or_ios"
                result["tags"].add("apple")
                result["tags"].add("airplay")
                result["confidence"] = 80
                
            if "_googlecast" in n_lower:
                result["device_type"] = "media_player"
                result["os_guess"] = "android_tv"
                result["tags"].add("chromecast")
                result["confidence"] = 90
            
            if "_printer" in n_lower or "_ipp" in n_lower:
                result["device_type"] = "printer"
                result["confidence"] = 80

        # 2. SSDP Rules
        if ssdp_server:
            s_lower = ssdp_server.lower()
            if "linux" in s_lower and "upnp" in s_lower and "av" in s_lower:
                 # Broad checks
                 pass
            if "sonos" in s_lower:
                result["device_type"] = "speaker"
                result["tags"].add("sonos")
                result["confidence"] = 90

        # 3. Vendor Rules (Fallback)
        if result["device_type"] == "unknown" and mac_vendor:
            v_lower = mac_vendor.lower()
            if "apple" in v_lower:
                result["tags"].add("apple_device")
                # Could be mac, iphone, etc. Hard to say without more info.
            elif "synology" in v_lower or "qnap" in v_lower:
                result["device_type"] = "nas"
                result["confidence"] = 70
            elif "hikvision" in v_lower:
                result["device_type"] = "camera"
                result["confidence"] = 80
            elif "epson" in v_lower or "hp" in v_lower or "brother" in v_lower:
                # Strong hint for printer
                result["device_type"] = "printer" # potential
                result["confidence"] = 50

        # Final Cleanup
        if not result["display_name"] and mac_vendor:
            # fallback name
            pass 
            
        result["tags"] = list(result["tags"])
        result["sources"] = list(result["sources"])
        
        return result
