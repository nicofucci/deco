from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Boolean, Text, Float, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=True)
    name = Column(String, nullable=False)
    # Mapped to 'contact' in DB
    contact_email = Column(String, nullable=True, name="contact")
    status = Column(String, default="active") # active, suspended
    # region = Column(String, default="us-east-1") 
    # api_key = Column(String, unique=True, nullable=True) 
    agent_api_key = Column(String, unique=True, nullable=True)
    client_panel_api_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # predictive_risk_score added in V2.1
    predictive_risk_score = Column(Integer, default=100)
    
    partner = relationship("Partner", back_populates="clients")
    agents = relationship("Agent", back_populates="client")
    assets = relationship("Asset", back_populates="client")
    network_assets = relationship("NetworkAsset", back_populates="client")
    scan_jobs = relationship("ScanJob", back_populates="client")
    predictive_signals = relationship("PredictiveSignal", back_populates="client", cascade="all, delete-orphan")
    # subscription = relationship("Subscription", back_populates="client", uselist=False, cascade="all, delete-orphan")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), unique=True, nullable=False)
    plan_id = Column(String, default="starter") # starter, pro, enterprise
    status = Column(String, default="active") # active, past_due, canceled
    current_period_end = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # client = relationship("Client", back_populates="subscription")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=True)
    hostname = Column(String, nullable=False)
    status = Column(String, default="offline") # online, offline, busy
    region = Column(String, default="us-east-1")
    local_ip = Column(String, nullable=True)
    primary_cidr = Column(String, nullable=True)
    interfaces = Column(JSON, nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(String, nullable=True)
    os = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    capabilities = Column(JSON, default={}) # xray, wti, autofix, update_v2
    
    client = relationship("Client", back_populates="agents")
    scan_jobs = relationship("ScanJob", back_populates="agent")

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    # agent_id = Column(String, ForeignKey("agents.id"), nullable=True) 
    ip = Column(String, nullable=False, name="ip_address")
    hostname = Column(String, nullable=True)
    type = Column(String, nullable=True)
    criticality = Column(String, nullable=True)
    # tags = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    client = relationship("Client", back_populates="assets")
    findings = relationship("Finding", back_populates="asset", cascade="all, delete-orphan")

class ScanJob(Base):
    __tablename__ = "scan_jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    type = Column(String, nullable=False)  # discovery, ports, services, os_fingerprint
    target = Column(String, nullable=False)  # IP o rango a escanear
    status = Column(String, default="pending")  # pending, running, done, error
    params = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    
    client = relationship("Client", back_populates="scan_jobs")
    agent = relationship("Agent", back_populates="scan_jobs")
    results = relationship("ScanResult", back_populates="job", uselist=False, cascade="all, delete-orphan")

class ScanResult(Base):
    __tablename__ = "scan_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    scan_job_id = Column(String, ForeignKey("scan_jobs.id"), nullable=False)
    raw_data = Column(JSON, nullable=True)
    parsed_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    job = relationship("ScanJob", back_populates="results")

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)
    severity = Column(String, nullable=False) # low, medium, high, critical
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    asset = relationship("Asset", back_populates="findings")

class Partner(Base):
    __tablename__ = "partners"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    status = Column(String, default="active") # active, suspended
    type = Column(String, default="FULL") # DEMO, FULL
    account_mode = Column(String, default="demo") # demo, full (nuevo campo lógico)
    partner_api_key = Column(String, unique=True, nullable=True)
    client_limit = Column(Integer, default=20)
    agent_limit = Column(Integer, default=20)
    client_packages = Column(Integer, default=0)
    agent_packages = Column(Integer, default=0)
    demo_expires_at = Column(DateTime(timezone=True), nullable=True)
    commission_percent = Column(Integer, nullable=False, default=50)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    clients = relationship("Client", back_populates="partner")
    api_keys = relationship("PartnerAPIKey", back_populates="partner")
    earnings = relationship("PartnerEarnings", back_populates="partner")

class PartnerAPIKey(Base):
    __tablename__ = "partner_api_keys"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=False)
    name = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    partner = relationship("Partner", back_populates="api_keys")

class PartnerEarnings(Base):
    __tablename__ = "partner_earnings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    partner_id = Column(String, ForeignKey("partners.id"), nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    period = Column(String, nullable=False) # YYYY-MM
    total_mrr_client = Column(Float, default=0.0)
    commission_rate = Column(Float, default=0.4)
    commission_amount = Column(Float, default=0.0)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    partner = relationship("Partner", back_populates="earnings")
    client = relationship("Client")

