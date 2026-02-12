"""
Sistema de Scoring de Riesgo
Calcula y clasifica riesgo de vulnerabilidades
"""

from typing import Dict, List
from enum import Enum

class RiskLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class RiskScorer:
    """Calculadora de riesgo de vulnerabilidades."""
    
    def __init__(self):
        self.risk_factors = {
            "cvss_score": 0.4,      # 40% peso
            "exploitability": 0.3,   # 30% peso
            "exposure": 0.2,         # 20% peso
            "impact": 0.1            # 10% peso
        }
    
    def calculate_risk(self, vulnerability: Dict) -> Dict[str, any]:
        """
        Calcula score de riesgo completo.
        
        Args:
            vulnerability: Diccionario con datos de vulnerabilidad
        
        Returns:
            Diccionario con score y clasificación
        """
        # Componentes del score
        cvss_component = self._score_cvss(vulnerability.get("cvss_score", 0))
        exploit_component = self._score_exploitability(
            vulnerability.get("exploitability", "unknown")
        )
        exposure_component = self._score_exposure(vulnerability)
        impact_component = self._score_impact(vulnerability)
        
        # Score ponderado
        total_score = (
            cvss_component * self.risk_factors["cvss_score"] +
            exploit_component * self.risk_factors["exploitability"] +
            exposure_component * self.risk_factors["exposure"] +
            impact_component * self.risk_factors["impact"]
        )
        
        # Clasificación
        risk_level = self._classify_risk(total_score)
        
        return {
            "total_score": round(total_score, 2),
            "risk_level": risk_level.value,
            "components": {
                "cvss": cvss_component,
                "exploitability": exploit_component,
                "exposure": exposure_component,
                "impact": impact_component
            },
            "recommendations": self._generate_recommendations(
                risk_level,
                vulnerability
            )
        }
    
    def _score_cvss(self, cvss: float) -> float:
        """Convierte CVSS (0-10) a score interno (0-100)."""
        return min(cvss * 10, 100)
    
    def _score_exploitability(self, exploitability: str) -> float:
        """Score de explotabilidad."""
        scores = {
            "high": 90,
            "medium": 60,
            "low": 30,
            "unknown": 50  # Asumir medio si desconocido
        }
        return scores.get(exploitability.lower(), 50)
    
    def _score_exposure(self, vulnerability: Dict) -> float:
        """Score de exposición (qué tan expuesto está el servicio)."""
        port = vulnerability.get("port", "")
        service = vulnerability.get("service", "").lower()
        
        score = 50  # Base
        
        # Puertos comunes expuestos = mayor riesgo
        high_exposure_ports = ["21", "22", "23", "80", "443", "3389", "445"]
        if str(port) in high_exposure_ports:
            score += 30
        
        # Servicios críticos
        critical_services = ["ssh", "rdp", "smb", "http", "https"]
        if any(s in service for s in critical_services):
            score += 20
        
        return min(score, 100)
    
    def _score_impact(self, vulnerability: Dict) -> float:
        """Score de impacto potencial."""
        description = vulnerability.get("description", "").lower()
        
        score = 50  # Base
        
        # Keywords de alto impacto
        if any(word in description for word in ["rce", "remote code execution", "arbitrary"]):
            score += 40
        elif any(word in description for word in ["privilege escalation", "bypass"]):
            score += 30
        elif any(word in description for word in ["dos", "denial of service"]):
            score += 20
        
        return min(score, 100)
    
    def _classify_risk(self, score: float) -> RiskLevel:
        """Clasifica riesgo según score."""
        if score >= 85:
            return RiskLevel.CRITICAL
        elif score >= 70:
            return RiskLevel.HIGH
        elif score >= 50:
            return RiskLevel.MEDIUM
        elif score >= 30:
            return RiskLevel.LOW
        else:
            return RiskLevel.INFO
    
    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        vulnerability: Dict
    ) -> List[str]:
        """Genera recomendaciones basadas en nivel de riesgo."""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.append("🔴 ACCIÓN INMEDIATA REQUERIDA")
            recommendations.append("Aislar el sistema afectado de la red")
            recommendations.append("Aplicar parche de emergencia")
            recommendations.append("Monitorear logs para detección de explotación")
        
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("🟠 PARCHEAR EN 24-48 HORAS")
            recommendations.append("Implementar controles compensatorios mientras se parchea")
            recommendations.append("Revisar logs de acceso")
        
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("🟡 PARCHEAR EN PRÓXIMA VENTANA DE MANTENIMIENTO")
            recommendations.append("Implementar monitoreo adicional")
            recommendations.append("Documentar para auditoría")
        
        else:
            recommendations.append("🟢 PARCHEAR SEGÚN CALENDARIO NORMAL")
            recommendations.append("Incluir en próximo ciclo de actualizaciones")
        
        # Recomendación específica al servicio
        service = vulnerability.get("service", "")
        if service:
            recommendations.append(f"Revisar configuración de seguridad de {service}")
        
        return recommendations


class VulnerabilityRanker:
    """Ranking y comparación de vulnerabilidades."""
    
    def __init__(self, scorer: RiskScorer):
        self.scorer = scorer
    
    def rank_vulnerabilities(
        self,
        vulnerabilities: List[Dict]
    ) -> List[Dict]:
        """Rankea vulnerabilidades por riesgo."""
        scored_vulns = []
        
        for vuln in vulnerabilities:
            risk_assessment = self.scorer.calculate_risk(vuln)
            
            scored_vuln = {
                **vuln,
                "risk_assessment": risk_assessment
            }
            scored_vulns.append(scored_vuln)
        
        # Ordenar por score total
        return sorted(
            scored_vulns,
            key=lambda v: v["risk_assessment"]["total_score"],
            reverse=True
        )
    
    def get_top_risks(
        self,
        vulnerabilities: List[Dict],
        limit: int = 10
    ) -> List[Dict]:
        """Obtiene top N vulnerabilidades más críticas."""
        ranked = self.rank_vulnerabilities(vulnerabilities)
        return ranked[:limit]
    
    def group_by_risk_level(
        self,
        vulnerabilities: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Agrupa vulnerabilidades por nivel de riesgo."""
        ranked = self.rank_vulnerabilities(vulnerabilities)
        
        grouped = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
        
        for vuln in ranked:
            level = vuln["risk_assessment"]["risk_level"]
            grouped[level].append(vuln)
        
        return grouped
