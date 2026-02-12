from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import cases, dashboard
from app.database import engine, Base

app = FastAPI(title="Jarvis API Minimal (Migration Check)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router, prefix="/cases", tags=["Cases"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"status": "minimal_mode"}