class NetworkAsset(Base):
    __tablename__ = "network_assets"

    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    
    ip = Column(String, nullable=False)
    mac = Column(String, nullable=True)
    mac_vendor = Column(String, nullable=True)
    hostname = Column(String, nullable=True)
    
    os_guess = Column(String, nullable=True)
    device_type = Column(String, default="unknown") # pc, mobile, printer, router, iot
    
    # V2 Fields
    status = Column(String, default="new") # new, stable, gone, at_risk
    times_seen = Column(Integer, default=1)
    
    origin_type = Column(String, default="unknown") # lan, local_interface, etc.
    confidence_score = Column(Integer, default=0)
    tags = Column(JSON, default=[])
    
    open_ports = Column(JSON, default=[])
    
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    
    client = relationship("Client", back_populates="network_assets")
    agent = relationship("Agent")
    history = relationship("NetworkAssetHistory", back_populates="asset", cascade="all, delete-orphan")
    # specialized_findings mapped below
    
class NetworkObservation(Base):
    __tablename__ = "network_observations"

    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    sensor_id = Column(String, nullable=True)
    
    ip = Column(String, nullable=True)
    mac = Column(String, nullable=True)
    hostname = Column(String, nullable=True)
    
    source = Column(String, nullable=False)
    raw_data = Column(JSON, nullable=True)
    confidence_delta = Column(Integer, default=0)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)


