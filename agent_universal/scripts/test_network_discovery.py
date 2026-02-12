import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from services.network_discovery import NetworkDiscovery

def main():
    print("Testing NetworkDiscovery...")
    discovery = NetworkDiscovery()
    info = discovery.get_network_info()
    print(json.dumps(info, indent=2))

if __name__ == "__main__":
    main()
