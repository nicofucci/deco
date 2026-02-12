from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.models.chat import Base

class AIAgentVersion(Base):
    __tablename__ = "ai_agent_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_key = Column(String, nullable=False, index=True)
    version_label = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIAgentBenchmark(Base):
    __tablename__ = "ai_agent_benchmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_key = Column(String, nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("ai_agent_versions.id"), nullable=False)
    test_type = Column(String, default="benchmark") # smoke, benchmark
    input_profile = Column(JSON, nullable=True)
    success = Column(Boolean, default=False)
    latency_ms = Column(Float, nullable=False)
    cpu_cost = Column(Float, nullable=True)
    memory_cost = Column(Float, nullable=True)
    score_qualitative = Column(Float, nullable=True) # 0-100
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
