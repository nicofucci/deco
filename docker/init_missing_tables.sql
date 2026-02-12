-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR PRIMARY KEY,
    client_id VARCHAR REFERENCES clients(id),
    name VARCHAR,
    hostname VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'offline',
    region VARCHAR DEFAULT 'us-east-1',
    local_ip VARCHAR,
    primary_cidr VARCHAR,
    interfaces JSON,
    last_seen_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version VARCHAR,
    os VARCHAR,
    ip VARCHAR
);

-- Create scan_jobs table
CREATE TABLE IF NOT EXISTS scan_jobs (
    id VARCHAR PRIMARY KEY,
    client_id VARCHAR REFERENCES clients(id),
    agent_id VARCHAR REFERENCES agents(id),
    type VARCHAR NOT NULL,
    target VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE
);

-- Create scan_results table
CREATE TABLE IF NOT EXISTS scan_results (
    id VARCHAR PRIMARY KEY,
    scan_job_id VARCHAR REFERENCES scan_jobs(id),
    raw_data JSON,
    parsed_summary JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create findings table
CREATE TABLE IF NOT EXISTS findings (
    id VARCHAR PRIMARY KEY,
    client_id VARCHAR REFERENCES clients(id),
    asset_id VARCHAR REFERENCES assets(id),
    severity VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    recommendation TEXT,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create partners table
CREATE TABLE IF NOT EXISTS partners (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'active',
    commission_percent INTEGER DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create partner_api_keys table
CREATE TABLE IF NOT EXISTS partner_api_keys (
    id VARCHAR PRIMARY KEY,
    partner_id VARCHAR REFERENCES partners(id),
    name VARCHAR,
    api_key VARCHAR UNIQUE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE
);

-- Create partner_earnings table
CREATE TABLE IF NOT EXISTS partner_earnings (
    id VARCHAR PRIMARY KEY,
    partner_id VARCHAR REFERENCES partners(id),
    client_id VARCHAR REFERENCES clients(id),
    period VARCHAR NOT NULL,
    total_mrr_client FLOAT DEFAULT 0.0,
    commission_rate FLOAT DEFAULT 0.4,
    commission_amount FLOAT DEFAULT 0.0,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
