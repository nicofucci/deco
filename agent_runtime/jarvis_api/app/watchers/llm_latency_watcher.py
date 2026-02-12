import asyncio
import logging
import time
import httpx
from app.database import SessionLocal
from app.services.alerts_service import create_alert_from_event, get_open_alert_by_source, update_alert_status

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://ollama:11434"
# Use the correct model
MODEL_TO_CHECK = "llama3.1:8b-instruct-q4_K_M"

# Global state for strikes
failure_count = 0
MAX_FAILURES = 3

async def start_llm_latency_watcher():
    """
    Monitor LLM Latency.
    Runs every 5 minutes.
    """
    logger.info("Starting LLM Latency Watcher...")
    while True:
        try:
            await check_llm_latency()
        except Exception as e:
            logger.error(f"Error in LLM Latency Watcher: {e}")
        
        await asyncio.sleep(300)

async def check_llm_latency():
    global failure_count
    db = SessionLocal()
    try:
        success = False
        error_msg = ""
        latency = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            start_time = time.time()
            try:
                # 1. Check Tags first (fastest)
                resp_tags = await client.get(f"{OLLAMA_URL}/api/tags")
                if resp_tags.status_code != 200:
                    raise Exception(f"Ollama API unreachable (Status {resp_tags.status_code})")

                # 2. Check Generation (deep check)
                payload = {
                    "model": MODEL_TO_CHECK,
                    "prompt": "ping",
                    "stream": False
                }
                resp = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
                end_time = time.time()
                latency = (end_time - start_time) * 1000 # ms
                
                if resp.status_code != 200:
                    # Try to parse error
                    try:
                        err_json = resp.json()
                        error_msg = err_json.get("error", resp.text)
                    except:
                        error_msg = f"Status {resp.status_code}"
                    raise Exception(f"Ollama Error: {error_msg}")
                
                success = True
                failure_count = 0 # Reset on success

            except Exception as e:
                error_msg = str(e)
                success = False
                failure_count += 1
                logger.warning(f"LLM Check Failed ({failure_count}/{MAX_FAILURES}): {error_msg}")

        # --- Logic for Alerts ---
        
        existing_alert = get_open_alert_by_source(db, source="llm_monitor", title="LLM Error")
        
        if success:
            # Auto-resolve if open alert exists
            if existing_alert:
                logger.info("LLM Recovered. Resolving alert.")
                update_alert_status(db, existing_alert.id, "resolved")
                
            # Check for high latency warning (only if successful)
            if latency > 10000:
                # Deduplicate high latency alerts too
                latency_alert = get_open_alert_by_source(db, source="llm_monitor", title="High LLM Latency")
                if not latency_alert:
                    create_alert_from_event(
                        db,
                        event_type="LLM",
                        severity="warning",
                        source="llm_monitor",
                        title="High LLM Latency",
                        description=f"LLM response time was {latency:.2f}ms (Threshold: 10000ms)",
                        metric_value=latency,
                        threshold=10000,
                        metadata={"latency_ms": latency}
                    )
        else:
            # Failure case
            if failure_count >= MAX_FAILURES:
                if not existing_alert:
                    logger.error("LLM Down. Creating Alert.")
                    create_alert_from_event(
                        db,
                        event_type="LLM",
                        severity="high",
                        source="llm_monitor",
                        title="LLM Error",
                        description=f"LLM failed {failure_count} consecutive checks. Last error: {error_msg}",
                        metadata={"error": error_msg, "failures": failure_count}
                    )
                else:
                    logger.info("LLM Down, but alert already exists.")

    finally:
        db.close()
