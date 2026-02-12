-- Crear tabla de reportes sin afectar tablas existentes
CREATE TABLE IF NOT EXISTS reports (
    id VARCHAR(255) PRIMARY KEY,
    client_id VARCHAR(255) NOT NULL REFERENCES clients(id),
    job_id VARCHAR(255) NULL REFERENCES scan_jobs(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NULL,
    status VARCHAR(50) DEFAULT 'generated',
    summary TEXT NULL,
    file_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_client_id ON reports(client_id);