class NetworkAssetHistory(Base):
    __tablename__ = "network_asset_history"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("network_assets.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now()) # Keep for legacy/dates
    changed_at = Column(DateTime(timezone=True), server_default=func.now()) # New precise timestamp
    reason = Column(String, nullable=True) # Reason for change
    
    status = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    mac = Column(String, nullable=True)
    hostname = Column(String, nullable=True)
    
    asset = relationship("NetworkAsset", back_populates="history")

class NetworkVulnerability(Base):
    __tablename__ = "network_vulnerabilities"

    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    asset_id = Column(String, ForeignKey("network_assets.id"), nullable=False)
    
    cpe = Column(String, nullable=True) # Common Platform Enumeration
    cve = Column(String, nullable=False) # Common Vulnerabilities and Exposures ID
    
    cvss_score = Column(Float, default=0.0)
    severity = Column(String, default="low") # critical, high, medium, low
    
    exploit_available = Column(Boolean, default=False)
    exploit_sources = Column(JSON, default=[]) # ["exploit-db", "metasploit", "github"]
    
    description_short = Column(Text, nullable=True)
    vector_string = Column(String, nullable=True) # CVSS Vector
    
    first_detected = Column(DateTime(timezone=True), server_default=func.now())
    last_detected = Column(DateTime(timezone=True), server_default=func.now())
    
    asset = relationship("NetworkAsset", back_populates="vulnerabilities")

class SpecializedFinding(Base):
    __tablename__ = "specialized_findings"

    id = Column(String, primary_key=True, default=generate_uuid)
    asset_id = Column(String, ForeignKey("network_assets.id"), nullable=False)
    job_type = Column(String, nullable=False) 
    data = Column(JSON, nullable=True)
    severity = Column(String, default="info")
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

    asset = relationship("NetworkAsset", back_populates="specialized_findings")

# Update NetworkAsset relationship
NetworkAsset.vulnerabilities = relationship("NetworkVulnerability", back_populates="asset", cascade="all, delete-orphan")
NetworkAsset.specialized_findings = relationship("SpecializedFinding", back_populates="asset", cascade="all, delete-orphan")

class PredictiveSignal(Base):
    __tablename__ = "predictive_signals"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    asset_id = Column(String, ForeignKey("network_assets.id"), nullable=True)
    
    signal_type = Column(String, nullable=False)
    severity = Column(String, nullable=False) # low, medium, high, critical
    description = Column(Text, nullable=True)
    score_delta = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    client = relationship("Client", back_populates="predictive_signals")
    asset = relationship("NetworkAsset")


class AutofixPlaybook(Base):
    __tablename__ = "autofix_playbooks"

    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    asset_id = Column(String, ForeignKey("network_assets.id"), nullable=False)
    vulnerability_id = Column(String, ForeignKey("network_vulnerabilities.id"), nullable=True)
    
    title = Column(String, nullable=False)
    playbook_json = Column(JSON, nullable=False) # {actions: [ {cmd: "...", desc: "..."} ]}
    risk_level = Column(String, default="medium") # low, medium, high
    status = Column(String, default="draft") # draft, approved, rejected, executed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    client = relationship("Client") # back_populates optional if not strictly needed
    asset = relationship("NetworkAsset")
    vulnerability = relationship("NetworkVulnerability")


class AutofixExecution(Base):
    __tablename__ = "autofix_executions"

    id = Column(String, primary_key=True, default=generate_uuid)
    playbook_id = Column(String, ForeignKey("autofix_playbooks.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True) # Who executed it
    
    execution_mode = Column(String, default="manual") # manual, semi_auto, full_auto
    status = Column(String, default="pending") # pending, running, success, failed
    logs = Column(Text, nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    playbook = relationship("AutofixPlaybook")



# ========================
# LEGACY REPORTS
# ========================
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("scan_jobs.id"), nullable=True)
    type = Column(String, nullable=False) # executive, technical
    title = Column(String, nullable=True)
    status = Column(String, default="generated")
    summary = Column(Text, nullable=True)
    file_path = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    agent_id = Column(String, nullable=True)
    
    client = relationship("Client")
    job = relationship("ScanJob")

# ========================
# SNAPSHOT REPORTING
# ========================

class ReportSnapshot(Base):
    __tablename__ = "report_snapshots"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("scan_jobs.id"), nullable=True) # Optional link to specific scan
    
    kind = Column(String, default="executive") # executive, technical
    status = Column(String, default="generating") # generating, ready, error
    
    # Metadata for History
    assets_count = Column(Integer, default=0)
    findings_count = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    
    # Storage
    pdf_path = Column(String, nullable=True) # Relative path in storage
    pdf_url = Column(String, nullable=True) # Public/Download URL if applicable
    
    filter_date_from = Column(DateTime(timezone=True), nullable=True)
    filter_date_to = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    client = relationship("Client")
    job = relationship("ScanJob")
    findings = relationship("ReportSnapshotFinding", back_populates="snapshot", cascade="all, delete-orphan")


class ReportSnapshotFinding(Base):
    __tablename__ = "report_snapshot_findings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    snapshot_id = Column(String, ForeignKey("report_snapshots.id"), nullable=False, index=True)
    
    # Deduplication Key elements
    asset_id = Column(String, nullable=True) # Link to asset if it exists
    ip = Column(String, nullable=True)
    hostname = Column(String, nullable=True)
    
    # Finding Details (Frozen)
    title = Column(String, nullable=False)
    severity = Column(String, default="low")
    cve = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    
    snapshot = relationship("ReportSnapshot", back_populates="findings")


class GlobalThreat(Base):
    __tablename__ = "global_threat_feed"

    id = Column(String, primary_key=True, default=generate_uuid)
    source = Column(String, nullable=False) # cisa, nvd, exploit-db
    cve = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    tags = Column(JSON, default=[]) # ["zero-day", "exploit", "ransomware"]
    exploit_status = Column(String, default="unknown") # confirmed, poc, under_analysis
    risk_score_base = Column(Float, default=0.0) # CVSS or normalized score
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)

class ClientThreatMatch(Base):
    __tablename__ = "client_threat_matches"

    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    threat_id = Column(String, ForeignKey("global_threat_feed.id"), nullable=False)
    asset_id = Column(String, ForeignKey("network_assets.id"), nullable=True) # Optional match to specific asset
    
    match_reason = Column(String, nullable=False) # asset-service, os-match, existing-vulnerability
    risk_level = Column(String, default="high") # critical, high, medium, low
    status = Column(String, default="active") # active, mitigated, dismissed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client")
    threat = relationship("GlobalThreat")
    asset = relationship("NetworkAsset")


class AgentVersion(Base):
    __tablename__ = "agent_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    version = Column(String, nullable=False, unique=True) # 1.1.0
    platform = Column(String, default="windows") # windows, linux
    
    download_url = Column(String, nullable=False)
    checksum_sha256 = Column(String, nullable=False)
    
    release_date = Column(DateTime(timezone=True), server_default=func.now())
    is_forced = Column(Boolean, default=False)
    min_orchestrator_version = Column(String, nullable=True)
    changelog = Column(Text, nullable=True)
    
    tier = Column(String, default="stable") # stable, beta

    def __repr__(self):
        return f"<AgentVersion {self.version} ({self.platform})>"


class AgentStatus(Base):
    __tablename__ = "agent_status"

    agent_id = Column(String, ForeignKey("agents.id"), primary_key=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    # partner_id = Column(String, ForeignKey("partners.id"), nullable=True) # Optional denormalization

    hostname = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    platform = Column(String, default="windows")
    version = Column(String, nullable=True)

    last_seen = Column(DateTime(timezone=True), nullable=True)
    last_update_check = Column(DateTime(timezone=True), nullable=True)
    last_update_status = Column(String, default="unknown") # success, failed, outdated

    health_state = Column(String, default="healthy") # healthy, warning, critical
    error_reason = Column(Text, nullable=True)

    jobs_executed_24h = Column(Integer, default=0)
    jobs_failed_24h = Column(Integer, default=0)

    cpu_usage = Column(Float, nullable=True)
    ram_usage = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agent = relationship("Agent")
    client = relationship("Client")


class FleetAlert(Base):
    __tablename__ = "fleet_alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    
    alert_type = Column(String, nullable=False) # agent_offline, outdated, update_failed
    severity = Column(String, default="medium") # low, medium, high, critical
    message = Column(Text, nullable=False)
    
    resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("Agent")
    client = relationship("Client")

