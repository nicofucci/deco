export interface Client {
    id: string;
    name: string;
    email: string;
    api_key: string;
    plan_id: string;
    region: string;
}

export interface Asset {
    id: string;
    ip: string;
    hostname?: string;
    open_ports?: number[];
    last_scan_at?: string;
}

export interface Finding {
    id: string;
    title: string;
    severity: "critical" | "high" | "medium" | "low" | "info";
    description: string;
    asset_id: string;
    asset_ip?: string;
    cve_id?: string;
    status: string;
    created_at: string;
}

export interface ScanJob {
    id: string;
    client_id: string;
    agent_id: string;
    target: string;
    status: string;
    created_at: string;
    completed_at?: string;
}

export interface ScanResult {
    id: string;
    job_id: string;
    data: any;
    created_at: string;
}

export interface Agent {
    id: string;
    hostname: string;
    status: string;
    local_ip?: string;
    primary_cidr?: string;
    interfaces?: any[];
    last_seen_at?: string;
}
