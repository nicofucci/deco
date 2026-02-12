"""
PDF Generation Service using WeasyPrint
Converts markdown reports to professional PDF documents.
"""

from weasyprint import HTML, CSS
from pathlib import Path
import markdown
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate professional PDFs from markdown content."""
    
    def __init__(self):
        self.css_template = """
            @page {
                size: A4;
                margin: 2cm;
                @bottom-center {
                    content: "Página " counter(page) " de " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }
            }
            
            body {
                font-family: 'DejaVu Sans', Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #1e293b;
            }
            
            h1 {
                color: #0f172a;
                font-size: 24pt;
                margin-top: 20pt;
                margin-bottom: 12pt;
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 8pt;
            }
            
            h2 {
                color: #1e293b;
                font-size: 18pt;
                margin-top: 16pt;
                margin-bottom: 10pt;
                border-bottom: 1px solid #cbd5e1;
                padding-bottom: 6pt;
            }
            
            h3 {
                color: #334155;
                font-size: 14pt;
                margin-top: 12pt;
                margin-bottom: 8pt;
            }
            
            p {
                margin-bottom: 10pt;
                text-align: justify;
            }
            
            ul, ol {
                margin-bottom: 10pt;
                padding-left: 20pt;
            }
            
            li {
                margin-bottom: 4pt;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 12pt 0;
            }
            
            th {
                background-color: #f1f5f9;
                color: #0f172a;
                font-weight: bold;
                padding: 8pt;
                border: 1pt solid #cbd5e1;
                text-align: left;
            }
            
            td {
                padding: 8pt;
                border: 1pt solid #e2e8f0;
            }
            
            tr:nth-child(even) {
                background-color: #f8fafc;
            }
            
            code {
                background-color: #f1f5f9;
                padding: 2pt 4pt;
                border-radius: 3pt;
                font-family: 'DejaVu Sans Mono', monospace;
                font-size: 10pt;
            }
            
            pre {
                background-color: #1e293b;
                color: #e2e8f0;
                padding: 12pt;
                border-radius: 6pt;
                overflow-x: auto;
                margin: 12pt 0;
            }
            
            pre code {
                background-color: transparent;
                color: inherit;
                padding: 0;
            }
            
            strong {
                color: #0f172a;
                font-weight: bold;
            }
            
            hr {
                border: none;
                border-top: 1pt solid #cbd5e1;
                margin: 16pt 0;
            }
            
            .cover-page {
                text-align: center;
                padding-top: 100pt;
            }
            
            .cover-title {
                font-size: 32pt;
                color: #0f172a;
                margin-bottom: 20pt;
            }
            
            .cover-subtitle {
                font-size: 16pt;
                color: #64748b;
                margin-bottom: 40pt;
            }
            
            .metadata {
                background-color: #f8fafc;
                padding: 12pt;
                border-left: 3pt solid #3b82f6;
                margin: 12pt 0;
            }
        """
    
    def markdown_to_html(self, markdown_content: str, metadata: dict = None) -> str:
        """Convert markdown to HTML with metadata header."""
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        
        # Build metadata section
        metadata_html = ""
        if metadata:
            metadata_html = f"""
            <div class="metadata">
                <p><strong>Acción:</strong> {metadata.get('action_name', 'N/A')}</p>
                <p><strong>Objetivo:</strong> {metadata.get('target', 'N/A')}</p>
                <p><strong>Fecha:</strong> {metadata.get('timestamp', 'N/A')}</p>
                <p><strong>Estado:</strong> {metadata.get('status', 'N/A')}</p>
            </div>
            """
        
        # Complete HTML document
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reporte de Seguridad</title>
        </head>
        <body>
            {metadata_html}
            {html_content}
        </body>
        </html>
        """
        
        return html_doc
    
    def generate_pdf(
        self,
        markdown_content: str,
        output_path: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Generate a PDF from markdown content.
        
        Args:
            markdown_content: The markdown text to convert
            output_path: Where to save the PDF
            metadata: Optional metadata to include in header
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert markdown to HTML
            html_content = self.markdown_to_html(markdown_content, metadata)
            
            # Create PDF
            html = HTML(string=html_content)
            css = CSS(string=self.css_template)
            
            html.write_pdf(output_path, stylesheets=[css])
            
            logger.info(f"PDF generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False
