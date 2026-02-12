import asyncio
import logging
import os
from datetime import datetime, timezone
from app.database import SessionLocal
from app.risk.risk_service import RiskService
from app.models.alerts import Alert
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logging.getLogger(__name__).warning("ReportLab not found. PDF reports will be disabled.")

logger = logging.getLogger(__name__)

REPORT_DIR = "/opt/deco/reports/daily"

async def start_continuous_audit_watcher():
    """
    Generates Daily Audit Reports (PDF).
    Runs every 6 hours.
    """
    logger.info("Starting Continuous Audit Watcher...")
    
    # Ensure directory exists
    os.makedirs(REPORT_DIR, exist_ok=True)

    while True:
        try:
            await generate_audit_report()
        except Exception as e:
            logger.error(f"Error in Continuous Audit Watcher: {e}")
        
        await asyncio.sleep(21600) # 6 hours

async def generate_audit_report():
    db = SessionLocal()
    try:
        timestamp = datetime.now(timezone.utc)
        filename = f"audit_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(REPORT_DIR, filename)

        # Gather Data
        risk_service = RiskService(db)
        global_risk = risk_service.get_risk_score('global', 'global')
        risk_score = global_risk.score if global_risk else 0.0
        
        critical_alerts = db.query(Alert).filter(
            Alert.severity == "critical",
            Alert.status == "open"
        ).count()
        
        total_alerts = db.query(Alert).filter(Alert.status == "open").count()

        # Generate Report
        if HAS_REPORTLAB:
            # Generate PDF
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter

            # Header
            c.setFont("Helvetica-Bold", 24)
            c.drawString(50, height - 50, "Deco-Gravity Daily Audit Report")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # Risk Section
            c.setStrokeColor(colors.black)
            c.line(50, height - 100, width - 50, height - 100)
            
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 130, "Global Risk Assessment")
            
            c.setFont("Helvetica", 14)
            c.drawString(50, height - 160, f"Risk Score: {risk_score:.2f} / 100")
            c.drawString(50, height - 180, f"Risk Level: {global_risk.level.upper() if global_risk else 'UNKNOWN'}")
            
            # Alerts Section
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 220, "Active Alerts")
            
            c.setFont("Helvetica", 14)
            c.drawString(50, height - 250, f"Critical Open Alerts: {critical_alerts}")
            c.drawString(50, height - 270, f"Total Open Alerts: {total_alerts}")
            
            # Footer
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(50, 50, "Generated automatically by Jarvis Continuous Audit Watcher")
            
            c.save()
            logger.info(f"Audit report generated (PDF): {filepath}")
        else:
            # Fallback to Markdown/Text
            txt_filepath = filepath.replace(".pdf", ".txt")
            with open(txt_filepath, "w") as f:
                f.write("Deco-Gravity Daily Audit Report\n")
                f.write("===============================\n")
                f.write(f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
                f.write("Global Risk Assessment\n")
                f.write("----------------------\n")
                f.write(f"Risk Score: {risk_score:.2f} / 100\n")
                f.write(f"Risk Level: {global_risk.level.upper() if global_risk else 'UNKNOWN'}\n\n")
                f.write("Active Alerts\n")
                f.write("-------------\n")
                f.write(f"Critical Open Alerts: {critical_alerts}\n")
                f.write(f"Total Open Alerts: {total_alerts}\n")
            
            logger.info(f"Audit report generated (TXT): {txt_filepath}")

    finally:
        db.close()
