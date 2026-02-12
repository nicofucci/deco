"""
JARVIS Continuous Learning Engine (CLE)
Configuration and Constants
"""

from typing import List, Dict
from datetime import timedelta

# ============================================================================
# ETHICAL BOUNDARIES
# ============================================================================

# Allowed domains for web crawling (whitelist)
ALLOWED_DOMAINS = [
    # Government & Standards
    "owasp.org",
    "nist.gov",
    "cisa.gov",
    "nvd.nist.gov",
    "cve.mitre.org",
    
    # Security Vendors & Platforms
    "portswigger.net",
    "offensive-security.com",
    "kali.org",
    "metasploit.com",
    
    # Education & Training
    "tryhackme.com",
    "hackthebox.com",
    "pentesterlab.com",
    "cybrary.it",
    
    # Technical Documentation
    "docs.kali.org",
    "www.kali.org",
    "help.offensive-security.com",
    
    # Security Research
    "arxiv.org",
    "reddit.com/r/netsec",
    "reddit.com/r/cybersecurity",
]

# Blocked keywords (auto-reject content containing these)
BLOCKED_KEYWORDS = [
    "dark web", "darknet", "tor marketplace",
    "0day for sale", "exploit kit sale",
    "ransomware as a service", "credential dump",
    "illegal access", "hack into", "steal data",
]

# GitHub topics to search
GITHUB_TOPICS = [
    "penetration-testing",
    "security-tools",
    "vulnerability-scanner",
    "network-security",
    "web-security",
    "osint",
    "red-team",
    "blue-team",
    "security-hardening",
]

# YouTube channels (educational only)
YOUTUBE_CHANNELS = {
    "NetworkChuck": "UC9x0AN7BWHpCDHSm9NiJFJQ",
    "TheCyberMentor": "UC0ArlFuFYMpEewyRBzdLHiw",
    "IPPSec": "UCa6eh7gCkpPo5XXUDfygQQA",
    "John Hammond": "UCVeW9qkBjo3zosnqUbG7CFw",
    "LiveOverflow": "UClcE-kVhqyiHCcjYwcpfj9w",
}

# ============================================================================
# QDRANT COLLECTIONS
# ============================================================================

CLE_COLLECTIONS = {
    "cle_articles": {
        "description": "Web articles and documentation",
        "vector_size": 4096,  # Llama 3.1 embeddings
    },
    "cle_github": {
        "description": "GitHub repositories and tools",
        "vector_size": 4096,
    },
    "cle_youtube": {
        "description": "YouTube video transcriptions",
        "vector_size": 4096,
    },
}

# ============================================================================
# LEARNING CYCLE
# ============================================================================

# How often to run learning cycle
LEARNING_CYCLE_INTERVAL = timedelta(hours=12)

# Max items to process per cycle
MAX_WEB_ARTICLES_PER_CYCLE = 20
MAX_GITHUB_REPOS_PER_CYCLE = 10
MAX_YOUTUBE_VIDEOS_PER_CYCLE = 5

# ============================================================================
# PATHS
# ============================================================================

REPORTS_DIR = "/opt/deco/agent_runtime/docs/learning/reports"
PROPOSALS_DIR = "/opt/deco/agent_runtime/docs/learning/proposals"

# ============================================================================
# LLM PROMPTS
# ============================================================================

SUMMARIZATION_PROMPT = """Eres un experto en ciberseguridad analizando contenido técnico para un sistema de aprendizaje de IA.

**Contenido a analizar:**
{content}

**Tu tarea:**
1. Proporciona un resumen conciso (2-3 frases) de qué trata este contenido
2. Extrae 5-10 conceptos técnicos o técnicas clave mencionadas
3. Identifica 2-3 casos de uso potenciales para Jarvis (nuestro agente de hacking ético)

**Formatea tu respuesta como JSON:**
{{
    "summary": "...",
    "concepts": ["concepto1", "concepto2", ...],
    "jarvis_use_cases": ["caso de uso 1", "caso de uso 2", ...]
}}

**Importante:** Solo enfócate en técnicas éticas, legales y apropiadas para laboratorios. Ignora cualquier contenido ilegal o no ético."""

GAP_ANALYSIS_PROMPT = """
Eres un experto en ciberseguridad y pentesting analizando nuevo conocimiento para JARVIS.

CONTEXTO DE JARVIS:
- Sistema autónomo de pentesting y ethical hacking
- Ejecuta escaneos de red, análisis de vulnerabilidades, fuzzing
- Genera reportes técnicos automáticos
- Utiliza herramientas como Nmap, Metasploit, SQLMap, Nikto
- Enfoque 100% ético y legal (labs, CTFs, entornos autorizados)

NUEVO CONOCIMIENTO ADQUIRIDO:
{knowledge_summary}

TAREA:
Identifica gaps (brechas) o mejoras potenciales en las capacidades de JARVIS basándote en este nuevo conocimiento.

RESPONDE EN FORMATO JSON:
{{
  "gaps": [
    {{
      "title": "Título descriptivo de la mejora (en español)",
      "description": "Descripción detallada de qué falta o se puede mejorar (en español)",
      "type": "new_action|enhancement|integration|optimization",
      "impact": "high|medium|low",
      "effort": "high|medium|low",
      "learned_from": "Fuente del conocimiento que sugiere esta mejora"
    }}
  ]
}}

IMPORTANTE:
- TODAS las descripciones deben estar en ESPAÑOL
- Solo sugiere mejoras éticas y legales
- Enfócate en mejoras prácticas y realizables
- Prioriza alto impacto con bajo/medio esfuerzo
- Máximo 10 propuestas
"""

# ============================================================================
# SCORING WEIGHTS
# ============================================================================

PROPOSAL_SCORING = {
    "impact_high": 3.0,
    "impact_medium": 2.0,
    "impact_low": 1.0,
    "effort_high": 3.0,
    "effort_medium": 2.0,
    "effort_low": 1.0,
}
