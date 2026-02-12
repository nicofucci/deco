from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, JSON, Text, Integer
from sqlalchemy.sql import func
from app.models.chat import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    country = Column(String)
    sector = Column(String)
    contact = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"))
    hostname = Column(String, nullable=False)
    ip_address = Column(String)
    type = Column(String)
    criticality = Column(String, default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class JarvisScanReport(Base):
    __tablename__ = "jarvis_scan_reports"
    __table_args__ = {'extend_existing': True}
    id = Column(String, primary_key=True, default=generate_uuid)
    scan_id = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=True)
    resumen_tecnico = Column(Text)
    riesgos_principales = Column(JSON)
    recomendaciones = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VulnScan(Base):
    __tablename__ = "vuln_scans"
    id = Column(String, primary_key=True, default=generate_uuid)
    target = Column(String, nullable=False)
    scan_type = Column(String)
    status = Column(String, default="pending")
    profile = Column(String)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
