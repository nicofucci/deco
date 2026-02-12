import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.models.domain import Client, Asset, Finding
import os

def _build_markdown(client: Client, assets: List[Asset], findings: List[Finding]) -> str:
    """
    Genera un resumen en Markdown para el cliente.
    """
    lines: List[str] = []
    lines.append(f"# Informe de Seguridad - {client.name}")
    lines.append(f"_Generado: {datetime.now(timezone.utc).isoformat()}_")
    lines.append("")
    lines.append("## Resumen Ejecutivo")
    lines.append(f"- Activos analizados: {len(assets)}")
    lines.append(f"- Hallazgos detectados: {len(findings)}")
    criticos = len([f for f in findings if f.severity.lower() == "critical"])
    altos = len([f for f in findings if f.severity.lower() == "high"])
    lines.append(f"- Críticos: {criticos} | Altos: {altos}")
    lines.append("")

    lines.append("## Activos Descubiertos")
    if not assets:
        lines.append("- No se han detectado activos.")
    else:
        for asset in assets:
            lines.append(f"- {asset.ip} ({asset.hostname or 'sin hostname'})")
    lines.append("")

    lines.append("## Hallazgos Prioritarios")
    if not findings:
        lines.append("No se detectaron hallazgos en los activos analizados.")
    else:
        for f in findings:
            lines.append(f"### {f.title} ({f.severity.upper()})")
            lines.append(f"- Activo: {f.asset.ip if f.asset else 'desconocido'}")
            if f.description:
                lines.append(f"- Descripción: {f.description}")
            if f.recommendation:
                lines.append(f"- Recomendación: {f.recommendation}")
            lines.append("")

    return "\n".join(lines)


def _markdown_to_html(md: str) -> str:
    """
    Conversión simple a HTML para MVP (sin dependencias externas).
    """
    import html
    html_lines: List[str] = []
    for line in md.splitlines():
        if line.startswith("# "):
            html_lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("- "):
            html_lines.append(f"<p>• {html.escape(line[2:])}</p>")
        elif line.strip() == "":
            html_lines.append("<br/>")
        else:
            html_lines.append(f"<p>{html.escape(line)}</p>")
    return "\n".join(html_lines)


def generate_client_report(db: Session, client: Client, format: str = "markdown") -> Dict[str, Any]:
    """
    Genera un informe ligero con activos y hallazgos del cliente.
    """
    assets = (
        db.query(Asset)
        .filter(Asset.client_id == client.id)
        .order_by(Asset.created_at.desc())
        .all()
    )
    findings = (
        db.query(Finding)
        .join(Asset, Finding.asset_id == Asset.id)
        .filter(Finding.client_id == client.id)
        .order_by(Finding.detected_at.desc())
        .all()
    )

    md = _build_markdown(client, assets, findings)
    content = md if format == "markdown" else _markdown_to_html(md)

    return {
        "report_id": str(uuid.uuid4()),
        "format": "markdown" if format not in ("html", "markdown") else format,
        "content": content,
        "generated_at": datetime.now(timezone.utc),
    }


class ReportGenerator:
    """
    Implementación real de reportes PDF usando WeasyPrint y Jinja2.
    """

    def __init__(self, output_dir: str = "/tmp/reports", template_dir: str = "/opt/deco/templates/pdf"):
        self.output_dir = output_dir
        self.template_dir = template_dir
        self._ensure_dir()

    def _ensure_dir(self):
        import os
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf_report(self, client_name: str, stats: Dict[str, Any], findings: List[Dict[str, Any]], lang: str = "es", type: str = "executive") -> str:
        """
        Genera un reporte PDF real usando templates HTML.
        """
        try:
            from weasyprint import HTML
            from jinja2 import Environment, FileSystemLoader
        except ImportError:
            print("Error: WeasyPrint or Jinja2 not installed. Falling back to dummy.")
            return self._generate_dummy_report(client_name, lang, type)

        # Setup Jinja2
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template_name = f"template_report_{lang}.html"
        
        try:
            template = env.get_template(template_name)
        except Exception:
            print(f"Template {template_name} not found, falling back to ES")
            template = env.get_template("template_report_es.html")

        # Render HTML
        html_content = template.render(
            client_name=client_name,
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            stats=stats,
            findings=findings
        )

        # Generate PDF filename
        filename = f"report_{client_name.replace(' ', '_')}_{type}_{lang}_{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Convert to PDF
        HTML(string=html_content).write_pdf(filepath)
        
        return filename

    def _generate_dummy_report(self, client_name: str, lang: str, type: str) -> str:
        # Fallback for when libraries are missing (should not happen in prod)
        filename = f"dummy_{client_name}_{type}_{lang}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w") as f:
            f.write(f"Dummy PDF for {client_name}")
        return filename

    # Legacy methods kept for compatibility if needed, but redirected to new logic or deprecated
    def generate_executive_report(self, client_name: str, stats: Dict[str, Any]) -> str:
        return self.generate_pdf_report(client_name, stats, [], lang="es", type="executive")

    def generate_technical_report(self, client_name: str, findings: List[Dict[str, Any]]) -> str:
        return self.generate_pdf_report(client_name, {}, findings, lang="es", type="technical")
