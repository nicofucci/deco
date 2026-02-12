import requests
import time
import sys

API_URL = "http://localhost:18001"
PARTNER_KEY = "fb59a40cbf50dbc5e71676565f10fe97"
CLIENT_ID = "45a5391a-a4fa-4364-84f0-1aa8c0dab72e"

headers = {
    "X-Partner-API-Key": PARTNER_KEY,
    "Content-Type": "application/json"
}

def log(msg):
    print(f"[TEST] {msg}")

def run_scan():
    log("Triggering Quick Scan...")
    res = requests.post(f"{API_URL}/api/partners/me/clients/{CLIENT_ID}/scan", json={"type": "quick", "target": "127.0.0.1"}, headers=headers)
    if res.status_code != 200:
        log(f"Scan failed: {res.text}")
        sys.exit(1)
    job = res.json()
    log(f"Job started: {job['id']}")
    return job['id']

def wait_for_job(job_id):
    log("Waiting for job completion...")
    for _ in range(30):
        # We don't have a direct job status endpoint for partners easily accessible without finding it,
        # but we can list jobs.
        res = requests.get(f"{API_URL}/api/partners/me/clients/{CLIENT_ID}/jobs", headers=headers)
        jobs = res.json()
        target_job = next((j for j in jobs if j['id'] == job_id), None)
        if target_job:
            status = target_job['status']
            log(f"Job Status: {status}")
            if status in ['done', 'completed', 'error', 'failed']:
                return status
        time.sleep(2)
    return "timeout"

def generate_report(rtype="executive"):
    log(f"Generating {rtype} report...")
    res = requests.post(f"{API_URL}/api/partners/me/clients/{CLIENT_ID}/reports", json={"type": rtype}, headers=headers)
    if res.status_code != 200:
        log(f"Report generation failed: {res.text}")
        sys.exit(1)
    rep = res.json()
    log(f"Report Generated: {rep['id']} | Status: {rep['status']}")
    return rep['id']

def list_reports():
    log("Listing reports...")
    res = requests.get(f"{API_URL}/api/partners/me/clients/{CLIENT_ID}/reports", headers=headers)
    reports = res.json()
    log(f"Found {len(reports)} reports.")
    for r in reports:
        print(f" - {r['type']}: {r['title']} ({r['generated_at']})")
        # Try download the first one
        durl = r['download_url']
        msg = "Download OK"
        try:
             # Fix relative URL if needed
             if not durl.startswith("http"):
                 durl = f"{API_URL}{durl}"
             
             dl_res = requests.get(durl, headers=headers)
             if dl_res.status_code == 200:
                 print(f"   [DOWNLOAD] Success. Content-Type: {dl_res.headers.get('Content-Type')}. Size: {len(dl_res.content)} bytes.")
             else:
                 print(f"   [DOWNLOAD] Failed: {dl_res.status_code}")
                 msg = "Download FAILED"
        except Exception as e:
             print(f"   [DOWNLOAD] Error: {e}")


if __name__ == "__main__":
    job_id = run_scan()
    status = wait_for_job(job_id)
    if status not in ['done', 'completed']:
        log(f"Job failed or timed out: {status}")
        # Proceeding anyway to test report generation on partial data or failure?
        # User said "based on completed Scan Jobs".
        # But let's try.
    
    rep_id = generate_report("executive")
    list_reports()
