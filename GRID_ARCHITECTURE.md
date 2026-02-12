# Deco-Security Global Grid - Architecture

## Overview
Deco-Security Global Grid is a distributed security platform consisting of a central Orchestrator, multiple management consoles, and a fleet of universal agents installed on client infrastructure.

## Components

### 1. Tower (Central Infrastructure)
- **Orchestrator API**: FastAPI backend handling agent registration, heartbeats, job distribution, and data persistence.
- **Database**: PostgreSQL storing Clients, Agents, Assets, Findings, and Jobs.
- **Consoles**:
    - **Master Grid**: Super-admin control.
    - **Partner Console**: Partner management of clients.
    - **Client Console**: End-user dashboard for security monitoring.

### 2. Universal Agent (`/opt/deco/agent_universal`)
- **Core**: Python-based service running on Windows and Linux.
- **Communication**: HTTPS (JSON) to Orchestrator.
- **Identity**: Authenticated via Client API Key.
- **Installers**:
    - **Windows**: PyInstaller-compiled EXE running as a Windows Service (NSSM/sc).
    - **Linux**: DEB package / Shell script installing a systemd service.
    - **Updates**: Auto-update capability via `updater.py` checking `agent_version.json`.
- **Capabilities**:
    - **Heartbeat**: Periodic status and network info reporting.
    - **Network Discovery**: Auto-detection of local subnets.
    - **Job Execution**: Running scans (Discovery, Port Scan) on demand.

### 3. Connectivity
- **Cloudflare Tunnel**: Exposes internal services securely to `*.deco-security.com`.
- **Download Portal**: Serves agent installers to end-users.

## Data Flow
1. **Registration**: Agent installs -> User inputs API Key -> Agent registers with Orchestrator -> Receives Agent ID.
2. **Heartbeat**: Agent sends `local_ip`, `primary_cidr`, status -> Orchestrator updates DB.
3. **Job Launch**: User selects Agent in Console -> "Scan Agent Network" uses `primary_cidr` -> Job created.
4. **Execution**: Agent picks up Job -> Executes -> Sends Results -> Orchestrator processes findings.
