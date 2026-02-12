import logging
import subprocess
import re
from typing import List, Dict, Any

logger = logging.getLogger("ndr_sensor")

class GatewayScanner:
    def scan_gateway_snmp(self, gateway_ip: str) -> List[Dict[str, Any]]:
        observations = []
        logger.info(f"Scanning Gateway {gateway_ip} via SNMP...")
        
        # 1. ARP Table (ipNetToMediaPhysAddress)
        # OID: 1.3.6.1.2.1.4.22.1.2
        try:
            cmd = ["snmpwalk", "-v2c", "-c", "public", "-Ot", "-OQ", gateway_ip, "1.3.6.1.2.1.4.22.1.2"]
            # -Ot: Print Time Ticks in raw format (no) - assume standard. 
            # -OQ: Quick print (var = value).
            # -On: numerical OID
            
            output = subprocess.check_output(cmd, text=True, timeout=5)
            
            # Output format example with -OQ:
            # ipNetToMediaPhysAddress.10.192.168.100.105 = 72:34:56:78:90:ab
            
            for line in output.splitlines():
                if "=" in line:
                    left, mac_raw = line.split("=", 1)
                    mac = mac_raw.strip().replace(" ", ":").replace('"', '')
                    
                    # Extract IP from OID suffix
                    # ipNetToMediaPhysAddress.<ifIndex>.<IP1>.<IP2>.<IP3>.<IP4>
                    parts = left.strip().split(".")
                    if len(parts) >= 4:
                        ip_parts = parts[-4:]
                        ip = ".".join(ip_parts)
                        
                        if len(mac) >= 12: # Valid-ish MAC
                            observations.append({
                                "ip": ip,
                                "mac": mac,
                                "source": "ndr_gateway_snmp_arp",
                                "confidence_delta": 60, # High confidence, router knows best
                                "raw_text": f"Gateway SNMP: {ip} -> {mac}"
                            })

        except subprocess.CalledProcessError:
            logger.debug(f"SNMP failed on {gateway_ip} (End of MIB or Timeout)")
        except FileNotFoundError:
            logger.error("snmpwalk not found")
        except Exception as e:
            logger.error(f"Gateway Scan Error: {e}")
            
        return observations

    def scan_gateway_upnp(self, gateway_ip: str) -> List[Dict[str, Any]]:
        # Placeholder for UPnP if needed. For now SNMP is "The One Step".
        return []
