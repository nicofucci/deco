"""
Sistema de Inteligencia Operacional de Jarvis
Planificación, análisis de riesgo y simulación defensiva
"""

from typing import Dict, List, Any
import json

class JarvisIntelligence:
    """Inteligencia operacional para análisis defensivo."""
    
    def __init__(self, ollama_client):
        self.ollama = ollama_client
    
    def plan_audit(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Planifica auditoría automática basada en objetivo.
        
        Returns plan con fases, tiempos estimados y recursos necesarios.
        """
        prompt = f"""Eres un analista de seguridad senior. Planifica una auditoría defensiva para:

Objetivo: {target_info.get('target', 'N/A')}
Tipo: {target_info.get('type', 'infraestructura')}
Alcance: {target_info.get('scope', 'básico')}

Genera un plan JSON con esta estructura:
{{
  "fases": [
    {{"nombre": "Reconocimiento", "duracion_estimada": "30min", "herramientas": ["nmap"], "riesgos": "bajo"}},
    {{"nombre": "Análisis de Vulnerabilidades", "duracion_estimada": "1h", "herramientas": ["nuclei"], "riesgos": "medio"}}
  ],
  "recursos_necesarios": ["VM Kali", "Conexión segura"],
  "consideraciones_eticas": ["Autorización escrita", "Solo laboratorio"],
  "entregables": ["Reporte MD", "Reporte PDF"]
}}

Responde SOLO con el JSON, sin texto adicional."""

        response = self.ollama.chat(
            messages=[{"role": "user", "content": prompt}],
            model="mistral:7b-instruct"
        )
        
        try:
            plan_text = response.get("message", {}).get("content", "{}")
            # Extraer JSON del texto
            start = plan_text.find("{")
            end = plan_text.rfind("}") + 1
            if start != -1 and end > start:
                plan = json.loads(plan_text[start:end])
            else:
                plan = self._fallback_plan()
        except:
            plan = self._fallback_plan()
        
        return plan
    
    def analyze_risk(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza riesgo real de una vulnerabilidad."""
        prompt = f"""Analiza el riesgo de esta vulnerabilidad desde perspectiva defensiva:

CVE: {vulnerability.get('cve_id', 'N/A')}
Severidad CVSS: {vulnerability.get('severity', 'N/A')}
Servicio: {vulnerability.get('service', 'N/A')}
Versión: {vulnerability.get('version', 'N/A')}

Proporciona análisis JSON:
{{
  "probabilidad_explotacion": "alta|media|baja",
  "complejidad_ataque": "baja|media|alta",
  "impacto_negocio": {{
    "confidencialidad": "alto|medio|bajo",
    "integridad": "alto|medio|bajo",
    "disponibilidad": "alto|medio|bajo"
  }},
  "vectores_ataque": ["phishing", "exploit directo"],
  "mitigaciones_prioritarias": [
    "Actualizar a versión X.Y.Z",
    "Implementar WAF"
  ],
  "tiempo_estimado_mitigacion": "inmediato|corto|medio|largo"
}}

Solo JSON, sin explicaciones."""

        response = self.ollama.chat(
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            analysis_text = response.get("message", {}).get("content", "{}")
            start = analysis_text.find("{")
            end = analysis_text.rfind("}") + 1
            analysis = json.loads(analysis_text[start:end])
        except:
            analysis = self._fallback_risk_analysis()
        
        return analysis
    
    def simulate_attack_chain(self, vulnerability: Dict[str, Any]) -> List[Dict]:
        """Simula cadena de ataque (kill chain) de forma defensiva."""
        prompt = f"""Como analista defensivo, simula la kill chain que un atacante seguiría para esta vulnerabilidad:

CVE: {vulnerability.get('cve_id')}
Servicio: {vulnerability.get('service')}

Genera JSON con las fases:
{{
  "kill_chain": [
    {{
      "fase": "Reconocimiento",
      "acciones_atacante": ["Escaneo de puertos", "Fingerprinting"],
      "indicadores_deteccion": ["Múltiples conexiones SYN", "User-Agent sospechoso"],
      "controles_defensivos": ["IDS", "Rate limiting"]
    }},
    {{
      "fase": "Explotación",
      "acciones_atacante": ["Envío de payload"],
      "indicadores_deteccion": ["Patrón de ataque conocido"],
      "controles_defensivos": ["WAF", "Patch management"]
    }}
  ]
}}

Solo JSON."""

        response = self.ollama.chat(
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            chain_text = response.get("message", {}).get("content", "{}")
            start = chain_text.find("{")
            end = chain_text.rfind("}") + 1
            chain = json.loads(chain_text[start:end])
            return chain.get("kill_chain", [])
        except:
            return self._fallback_kill_chain()
    
    def recommend_mitigations(
        self,
        vulnerabilities: List[Dict],
        context: Dict[str, Any]
    ) -> List[Dict]:
        """Genera recomendaciones de mitigación prioritarias."""
        # Ordenar por severidad
        vulnerabilities_sorted = sorted(
            vulnerabilities,
            key=lambda v: self._severity_score(v.get("severity", "Low")),
            reverse=True
        )
        
        recommendations = []
        
        for vuln in vulnerabilities_sorted[:5]:  # Top 5
            rec = {
                "cve_id": vuln.get("cve_id"),
                "prioridad": "crítica" if vuln.get("severity") == "Critical" else "alta",
                "acciones": [
                    f"Actualizar {vuln.get('service')} inmediatamente",
                    "Implementar controles compensatorios mientras se parchea",
                    "Monitorear logs para detección de explotación"
                ],
                "recursos_necesarios": ["Ventana de mantenimiento", "Testing previo"],
                "tiempo_estimado": "24-48 horas"
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _severity_score(self, severity: str) -> int:
        """Convierte severidad a score numérico."""
        scores = {
            "Critical": 5,
            "High": 4,
            "Medium": 3,
            "Low": 2,
            "Info": 1
        }
        return scores.get(severity, 0)
    
    def _fallback_plan(self) -> Dict:
        """Plan de fallback si LLM falla."""
        return {
            "fases": [
                {"nombre": "Reconocimiento", "duracion_estimada": "30min"},
                {"nombre": "Análisis", "duracion_estimada": "1h"},
                {"nombre": "Reporte", "duracion_estimada": "30min"}
            ],
            "recursos_necesarios": ["VM Kali"],
            "consideraciones_eticas": ["Solo laboratorio autorizado"],
            "entregables": ["Reporte PDF"]
        }
    
    def _fallback_risk_analysis(self) -> Dict:
        """Análisis de riesgo de fallback."""
        return {
            "probabilidad_explotacion": "media",
            "complejidad_ataque": "media",
            "impacto_negocio": {
                "confidencialidad": "medio",
                "integridad": "medio",
                "disponibilidad": "medio"
            },
            "vectores_ataque": ["Requiere análisis manual"],
            "mitigaciones_prioritarias": ["Parchear sistema"],
            "tiempo_estimado_mitigacion": "corto"
        }
    
    def _fallback_kill_chain(self) -> List[Dict]:
        """Kill chain de fallback."""
        return [
            {
                "fase": "Reconocimiento",
                "acciones_atacante": ["Escaneo"],
                "indicadores_deteccion": ["Logs de firewall"],
                "controles_defensivos": ["IDS"]
            },
            {
                "fase": "Explotación",
                "acciones_atacante": ["Exploit"],
                "indicadores_deteccion": ["Anomalías"],
                "controles_defensivos": ["Patching"]
            }
        ]
