import asyncio
import os
import sys
# Add app to path
sys.path.append(os.getcwd())

from app.services.kali_runner import kali_runner
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

async def verify():
    print("Starting Nmap Overhaul Verification...")
    
    # Force local execution and disable mock
    kali_runner.host = "localhost"
    kali_runner.mock_mode = False
    
    # 1. Run Action (Mock Mode or Localhost)
    # We use localhost to trigger the script but we need to make sure nmap is installed or mocked.
    # The script handles missing nmap by simulating output.
    
    target = "127.0.0.1"
    action_id = "act_01"
    script_path = "/opt/deco/agent_runtime/scripts/actions/01_network_scan.sh"
    
    # Ensure script exists and is executable
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}")
        return

    os.chmod(script_path, 0o755)

    # Run
    result = await kali_runner.run_action(
        action_id=action_id,
        script_path=script_path,
        target=target,
        tenant_slug="verification"
    )
    
    print("Execution Result:", result)
    
    if result["status"] != "completed":
        print("Execution Failed!")
        return

    # 2. Check Artifacts
    report_path = result["report_path"]
    xml_path = f"{report_path}/scan_raw.xml"
    if os.path.exists(xml_path):
        print(f"XML Artifact Found: {xml_path}")
        with open(xml_path, "r") as f:
            print("XML Content Preview:", f.read()[:200])
    else:
        print("XML Artifact NOT Found!")

    # 3. Check Ingestion (Manual check via logs or API if possible)
    # We can't easily check DB here without connecting to Orchestrator DB.
    # But logs should show "Report ingested into Orchestrator".
    
    print("Verification Complete. Check logs for ingestion success.")

if __name__ == "__main__":
    asyncio.run(verify())
