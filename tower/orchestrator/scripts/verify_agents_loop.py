import sys
import os

# Set up path to import app modules
sys.path.append('/opt/deco/tower/orchestrator')

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.domain import Base, Partner, Client, Agent

# Database Connection (Adjust URL if needed, assuming default from environment or standard for this user)
# User info says user is 'leoslo', user_rules say nothing about DB bounds, but files suggest project structure.
# I will guess the DB URL based on standard project config, or check env vars. 
# For safety, I'll search for the DB URL in a configuration file first, but let's try a standard one.
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/deco"

import sys
import os

# Set up path to import app modules
# We need to add the parent directory of 'app' to sys.path
sys.path.append('/opt/deco/tower/orchestrator')

from app.db.session import SessionLocal
from app.models.domain import Base, Partner, Client, Agent
from sqlalchemy import func

def verify_partner_agents():
    db = SessionLocal()
    try:
        print("--- VERIFICACIÓN DE ESTADO DE BASE DE DATOS ---")
        partners = db.query(Partner).all()
        for p in partners:
            print(f"\nPartner: {p.name} (ID: {p.id})")
            print(f"  - Account Mode: {getattr(p, 'account_mode', 'N/A')}")
            print(f"  - API Key: {p.partner_api_key}")
            print(f"  - Agent Limit: {p.agent_limit}")
            
            clients = db.query(Client).filter(Client.partner_id == p.id).all()
            total_real_agents = 0
            
            print(f"  - Clients: {len(clients)}")
            for c in clients:
                agent_count = db.query(Agent).filter(Agent.client_id == c.id).count()
                total_real_agents += agent_count
                print(f"    * Client: {c.name} (ID: {c.id}) -> Agents: {agent_count}")
                
            assigned_calc = total_real_agents
            available_calc = max(0, p.agent_limit - assigned_calc)
            
            print(f"  -> CALCULO FINAL:")
            print(f"     Assigned (Real DB): {assigned_calc}")
            print(f"     Available (Real DB): {available_calc}")
            
            # Check if this matches typical known state (13 assigned)
            if assigned_calc == 0:
                print("     [!] ALERT: 0 Agents assigned. UI showing 'Limit' (e.g. 20) is CORRECT behavior if DB is empty.")
            elif assigned_calc == 13:
                 print("     [+] MATCH: DB matches the expected '13 assigned' scenario.")
            else:
                 print(f"     [?] INFO: DB has {assigned_calc} agents. UI should show {available_calc}.")
                 
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_partner_agents()
