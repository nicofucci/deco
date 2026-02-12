from fastapi import FastAPI
from logging_config import setup_logging

setup_logging()
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import clients, assets, cases, dashboard, reports, vuln, system, events, playbooks, schedules

app = FastAPI(title="Deco-Gravity Orchestrator API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (MVP approach)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Import models here to ensure they are registered with Base
        from models import remote_agent, activation_code  # noqa
        await conn.run_sync(Base.metadata.create_all)

from routers import clients, assets, vuln, reports, system, events, playbooks, schedules, dashboard, ai_agents, learning, ai_performance_proxy, alerts_proxy, risk_proxy, actions_proxy, jarvis_console_proxy, remote_agents, llm, intelligence_proxy, activation_codes, partners, client_portal

app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(ai_agents.router, prefix="/api/ai/agents", tags=["agents"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(vuln.router, prefix="/api/vuln", tags=["vuln"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(playbooks.router, prefix="/api/playbooks", tags=["playbooks"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(learning.router, prefix="/api/jarvis/auto-learn", tags=["learning"])
app.include_router(ai_performance_proxy.router, prefix="/api/ai/performance", tags=["AI Performance"])
app.include_router(alerts_proxy.router, prefix="/api/alerts", tags=["Alerts Proxy"])
app.include_router(risk_proxy.router, prefix="/api/ai/risk", tags=["Risk Proxy"])
app.include_router(actions_proxy.router, prefix="/api/ai/actions", tags=["Actions Proxy"])
app.include_router(jarvis_console_proxy.router, prefix="/api/ai/jarvis", tags=["Jarvis Console Proxy"])
app.include_router(intelligence_proxy.router, prefix="/api/intelligence", tags=["Intelligence Proxy"])
app.include_router(activation_codes.router, prefix="/api/activation", tags=["activation"])
app.include_router(remote_agents.router, prefix="/api/agents", tags=["remote_agents"])
app.include_router(partners.router, prefix="/api/partners", tags=["partners"])
app.include_router(client_portal.router, prefix="/api/client", tags=["client_portal"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "orchestrator_api"}

@app.get("/api/health")
def api_health_check():
    return {"status": "ok", "service": "orchestrator_api", "detail": "compatibility_mode"}

@app.get("/rag/ping")
def rag_ping():
    return {"status": "disabled", "detail": "RAG pipeline not configured yet"}

@app.get("/metrics")
def metrics():
    return "metrics temporarily disabled"
