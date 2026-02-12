import time
import sys
import traceback
from .config import config
from .http_client import HTTPClient
from .scanner import Scanner
from .updater import Updater

def main():
    print("🛡️ Deco-Security Agent Starting...")
    
    if not config.client_api_key:
        print("[!] Error: CLIENT_API_KEY not set.")
        sys.exit(1)

    client = HTTPClient()
    scanner = Scanner()

    # 1. Registration
    if not config.agent_id:
        if not client.register():
            print("[!] Registration failed. Retrying in 10s...")
            time.sleep(10)
            sys.exit(1) # Exit to let service restart
    else:
        print(f"[*] Agent ID loaded: {config.agent_id}")

    updater = Updater()
    AGENT_VERSION = "3.0.0"

    # 2. Main Loop
    print(f"[*] Entering Heartbeat Loop... (Version: {AGENT_VERSION})")
    while True:
        try:
            # Update Check
            # Force platform='windows' for ThinkPad context simulation
            update_meta = updater.check_for_update(AGENT_VERSION, platform="windows")
            if update_meta:
                 print("[!] Update Available! Applying...")
                 if updater.perform_update(update_meta):
                     print("[*] Update applied (simulation). Restarting agent loop...")
                     # In real windows, we exited. Here we loop/restart.
                     
            # Heartbeat
            hb_response = client.send_heartbeat()
            
            if hb_response and "pending_jobs" in hb_response:
                job_ids = hb_response["pending_jobs"]
                if job_ids:
                    print(f"[*] Received {len(job_ids)} jobs: {job_ids}")
                    
                    for job_id in job_ids:
                        # Fetch Job Details
                        job = client.get_job(job_id)
                        if job:
                            print(f"[*] Executing Job {job_id}: {job['type']} -> {job['target']}")
                            
                            # Execute Scan
                            result_data = scanner.scan(job['target'], job['type'])
                            
                            # Upload Result
                            client.upload_result(job_id, result_data)
                        else:
                            print(f"[-] Failed to fetch job {job_id}")

            time.sleep(config.heartbeat_interval)

        except KeyboardInterrupt:
            print("\n[!] Stopping Agent.")
            break
        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    main()
