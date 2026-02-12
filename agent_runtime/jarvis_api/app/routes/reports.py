from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
from pathlib import Path

router = APIRouter()
REPORTS_BASE_PATH = "/opt/deco/reports"


def _find_report_dir(report_id: str) -> Optional[Path]:
    base_path = Path(REPORTS_BASE_PATH)
    for path in base_path.glob(f"*/*/{report_id}"):
        if path.is_dir():
            return path
    return None

@router.get("/")
async def list_reports(action_id: str = None):
    """Lista todos los reportes disponibles, opcionalmente filtrados por action_id."""
    reports = []
    
    # Recorrer estructura: reports/{tenant}/{action_id}/{timestamp_execid}/metadata.json
    base_path = Path(REPORTS_BASE_PATH)
    
    if not base_path.exists():
        return []
        
    try:
        # Buscar en todos los tenants - patrón: {tenant}/{action_id}/{timestamp}/metadata.json
        search_pattern = f"*/{action_id}/*/metadata.json" if action_id else "*/*/*/metadata.json"
        
        # Buscar recursivamente archivos metadata.json
        for metadata_file in base_path.glob(search_pattern):
            try:
                with open(metadata_file, "r") as f:
                    data = json.load(f)
                    
                # El ID del reporte es el nombre de la carpeta padre (timestamp_execid)
                report_id = metadata_file.parent.name
                # El action_id es el nombre de la carpeta abuela
                current_action_id = metadata_file.parent.parent.name
                
                reports.append({
                    "id": report_id,
                    "action_id": current_action_id,
                    "action_name": data.get("action_name", "Unknown"),
                    "target": data.get("target", "Unknown"),
                    "timestamp": data.get("timestamp", ""),
                    "status": data.get("status", "unknown")
                })
            except Exception as e:
                print(f"Error reading metadata {metadata_file}: {e}")
                continue
                
        # Ordenar por fecha descendente
        reports.sort(key=lambda x: x["timestamp"], reverse=True)
        return reports
        
    except Exception as e:
        print(f"Error listing reports: {e}")
        return []

@router.get("/{report_id}")
async def get_report(report_id: str):
    """Obtiene el contenido de un reporte específico."""
    found_path = _find_report_dir(report_id)

    if not found_path:
        raise HTTPException(status_code=404, detail=f"Reporte no encontrado: {report_id}")
        
    try:
        # Leer report_ai.md
        report_file = found_path / "report_ai.md"
        if not report_file.exists():
            raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado")
            
        with open(report_file, "r") as f:
            content = f.read()
            
        # Leer metadata
        metadata = {}
        meta_file = found_path / "metadata.json"
        if meta_file.exists():
            with open(meta_file, "r") as f:
                metadata = json.load(f)
                
        return {
            "id": report_id,
            "metadata": metadata,
            "content": content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}/metadata")
async def get_report_metadata(report_id: str):
    """Devuelve el metadata.json completo del reporte."""
    found_path = _find_report_dir(report_id)
    if not found_path:
        raise HTTPException(status_code=404, detail=f"Reporte no encontrado: {report_id}")

    meta_file = found_path / "metadata.json"
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail="metadata.json no encontrado")

    try:
        with open(meta_file, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}/artifact")
async def get_report_artifact(report_id: str, name: str):
    """Devuelve artefactos de texto (ej: scan_results.txt, report_ai.md)."""
    allowed = {"scan_results.txt", "scan_raw.xml", "report_ai.md", "metadata.json"}
    if name not in allowed:
        raise HTTPException(status_code=400, detail="Artifact no permitido")

    found_path = _find_report_dir(report_id)
    if not found_path:
        raise HTTPException(status_code=404, detail=f"Reporte no encontrado: {report_id}")

    file_path = found_path / name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró el artefacto solicitado: {name}")

    try:
        with open(file_path, "r") as f:
            content = f.read()
    except UnicodeDecodeError:
        content = file_path.read_bytes().decode(errors="ignore")

    return {"name": name, "content": content}


@router.get("/{report_id}/pdf")
async def export_report_pdf(report_id: str):
    """Genera y descarga un PDF profesional del reporte."""
    from fastapi.responses import FileResponse
    from app.services.pdf_generator import PDFGenerator
    import tempfile
    
    base_path = Path(REPORTS_BASE_PATH)
    
    # Buscar la carpeta del reporte
    found_path = None
    for path in base_path.glob(f"*/*/{report_id}"):
        if path.is_dir():
            found_path = path
            break
            
    if not found_path:
        raise HTTPException(status_code=404, detail=f"Reporte no encontrado: {report_id}")
        
    try:
        # Leer report_ai.md
        report_file = found_path / "report_ai.md"
        if not report_file.exists():
            raise HTTPException(status_code=404, detail="Archivo de reporte no encontrado")
            
        with open(report_file, "r") as f:
            markdown_content = f.read()
            
        # Leer metadata
        metadata = {}
        meta_file = found_path / "metadata.json"
        if meta_file.exists():
            with open(meta_file, "r") as f:
                metadata = json.load(f)
        
        # Generar PDF
        pdf_gen = PDFGenerator()
        
        # Crear archivo temporal para el PDF
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp_pdf:
            pdf_path = tmp_pdf.name
        
        success = pdf_gen.generate_pdf(
            markdown_content=markdown_content,
            output_path=pdf_path,
            metadata=metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Error generando PDF")
        
        # Nombre del archivo para descarga
        filename = f"reporte_{metadata.get('action_name', 'security')}_{report_id[:8]}.pdf"
        
        # Asegurar que el archivo existe y se puede leer
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="PDF file not created")
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"PDF Generation Error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")

@router.get("/audits/list")
async def list_audit_reports():
    """Lista los reportes de auditoría diaria."""
    audit_dir = Path("/opt/deco/reports/daily")
    if not audit_dir.exists():
        return []
    
    reports = []
    for f in audit_dir.glob("*.pdf"):
        reports.append({
            "filename": f.name,
            "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "size": f.stat().st_size
        })
    
    reports.sort(key=lambda x: x["created_at"], reverse=True)
    return reports

@router.get("/audits/download/{filename}")
async def download_audit_report(filename: str):
    """Descarga un reporte de auditoría."""
    from fastapi.responses import FileResponse
    audit_dir = Path("/opt/deco/reports/daily")
    file_path = audit_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
